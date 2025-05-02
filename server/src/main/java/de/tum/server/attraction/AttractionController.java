package de.tum.server.attraction;

import de.tum.server.user.UserEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
    public ResponseEntity<List<AttractionEntity>> getAllAttractions() {
        List<AttractionEntity> attractions = attractionService.getAllAttractions();
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

    @PostMapping
    public ResponseEntity<Void> saveAttraction(@RequestBody AttractionEntity attraction) {
        attractionService.saveAttraction(attraction);
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    @DeleteMapping
    public ResponseEntity<Void> deleteAttraction(@RequestBody AttractionEntity attraction) {
        attractionService.deleteAttraction(attraction);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
