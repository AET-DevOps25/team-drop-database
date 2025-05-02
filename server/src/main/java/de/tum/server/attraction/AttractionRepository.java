package de.tum.server.attraction;

import de.tum.server.user.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AttractionRepository extends JpaRepository<AttractionEntity, Long> {
    Optional<AttractionEntity> findByName(String name);
}
