package de.tum.userservice.user;

import org.springframework.stereotype.Service;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;

@Service
public class UserService {
    private final UserRepository repository;

    private final Counter createProfileCounter;
    private final Counter createProfileErrorCounter;
    private final Timer createProfileTimer;


    private final Counter getProfileCounter;
    private final Counter getProfileErrorCounter;
    private final Timer getProfileTimer;

    private final Counter updateProfileCounter;
    private final Counter updateProfileErrorCounter;
    private final Timer updateProfileTimer;

    private final Counter deleteProfileCounter;
    private final Counter deleteProfileErrorCounter;
    private final Timer deleteProfileTimer;

    public UserService(UserRepository repository, MeterRegistry registry) {
        this.repository = repository;

        this.createProfileCounter = Counter
                .builder("user_service_profile_creation_total")
                .description("Total number of user profiles created")
                .register(registry);
        this.createProfileErrorCounter = Counter
                .builder("user_service_profile_creation_errors_total")
                .description("Total number of errors during user profile creation")
                .register(registry);
        this.createProfileTimer = Timer
                .builder("user_service_profile_creation_duration_seconds")
                .description("Time to create a user profile")
                .publishPercentileHistogram()
                .register(registry);

        this.getProfileCounter = Counter
                .builder("user_service_profile_fetch_total")
                .description("Total number of fetch user profiles attempts")
                .register(registry);
        this.getProfileErrorCounter = Counter
                .builder("user_service_profile_fetch_errors_total")
                .description("Total number of errors during fetching profile")
                .register(registry);
        this.getProfileTimer = Timer
                .builder("user_service_profile_fetch_duration_seconds")
                .description("Time to fetch a user profile")
                .publishPercentileHistogram()
                .register(registry);

        this.updateProfileCounter = Counter
                .builder("user_service_profile_update_total")
                .description("Total number of profile updates")
                .register(registry);
        this.updateProfileErrorCounter = Counter
                .builder("user_service_profile_update_errors_total")
                .description("Total number of errors during updating profiles")
                .register(registry);
        this.updateProfileTimer = Timer
                .builder("user_profile_update_duration_seconds")
                .description("Time to update a user profile")
                .publishPercentileHistogram()
                .register(registry);

        this.deleteProfileCounter = Counter
                .builder("user_service_profile_deletion_total")
                .description("Total number of profile deletion attempts")
                .register(registry);
        this.deleteProfileErrorCounter = Counter
                .builder("user_service_profile_deletion_errors_total")
                .description("Total number of errors during deleting profiles")
                .register(registry);
        this.deleteProfileTimer = Timer
                .builder("user_service_profile_deletion_duration_seconds")
                .description("Time to delete a user profile")
                .publishPercentileHistogram()
                .register(registry);
    }

    public UserEntity createProfile(UserEntity profile) {
        createProfileCounter.increment();
        return createProfileTimer.record(() -> {
            try {
                if (repository.findByEmail(profile.getEmail()) != null) {
                    throw new IllegalArgumentException("Email already exists");
                }
                return repository.save(profile);
            } catch (Exception e) {
                createProfileErrorCounter.increment();
                throw e;
            }
        });
//        if (repository.findByEmail(profile.getEmail()) != null) {
//            throw new IllegalArgumentException("Email already exists");
//        }
//        return repository.save(profile);
    }

    public UserEntity getProfileById(Long id) {
        getProfileCounter.increment();
        return getProfileTimer.record(() -> {
            try {
                return repository.findById(id)
                        .orElseThrow(() -> new IllegalArgumentException("Profile not found with id " + id));
            } catch (Exception e) {
                getProfileErrorCounter.increment();
                throw e;
            }
        });
//        return repository.findById(id).orElseThrow(
//                () -> new IllegalArgumentException("Profile not found with id " + id));
    }

    public UserEntity getProfileByEmail(String email) {
        getProfileCounter.increment();
        return getProfileTimer.record(() -> {
            try {
                UserEntity profile = repository.findByEmail(email);
                if (profile == null) {
                    throw new IllegalArgumentException("Profile not found with email " + email);
                }
                return profile;
            } catch (Exception e) {
                getProfileErrorCounter.increment();
                throw e;
            }
        });
//        UserEntity profile = repository.findByEmail(email);
//        if (profile == null) {
//            throw new IllegalArgumentException("Profile not found with email " + email);
//        }
//        return profile;
    }

    public UserEntity updateProfile(Long id, UserEntity profile) {
        updateProfileCounter.increment();
        return updateProfileTimer.record(() -> {
            try {
                return repository.findById(id)
                        .map(existing -> {
                            existing.setFirstName(profile.getFirstName());
                            existing.setLastName(profile.getLastName());
                            existing.setProfilePicture(profile.getProfilePicture());
                            existing.setPreference(profile.getPreference());
                            return repository.save(existing);
                        })
                        .orElseThrow(() -> new IllegalArgumentException("Profile not found with id " + id));
            } catch (Exception e) {
                updateProfileErrorCounter.increment();
                throw e;
            }
        });
//        return repository.findById(id)
//                .map(existing -> {
//                    existing.setFirstName(profile.getFirstName());
//                    existing.setLastName(profile.getLastName());
//                    existing.setProfilePicture(profile.getProfilePicture());
//                    existing.setPreference(profile.getPreference());
//                    return repository.save(existing);
//                })
//                .orElseThrow(() -> new IllegalArgumentException("Profile not found with id " + id));
    }

    public boolean deleteProfile(Long id) {
        deleteProfileCounter.increment();
        return deleteProfileTimer.record(() -> {
            try {
                if (!repository.existsById(id)) {
                    return false;
                }
                repository.deleteById(id);
                return true;
            } catch (Exception e) {
                deleteProfileErrorCounter.increment();
                throw e;
            }
        });
//        if (!repository.existsById(id)) {
//            return false;
//        }
//        repository.deleteById(id);
//        return true;
    }
}
