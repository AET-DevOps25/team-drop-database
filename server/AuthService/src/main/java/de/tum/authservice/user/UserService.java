package de.tum.authservice.user;

import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.security.Principal;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;

@Service
public class UserService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepository repository;

    private final Counter pwdChangeAttempts;
    private final Counter pwdChangeSuccesses;
    private final Counter pwdChangeFailures;
    private final Timer pwdChangeTimer;

    public UserService(PasswordEncoder passwordEncoder,
                       UserRepository repository,
                       MeterRegistry registry) {
        this.passwordEncoder = passwordEncoder;
        this.repository = repository;

        // Password-change metrics
        this.pwdChangeAttempts = Counter
                .builder("authentication_service_password_change_attempts_total")
                .description("Total password change attempts")
                .register(registry);
        this.pwdChangeSuccesses = Counter
                .builder("authentication_service_password_change_success_total")
                .description("Total successful password changes")
                .register(registry);
        this.pwdChangeFailures = Counter
                .builder("authentication_service_password_change_failure_total")
                .description("Total failed password change attempts")
                .register(registry);

        this.pwdChangeTimer = Timer
                .builder("authentication_service_password_change_duration_seconds")
                .description("Time taken by changePassword()")
                .publishPercentileHistogram()
                .register(registry);
    }

    public void changePassword(ChangePasswordRequest request, Principal connectedUser) {
        pwdChangeAttempts.increment();
        pwdChangeTimer.record(() -> {
            var user = (User) ((UsernamePasswordAuthenticationToken) connectedUser).getPrincipal();

            // check if the current password is correct
            if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
                pwdChangeFailures.increment();
                throw new IllegalStateException("Wrong password");
            }
            // check if the two new passwords are the same
            if (!request.getNewPassword().equals(request.getConfirmationPassword())) {
                pwdChangeFailures.increment();
                throw new IllegalStateException("Passwords do not match");
            }

            // update and save the new password
            user.setPassword(passwordEncoder.encode(request.getNewPassword()));
            repository.save(user);
            pwdChangeSuccesses.increment();
        });

//        var user = (User) ((UsernamePasswordAuthenticationToken) connectedUser).getPrincipal();
//
//        // check if the current password is correct
//        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
//            throw new IllegalStateException("Wrong password");
//        }
//        // check if the two new passwords are the same
//        if (!request.getNewPassword().equals(request.getConfirmationPassword())) {
//            throw new IllegalStateException("Password are not the same");
//        }
//
//        // update the password
//        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
//
//        // save the new password
//        repository.save(user);
    }

    public User findByEmail(String email) {
        return repository.findByEmail(email).orElse(null);
    }
}