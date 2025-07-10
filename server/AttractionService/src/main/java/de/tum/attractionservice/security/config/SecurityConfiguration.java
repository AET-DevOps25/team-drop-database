package de.tum.attractionservice.security.config;

import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import static org.springframework.security.config.http.SessionCreationPolicy.STATELESS;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
@EnableMethodSecurity
public class SecurityConfiguration {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    private static final String USER = "USER";
    private static final String ADMIN = "ADMIN";
    private static final String MANAGER = "MANAGER";

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .cors(Customizer.withDefaults())
                .csrf(AbstractHttpConfigurer::disable)
                .exceptionHandling(e -> e
                        .authenticationEntryPoint((request, response, authException) -> {
                            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Unauthorized");
                        })
                )
                .authorizeHttpRequests(req ->
                        req.requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                            //  configure role-based access control
                            .requestMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                            .requestMatchers(HttpMethod.POST, "/cities").hasAnyRole(ADMIN, MANAGER)
                            .requestMatchers(HttpMethod.DELETE, "/cities/**").hasAnyRole(ADMIN, MANAGER)
                            .requestMatchers(HttpMethod.POST, "/attractions/**").hasAnyRole(ADMIN, MANAGER)
                            .requestMatchers(HttpMethod.DELETE, "/attractions/**").hasAnyRole(ADMIN, MANAGER)
                            // configure access to connection endpoints
                            .requestMatchers("/connection/ping").permitAll()
                            .requestMatchers("/connection/user-ping").hasAnyRole(USER)
                            .requestMatchers("/connection/admin-ping").hasAnyRole(ADMIN)
                            .requestMatchers("/connection/manager-ping").hasAnyRole(MANAGER)
                            // configure access to public endpoints
                            .requestMatchers(HttpMethod.GET, "/cities/**").permitAll()
                            .requestMatchers(HttpMethod.GET, "/attractions/**").permitAll()
                            .anyRequest()
                            .authenticated()
                )
                .sessionManagement(session -> session.sessionCreationPolicy(STATELESS))
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}

