package de.tum.authservice.auth;

import de.tum.authservice.config.JwtService;
import de.tum.authservice.token.Token;
import de.tum.authservice.token.TokenRepository;
import de.tum.authservice.token.TokenType;
import de.tum.authservice.user.User;
import de.tum.authservice.user.UserRepository;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.io.IOException;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;

@Service
public class AuthenticationService {
    private final UserRepository repository;
    private final TokenRepository tokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    private final Counter registerCounter;
    private final Counter authCounter;
    private final Counter authFailureCounter;
    private final Counter refreshCounter;
    private final Counter refreshFailureCounter;

    private final Timer registerTimer;
    private final Timer authTimer;
    private final Timer refreshTimer;

    public AuthenticationService(UserRepository repository,
                                 TokenRepository tokenRepository,
                                 PasswordEncoder passwordEncoder,
                                 JwtService jwtService,
                                 AuthenticationManager authenticationManager,
                                 MeterRegistry registry) {
        this.repository = repository;
        this.tokenRepository = tokenRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.authenticationManager = authenticationManager;

        this.registerCounter = Counter
                .builder("authentication_service_register_total")
                .description("Number of register calls")
                .register(registry);
        this.authCounter = Counter
                .builder("authentication_service_authenticate_total")
                .description("Number of authenticate calls")
                .register(registry);
        this.authFailureCounter = Counter
                .builder("authentication_service_authenticate_failure_total")
                .description("Number of failed authenticate calls")
                .register(registry);
        this.refreshCounter = Counter
                .builder("authentication_service_refresh_total")
                .description("Number of refreshToken calls")
                .register(registry);
        this.refreshFailureCounter = Counter
                .builder("authentication_service_refresh_failure_total")
                .description("Number of failed refreshToken calls")
                .register(registry);

        this.registerTimer = Timer
                .builder("authentication_service_register_duration_seconds")
                .description("Time to register the user")
                .publishPercentileHistogram()
                .register(registry);
        this.authTimer = Timer
                .builder("authentication_service_authenticate_duration_seconds")
                .description("Time to authenticate the user")
                .publishPercentileHistogram()
                .register(registry);
        this.refreshTimer = Timer.builder("authentication_service_refresh_duration_seconds")
                .description("Time to refresh the token")
                .publishPercentileHistogram()
                .register(registry);
    }

    public AuthenticationResponse register(RegisterRequest request) {
        registerCounter.increment();
        return registerTimer.record(() -> {
            var user = User.builder()
                    .email(request.getEmail())
                    .password(passwordEncoder.encode(request.getPassword()))
                    .role(request.getRole())
                    .build();
            var savedUser = repository.save(user);
            var jwtToken = jwtService.generateToken(user);
            var refreshToken = jwtService.generateRefreshToken(user);
            return AuthenticationResponse.builder()
                    .accessToken(jwtToken)
                    .refreshToken(refreshToken)
                    .build();
        });
//        var user = User.builder()
//                .email(request.getEmail())
//                .password(passwordEncoder.encode(request.getPassword()))
//                .role(request.getRole())
//                .build();
//        var savedUser = repository.save(user);
//        var jwtToken = jwtService.generateToken(user);
//        var refreshToken = jwtService.generateRefreshToken(user);
////        saveUserToken(savedUser, jwtToken);
//        return AuthenticationResponse.builder()
//                .accessToken(jwtToken)
//                .refreshToken(refreshToken)
//                .build();
    }

    public AuthenticationResponse authenticate(AuthenticationRequest request) {
        authCounter.increment();
        return authTimer.record(() -> {
            try {
                authenticationManager.authenticate(
                        new UsernamePasswordAuthenticationToken(
                                request.getEmail(),
                                request.getPassword()
                        )
                );
            } catch (Exception e) {
                authFailureCounter.increment();
                throw e;
            }
            var user = repository.findByEmail(request.getEmail())
                    .orElseThrow();
            var jwtToken = jwtService.generateToken(user);
            var refreshToken = jwtService.generateRefreshToken(user);
            return AuthenticationResponse.builder()
                    .accessToken(jwtToken)
                    .refreshToken(refreshToken)
                    .build();
        });

//        authenticationManager.authenticate(
//                new UsernamePasswordAuthenticationToken(
//                        request.getEmail(),
//                        request.getPassword()
//                )
//        );
//        var user = repository.findByEmail(request.getEmail())
//                .orElseThrow();
//        var jwtToken = jwtService.generateToken(user);
//        var refreshToken = jwtService.generateRefreshToken(user);
////        revokeAllUserTokens(user);
////        saveUserToken(user, jwtToken);
//        return AuthenticationResponse.builder()
//                .accessToken(jwtToken)
//                .refreshToken(refreshToken)
//                .build();
    }

    private void saveUserToken(User user, String jwtToken) {
        var token = Token.builder()
                .user(user)
                .token(jwtToken)
                .tokenType(TokenType.BEARER)
                .expired(false)
                .revoked(false)
                .build();
        tokenRepository.save(token);
    }

    private void revokeAllUserTokens(User user) {
        var validUserTokens = tokenRepository.findAllValidTokenByUser(user.getId());
        if (validUserTokens.isEmpty())
            return;
        validUserTokens.forEach(token -> {
            token.setExpired(true);
            token.setRevoked(true);
        });
        tokenRepository.saveAll(validUserTokens);
    }

    public void refreshToken(
            HttpServletRequest request,
            HttpServletResponse response
    ) throws IOException {
        refreshCounter.increment();
        refreshTimer.record(() -> {
            final String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                refreshFailureCounter.increment();
                return null;
            }
            String refreshToken = authHeader.substring(7);
            String userEmail = jwtService.extractUsername(refreshToken);
            if (userEmail == null) {
                refreshFailureCounter.increment();
                return null;
            }
            var user = repository.findByEmail(userEmail)
                    .orElseThrow();
            if (!jwtService.isTokenValid(refreshToken, user)) {
                refreshFailureCounter.increment();
                return null;
            }

            var accessToken = jwtService.generateToken(user);
            var authResponse = AuthenticationResponse.builder()
                    .accessToken(accessToken)
                    .refreshToken(refreshToken)
                    .build();
            try {
                new ObjectMapper().writeValue(response.getOutputStream(), authResponse);
            } catch (IOException e) {
                refreshFailureCounter.increment();
                throw new RuntimeException(e);
            }
            return null;
        });

//        final String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
//        final String refreshToken;
//        final String userEmail;
//        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
//            return;
//        }
//        refreshToken = authHeader.substring(7);
//        userEmail = jwtService.extractUsername(refreshToken);
//        if (userEmail != null) {
//            var user = this.repository.findByEmail(userEmail)
//                    .orElseThrow();
//            if (jwtService.isTokenValid(refreshToken, user)) {
//                var accessToken = jwtService.generateToken(user);
////                revokeAllUserTokens(user);
////                saveUserToken(user, accessToken);
//                var authResponse = AuthenticationResponse.builder()
//                        .accessToken(accessToken)
//                        .refreshToken(refreshToken)
//                        .build();
//                new ObjectMapper().writeValue(response.getOutputStream(), authResponse);
//            }
//        }
    }
}
