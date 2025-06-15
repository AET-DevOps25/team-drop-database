package de.tum.attractionservice.service;

import de.tum.attractionservice.model.CityEntity;
import de.tum.attractionservice.repository.CityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class CityService {

    private final CityRepository cityRepository;

    @Autowired
    public CityService(CityRepository cityRepository) {
        this.cityRepository = cityRepository;
    }

    public CityEntity createCity(CityEntity city) {
        // may add unique checks
        return cityRepository.save(city);
    }

    public List<CityEntity> getAllCities() {
        return cityRepository.findAll();
    }

    public Optional<CityEntity> getCityById(Long id) {
        return cityRepository.findById(id);
    }

    public void deleteCity(Long id) {
        cityRepository.deleteById(id);
    }

    public boolean existsById(Long id) {
        return cityRepository.existsById(id);
    }
}

