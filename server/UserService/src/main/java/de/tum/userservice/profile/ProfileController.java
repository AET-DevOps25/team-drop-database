package de.tum.userservice.profile;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/profiles")
public class ProfileController {
    private final ProfileService service;

    @Autowired
    public ProfileController(ProfileService service) {
        this.service = service;
    }

    /**
     * POST /api/v1/profiles
     * Creates a new profile.
     */
    @PostMapping
    public ResponseEntity<ProfileEntity> create(@RequestBody ProfileEntity profile) {
        try {
            ProfileEntity createdProfile = service.createProfile(profile);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdProfile);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
    * GET /api/v1/profiles/{id}
    * Retrieves a profile by ID.
    */
    @GetMapping("/{id}")
    public ResponseEntity<ProfileEntity> getById(@PathVariable Long id) {
        try {
            ProfileEntity profile = service.getProfileById(id);
            return ResponseEntity.ok(profile);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * PUT /api/v1/profiles/{id}
     * Updates a profile by ID.
     */
    @PutMapping("/{id}")
    public ResponseEntity<ProfileEntity> update(@PathVariable Long id, @RequestBody ProfileEntity profile) {
        try {
            ProfileEntity updated = service.updateProfile(id, profile);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * DELETE /api/v1/profiles/{id}
     * Deletes a profile by ID.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (service.deleteProfile(id)) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
