package de.tum.userservice.profile;

import java.util.List;
import java.util.Optional;

public interface ProfileService {
    ProfileEntity createProfile(ProfileEntity profile);
    ProfileEntity getProfileById(Long id);
    ProfileEntity updateProfile(Long id, ProfileEntity profile);
    void deleteProfile(Long id);
}
