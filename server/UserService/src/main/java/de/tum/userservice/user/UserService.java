package de.tum.userservice.user;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository repository;

    public UserEntity createProfile(UserEntity profile) {
        if (repository.findByEmail(profile.getEmail()) != null) {
            throw new IllegalArgumentException("Email already exists");
        }
        return repository.save(profile);
    }

    public UserEntity getProfileById(Long id) {
        return repository.findById(id).orElseThrow(
                () -> new IllegalArgumentException("Profile not found with id " + id));
    }

    public UserEntity getProfileByEmail(String email) {
        UserEntity profile = repository.findByEmail(email);
        if (profile == null) {
            throw new IllegalArgumentException("Profile not found with email " + email);
        }
        return profile;
    }

    public UserEntity updateProfile(Long id, UserEntity profile) {
        return repository.findById(id)
                .map(existing -> {
                    existing.setFirstName(profile.getFirstName());
                    existing.setLastName(profile.getLastName());
                    existing.setProfilePicture(profile.getProfilePicture());
                    existing.setPreference(profile.getPreference());
                    return repository.save(existing);
                })
                .orElseThrow(() -> new IllegalArgumentException("Profile not found with id " + id));
    }

    public boolean deleteProfile(Long id) {
        if (!repository.existsById(id)) {
            return false;
        }
        repository.deleteById(id);
        return true;
    }
}
