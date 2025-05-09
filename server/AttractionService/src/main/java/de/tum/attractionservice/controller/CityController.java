package de.tum.attractionservice.controller;

import de.tum.attractionservice.model.CityEntity;
import de.tum.attractionservice.repository.CityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/cities")
public class CityController {

    private final CityRepository cityRepository;

    @Autowired
    public CityController(CityRepository cityRepository) {
        this.cityRepository = cityRepository;
    }

    
    @GetMapping
    public ResponseEntity<List<CityEntity>> getAllCities() {
        return ResponseEntity.ok(cityRepository.findAll());
    }

    
    @GetMapping("/{id}")
    public ResponseEntity<CityEntity> getCityById(@PathVariable Long id) {
        Optional<CityEntity> city = cityRepository.findById(id);
        return city.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public ResponseEntity<CityEntity> createCity(@RequestBody CityEntity city) {
        CityEntity saved = cityRepository.save(city);
        return new ResponseEntity<>(saved, HttpStatus.CREATED);
    }

    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')")
    public ResponseEntity<Void> deleteCity(@PathVariable Long id) {
        if (cityRepository.existsById(id)) {
            cityRepository.deleteById(id);
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
