package de.tum.userservice.profile;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ProfileRepository extends JpaRepository<ProfileEntity, Long> {
    ProfileEntity findByEmail(String email);
}
