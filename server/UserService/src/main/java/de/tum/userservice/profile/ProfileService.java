package de.tum.userservice.profile;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ProfileService {
    private final ProfileRepository repository;

    public ProfileEntity createProfile(ProfileEntity profile) {
        if (repository.findByEmail(profile.getEmail()) != null) {
            throw new IllegalArgumentException("Email already exists");
        }
        return repository.save(profile);
    }

    public ProfileEntity getProfileById(Long id) {
        return repository.findById(id).orElseThrow(
                () -> new IllegalArgumentException("Profile not found with id " + id));
    }

    public ProfileEntity updateProfile(Long id, ProfileEntity profile) {
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
