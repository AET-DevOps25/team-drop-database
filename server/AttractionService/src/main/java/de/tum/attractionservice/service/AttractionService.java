package de.tum.attractionservice.service;

import de.tum.attractionservice.importer.AttractionDTO;
import de.tum.attractionservice.model.CityEntity;
import de.tum.attractionservice.model.Location;
import de.tum.attractionservice.model.OpeningHours;
import de.tum.attractionservice.repository.CityRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import de.tum.attractionservice.model.AttractionEntity;
import de.tum.attractionservice.repository.AttractionRepository;

import java.net.URL;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;


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
        return attractionRepository.findByCity_Name(city, pageable);
    }

    public AttractionEntity getAttractionById(Long id) {
        return attractionRepository.findById(id).orElse(null);
    }

    public void saveAttraction(AttractionEntity attraction) {
        attractionRepository.save(attraction);
    }

    public void deleteById(Long id) {
        attractionRepository.deleteById(id);
    }

    public void saveAll(List<AttractionDTO> dtos) {
        // pull all existing names in one go
        Set<String> existing = attractionRepository.findAll()
                .stream()
                .map(AttractionEntity::getName)
                .collect(Collectors.toSet());

        dtos.stream()
                .filter(dto -> !existing.contains(dto.getName()))
                .map(this::toEntity)
                .forEach(attractionRepository::save);
    }

    private AttractionEntity toEntity(AttractionDTO dto) {
        // 1) City: find or create
        CityEntity city = cityRepository.findByName(dto.getCity())
                .orElseGet(() -> {
                    CityEntity c = new CityEntity();
                    c.setName(dto.getCity());
                    c.setCountry(dto.getCountry());
                    return cityRepository.save(c);
                });

        // 2) Location
        Location loc = new Location();
        loc.setAddress(dto.getAddress());
        loc.setCountry(dto.getCountry());
        loc.setLatitude(dto.getLatitude());
        loc.setLongitude(dto.getLongitude());

        // 3) OpeningHours (parse “Day: HH:mm - HH:mm”)
        List<OpeningHours> hours = dto.getOpeningHours().stream().map(s -> {
            String[] parts = s.split(": ", 2);
            String day = parts[0];
            String[] times = parts[1].split(" - ");
            OpeningHours oh = new OpeningHours();
            oh.setDay(day);
            oh.setFromTime(times[0]);
            oh.setToTime(times[1]);
            return oh;
        }).collect(Collectors.toList());

        // 4) Photos → URL objects
        List<URL> photoUrls = dto.getPhotos().stream()
                .map(u -> {
                    try { return new URL(u); }
                    catch (Exception e) { throw new RuntimeException("Invalid URL", e); }
                })
                .collect(Collectors.toList());

        // 5) Assemble AttractionEntity
        AttractionEntity ent = new AttractionEntity();
        ent.setName(dto.getName());
        ent.setDescription(dto.getDescription());
        ent.setCity(city);
        ent.setLocation(loc);
        ent.setOpeningHours(hours);
        ent.setPhotos(photoUrls);
        ent.setWebsite(dto.getWebsite());
        return ent;
    }
}