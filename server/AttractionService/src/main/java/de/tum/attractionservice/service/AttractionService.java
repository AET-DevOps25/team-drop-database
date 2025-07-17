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

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;


@Service
public class AttractionService {

    private final AttractionRepository attractionRepository;
    private final CityRepository cityRepository;

    private final Counter totalLookUpsCounter;
    private final Counter singleLookUpCounter;
    private final Counter totalSavesCounter;
    private final Counter singleSaveCounter;
    private final Counter totalDeletesCounter;
    private final Counter importedAttractionsCounter;
    private final Counter urlParseErrorsCounter;

    private final Timer lookupTimer;
    private final Timer importTimer;

    @Autowired
    public AttractionService(AttractionRepository attractionRepository, CityRepository cityRepository, MeterRegistry registry) {
        this.attractionRepository = attractionRepository;
        this.cityRepository = cityRepository;

        this.totalLookUpsCounter = Counter
                .builder("attraction_service_get_all_total")
                .description("Total number of getAllAttractions calls")
                .register(registry);
        this.singleLookUpCounter = Counter
                .builder("attraction_service_get_by_id_total")
                .description("Total number of getAttractionById calls")
                .register(registry);
        this.totalSavesCounter = Counter
                .builder("attraction_service_save_all_total")
                .description("Total number of saveAll calls")
                .register(registry);
        this.singleSaveCounter = Counter
                .builder("attraction_service_save_total")
                .description("Total number of saveAttraction calls")
                .register(registry);
        this.totalDeletesCounter = Counter
                .builder("attraction_service_deletes_total")
                .description("Total number of deleteById calls")
                .register(registry);
        this.lookupTimer = Timer
                .builder("attraction_service_get_by_name_duration_seconds")
                .description("Latency of getAttractionByName")
                .publishPercentileHistogram()
                .register(registry);
        this.importTimer = Timer
                .builder("attraction_service_save_all_duration_seconds")
                .description("Time to process saveAll imports")
                .publishPercentileHistogram()
                .register(registry);
        this.importedAttractionsCounter = Counter
                .builder("attraction_service_imported_attractions_total")
                .description("Number of new attractions imported")
                .register(registry);
        this.urlParseErrorsCounter = Counter
                .builder("attraction_service_url_parse_errors_total")
                .description("Invalid photo URL count during import")
                .register(registry);
    }

    public AttractionEntity getAttractionByName(String name) {
        return attractionRepository.findByName(name).orElse(null);
    }

    public Page<AttractionEntity> getAllAttractions(Pageable pageable) {
        totalLookUpsCounter.increment();
        return attractionRepository.findAll(pageable);
    }

    public Page<AttractionEntity> getAttractionsByCity(String city, Pageable pageable) {
        return attractionRepository.findByCity_Name(city, pageable);
    }

    public AttractionEntity getAttractionById(Long id) {
        singleLookUpCounter.increment();
        return attractionRepository.findById(id).orElse(null);
    }

    public void saveAttraction(AttractionEntity attraction) {
        singleSaveCounter.increment();
        attractionRepository.save(attraction);
    }

    public void deleteById(Long id) {
        totalDeletesCounter.increment();
        attractionRepository.deleteById(id);
    }

    public void saveAll(List<AttractionDTO> dtos) {
        totalSavesCounter.increment();

        importTimer.record(() -> {
            for (AttractionDTO dto : dtos) {
                if (attractionRepository.findByName(dto.getName()).isEmpty()) {
                    importedAttractionsCounter.increment();
                    attractionRepository.save(toEntity(dto));
                }
            }
        });

//        Set<String> existing = attractionRepository.findAll()
//                .stream()
//                .map(AttractionEntity::getName)
//                .collect(Collectors.toSet());
//
//        dtos.stream()
//                .filter(dto -> !existing.contains(dto.getName()))
//                .map(this::toEntity)
//                .forEach(attractionRepository::save);
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
                    catch (Exception e) {
                        urlParseErrorsCounter.increment();
                        throw new RuntimeException("Invalid URL", e);
                    }
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