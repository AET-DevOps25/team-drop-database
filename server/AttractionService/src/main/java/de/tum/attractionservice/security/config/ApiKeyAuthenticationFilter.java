package de.tum.attractionservice.security.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class ApiKeyAuthenticationFilter extends OncePerRequestFilter {

    @Value("${application.security.api-key}")
    private String validApiKey;

    // the header to look in; choose whatever you like
    private static final String HEADER = "X-API-KEY";

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {
        String apiKey = request.getHeader(HEADER);

        if (apiKey != null && apiKey.equals(validApiKey)) {
            // create an Authentication and put it into SecurityContext
            Authentication auth = new UsernamePasswordAuthenticationToken(
                    "apiKeyUser",      // a placeholder principal
                    null,
                    List.of(new SimpleGrantedAuthority("ROLE_API"))  // give it a role
            );
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        // else: leave SecurityContext empty → later rules will reject if needed
        filterChain.doFilter(request, response);
    }
}
