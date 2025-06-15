package de.tum.attractionservice.service;

import de.tum.attractionservice.model.CityEntity;
import de.tum.attractionservice.repository.CityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import de.tum.attractionservice.model.AttractionEntity;
import de.tum.attractionservice.repository.AttractionRepository;


@Service
public class AttractionService {

    private final AttractionRepository attractionRepository;
    private final CityRepository cityRepository;

    @Autowired
    public AttractionService(AttractionRepository attractionRepository, CityRepository cityRepository) {
        this.attractionRepository = attractionRepository;
        this.cityRepository = cityRepository;
    }

    public AttractionEntity getAttractionByName(String name) {
        return attractionRepository.findByName(name).orElse(null);
    }

    public Page<AttractionEntity> getAllAttractions(Pageable pageable) {
        return attractionRepository.findAll(pageable);
    }

    public Page<AttractionEntity> getAttractionsByCity(String city, Pageable pageable) {
        return attractionRepository.findByLocationCity(city, pageable);
    }

    public void saveAttraction(AttractionEntity attraction) {
        Long cityId = attraction.getCity().getId();
        CityEntity managedCity = cityRepository.findById(cityId)
                .orElseThrow(() -> new IllegalArgumentException("City with ID " + cityId + " not found"));

        attraction.setCity(managedCity);
        attractionRepository.save(attraction);
    }

    public void deleteAttraction(AttractionEntity attraction) {
        attractionRepository.delete(attraction);
    }
}