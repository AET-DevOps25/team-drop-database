package de.tum.server.attraction;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

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

    public List<AttractionEntity> getAllAttractions() {
        return attractionRepository.findAll();
    }

    public void saveAttraction(AttractionEntity attraction) {
        attractionRepository.save(attraction);
    }

    public void deleteAttraction(AttractionEntity attraction) {
        attractionRepository.delete(attraction);
    }
}
