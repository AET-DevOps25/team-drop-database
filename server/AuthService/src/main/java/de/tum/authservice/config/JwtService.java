package de.tum.authservice.config;

import de.tum.authservice.user.Permission;
import de.tum.authservice.user.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyFactory;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.*;
import java.util.function.Function;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

@Service
public class JwtService {

    @Value("${application.security.jwt.expiration}")
    private long jwtExpiration;
    @Value("${application.security.jwt.refresh-token.expiration}")
    private long refreshExpiration;
    @Value("${application.security.jwt.private-key-path}")
    private String privateKeyPath;
    @Value("${application.security.jwt.public-key-path}")
    private String publicKeyPath;

    private RSAPrivateKey privateKey;
    private RSAPublicKey publicKey;

    private final Counter tokenGenCounter;
    private final Counter refreshGenCounter;
    private final Counter validationSuccessCounter;
    private final Counter validationFailureCounter;
    private final Counter keyLoadErrorCounter;
    private final Timer tokenGenTimer;
    private final Timer validationTimer;

    public JwtService(MeterRegistry registry) {
        this.tokenGenCounter = Counter
                .builder("authentication_service_jwt_tokens_generated_total")
                .description("Number of JWTs issued")
                .register(registry);
        this.refreshGenCounter = Counter
                .builder("authentication_service_jwt_refresh_tokens_generated_total")
                .description("Number of refresh tokens issued")
                .register(registry);
        this.validationSuccessCounter = Counter
                .builder("authentication_service_jwt_validation_success_total")
                .description("Number of successful token validations")
                .register(registry);
        this.validationFailureCounter = Counter
                .builder("authentication_service_jwt_validation_failure_total")
                .description("Number of failed token validations")
                .register(registry);
        this.keyLoadErrorCounter = Counter
                .builder("authentication_service_jwt_key_load_errors_total")
                .description("Number of failures loading RSA keys")
                .register(registry);

        this.tokenGenTimer = Timer
                .builder("authentication_service_jwt_token_generation_duration_seconds")
                .description("Time to generate JWTs")
                .publishPercentileHistogram()
                .register(registry);
        this.validationTimer = Timer
                .builder("authentication_service_jwt_token_validation_duration_seconds")
                .description("Time to validate JWTs")
                .publishPercentileHistogram()
                .register(registry);
    }

    @PostConstruct
    private void initKeys() {
        try {
            this.privateKey = loadPrivateKey();
            this.publicKey = loadPublicKey();
        } catch (Exception e) {
            keyLoadErrorCounter.increment();
            throw (RuntimeException) e;
        }
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    public String generateToken(UserDetails userDetails) {
        return tokenGenTimer.record(() -> {
            if (!(userDetails instanceof User user)) {
                throw new IllegalArgumentException("userDetails must be User");
            }
            tokenGenCounter.increment();
            Map<String, Object> extraClaims = new HashMap<>();
            extraClaims.put("roles", List.of(user.getRole().name()));
            extraClaims.put("permissions", user.getRole().getPermissions()
                    .stream()
                    .map(p -> p.getPermission())
                    .toList());
            return buildToken(extraClaims, userDetails, jwtExpiration);
        });

//        if (!(userDetails instanceof User user)) {
//            throw new IllegalArgumentException("userDetails must be instance of User");
//        }
//
//        var extraClaims = new HashMap<String, Object>();
//        extraClaims.put("roles", List.of(user.getRole().name()));
//        List<String> permissions = user.getRole().getPermissions()
//                .stream()
//                .map(Permission::getPermission)
//                .toList();
//        extraClaims.put("permissions", permissions);
//        return generateToken(extraClaims, userDetails);
    }

//    public String generateToken(
//            Map<String, Object> extraClaims,
//            UserDetails userDetails
//    ) {
//        return buildToken(extraClaims, userDetails, jwtExpiration);
//    }

    public String generateRefreshToken(
            UserDetails userDetails
    ) {
        return tokenGenTimer.record(() -> {
            refreshGenCounter.increment();
            return buildToken(new HashMap<>(), userDetails, refreshExpiration);
        });
//        return buildToken(new HashMap<>(), userDetails, refreshExpiration);
    }

    private String buildToken(
            Map<String, Object> extraClaims,
            UserDetails userDetails,
            long expiration
    ) {
        return Jwts
                .builder()
                .setClaims(extraClaims)
                .setSubject(userDetails.getUsername())
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(privateKey, SignatureAlgorithm.RS256)
                .compact();
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        return validationTimer.record(() -> {
            boolean valid = false;
            try {
                String username = extractUsername(token);
                valid = username.equals(userDetails.getUsername()) && !isTokenExpired(token);
            } catch (Exception e) {
                validationFailureCounter.increment();
                return false;
            }
            if (valid) validationSuccessCounter.increment();
            else    validationFailureCounter.increment();
            return valid;
        });
//        final String username = extractUsername(token);
//        return (username.equals(userDetails.getUsername())) && !isTokenExpired(token);
    }

    private boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    private Claims extractAllClaims(String token) {
        return Jwts
                .parserBuilder()
                .setSigningKey(publicKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
    }


    public RSAPrivateKey loadPrivateKey() {
        try {
            String key = readKeyFromFileOrClasspath(privateKeyPath)
                    .replace("-----BEGIN PRIVATE KEY-----", "")
                    .replace("-----END PRIVATE KEY-----", "")
                    .replaceAll("\\s+", "");

            byte[] decoded = Base64.getDecoder().decode(key);
            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(decoded);
            return (RSAPrivateKey) KeyFactory.getInstance("RSA").generatePrivate(keySpec);

        } catch (Exception e) {
            throw new RuntimeException("Failed to load RSA private key from: " + privateKeyPath, e);
        }
    }

    public RSAPublicKey loadPublicKey() {
        try {
            String key = readKeyFromFileOrClasspath(publicKeyPath)
                    .replace("-----BEGIN PUBLIC KEY-----", "")
                    .replace("-----END PUBLIC KEY-----", "")
                    .replaceAll("\\s+", "");

            byte[] decoded = Base64.getDecoder().decode(key);
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(decoded);
            return (RSAPublicKey) KeyFactory.getInstance("RSA").generatePublic(keySpec);

        } catch (Exception e) {
            throw new RuntimeException("Failed to load RSA public key from: " + publicKeyPath, e);
        }
    }

    private String readKeyFromFileOrClasspath(String path) throws Exception {
        if (path == null || path.isBlank()) {
            throw new IllegalArgumentException("Key path must not be null or empty.");
        }

        Path filePath = Paths.get(path);
        if (Files.exists(filePath)) {
            return Files.readString(filePath, StandardCharsets.UTF_8);
        }

        // Only try classpath resource if it's a relative path, not absolute
        if (!path.startsWith("/")) {
            Resource resource = new ClassPathResource(path);
            try (InputStream inputStream = resource.getInputStream()) {
                return new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
            }
        }

        throw new FileNotFoundException("Key file not found at path: " + path);
    }
}
