package de.tum.attractionservice;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AttractionRepository extends JpaRepository<AttractionEntity, Long> {
    Optional<AttractionEntity> findByName(String name);
    Page<AttractionEntity> findByLocationCity(String city, Pageable pageable);
}