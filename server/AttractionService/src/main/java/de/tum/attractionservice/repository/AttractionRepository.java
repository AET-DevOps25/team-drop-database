package de.tum.attractionservice.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import de.tum.attractionservice.model.AttractionEntity;

import java.util.Optional;

@Repository
public interface AttractionRepository extends JpaRepository<AttractionEntity, Long> {
    Optional<AttractionEntity> findByName(String name);
    Page<AttractionEntity> findByCity_Name(String cityName, Pageable pageable);
    Optional<AttractionEntity> findById(Long id);

}