package de.tum.authservice.config;

import de.tum.authservice.token.TokenRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.logout.LogoutHandler;
import org.springframework.stereotype.Service;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;

@Service
public class LogoutService implements LogoutHandler {

    private final TokenRepository tokenRepository;
    private final Counter logoutCounter;
    private final Counter successCounter;

    public LogoutService(TokenRepository tokenRepository, MeterRegistry registry) {
        this.tokenRepository = tokenRepository;

        this.logoutCounter = Counter
                .builder("authentication_service_logout_total")
                .description("Total number of logout attempts")
                .register(registry);
        this.successCounter = Counter
                .builder("authentication_service_logout_success_total")
                .description("Total number of successful logouts")
                .register(registry);
    }


    @Override
    public void logout(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication
    ) {
        logoutCounter.increment();
        final String authHeader = request.getHeader("Authorization");
        final String jwt;
        if (authHeader == null ||!authHeader.startsWith("Bearer ")) {
            return;
        }
        jwt = authHeader.substring(7);
        var storedToken = tokenRepository.findByToken(jwt)
                .orElse(null);
        if (storedToken != null) {
            successCounter.increment();
            storedToken.setExpired(true);
            storedToken.setRevoked(true);
            tokenRepository.save(storedToken);
            SecurityContextHolder.clearContext();
        }
    }
}
