package de.tum.attractionservice.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import de.tum.attractionservice.model.AttractionEntity;
import de.tum.attractionservice.repository.AttractionRepository;


@Service
public class AttractionService {

    private final AttractionRepository attractionRepository;

    @Autowired
    public AttractionService(AttractionRepository attractionRepository) {
        this.attractionRepository = attractionRepository;
    }

    public AttractionEntity getAttractionByName(String name) {
        return attractionRepository.findByName(name).orElse(null);
    }

    public Page<AttractionEntity> getAllAttractions(Pageable pageable) {
        return attractionRepository.findAll(pageable);
    }

    public Page<AttractionEntity> getAttractionsByCity(String city, Pageable pageable) {
        return attractionRepository.findByCity_Name(city, pageable);
    }

    public AttractionEntity getAttractionById(Long id) {
        return attractionRepository.findById(id).orElse(null);
    }

    public void saveAttraction(AttractionEntity attraction) {
        attractionRepository.save(attraction);
    }

    public void deleteAttraction(AttractionEntity attraction) {
        attractionRepository.delete(attraction);
    }
}