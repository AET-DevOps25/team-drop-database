package de.tum.attractionservice.controller;

import de.tum.attractionservice.importer.AttractionDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import de.tum.attractionservice.model.AttractionEntity;
import de.tum.attractionservice.service.AttractionService;

import java.util.List;


@RestController
@RequestMapping("/attractions")
public class AttractionController {
    private final AttractionService attractionService;

    @Autowired
    public AttractionController(AttractionService attractionService) {
        this.attractionService = attractionService;
    }

    @GetMapping
    public ResponseEntity<Page<AttractionEntity>> getAllAttractions(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "name") String sortBy) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(sortBy));
        Page<AttractionEntity> attractions = attractionService.getAllAttractions(pageRequest);
        return new ResponseEntity<>(attractions, HttpStatus.OK);
    }

    @GetMapping("/city/{city}")
    public ResponseEntity<Page<AttractionEntity>> getAttractionsByCity(
            @PathVariable String city,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "name") String sortBy) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(sortBy));
        Page<AttractionEntity> attractions = attractionService.getAttractionsByCity(city, pageRequest);
        return new ResponseEntity<>(attractions, HttpStatus.OK);
    }

    @GetMapping("/{name}")
    public ResponseEntity<AttractionEntity> getAttractionByName(@PathVariable String name) {
        AttractionEntity attraction = attractionService.getAttractionByName(name);
        if (attraction != null) {
            return new ResponseEntity<>(attraction, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    @GetMapping("/id/{id}")
    public ResponseEntity<AttractionEntity> getAttractionById(@PathVariable Long id) {
        AttractionEntity attraction = attractionService.getAttractionById(id);
        if (attraction != null) {
            return new ResponseEntity<>(attraction, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    @PostMapping(consumes = "application/json")
    public ResponseEntity<String> ingest(@RequestBody List<AttractionDTO> dtos) {
        attractionService.saveAll(dtos);
        return ResponseEntity.ok("Saved " + dtos.size() + " attractions");
    }


    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAttraction(@PathVariable Long id) {
        AttractionEntity attraction = attractionService.getAttractionById(id);
        if (attraction != null) {
            attractionService.deleteById(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } else {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }
}
