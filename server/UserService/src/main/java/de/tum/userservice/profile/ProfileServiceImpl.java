package de.tum.userservice.profile;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ProfileServiceImpl implements ProfileService{
    private final ProfileRepository repository;

    @Autowired
    public ProfileServiceImpl(ProfileRepository repository) {
        this.repository = repository;
    }

    @Override
    public ProfileEntity createProfile(ProfileEntity profile) {
        return repository.save(profile);
    }

    @Override
    public ProfileEntity getProfileById(Long id) {
        return repository.findById(id).orElse(null);
    }

    @Override
    public ProfileEntity updateProfile(Long id, ProfileEntity profile) {
        return repository.findById(id)
                .map(existing -> {
                    existing.setFirstName(profile.getFirstName());
                    existing.setLastName(profile.getLastName());
                    existing.setEmail(profile.getEmail());
                    return repository.save(existing);
                })
                .orElseThrow(() -> new RuntimeException("Profile not found with id " + id));
    }

    @Override
    public void deleteProfile(Long id) {
        repository.deleteById(id);
    }
}
