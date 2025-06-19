package de.tum.userservice.user;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.parameters.P;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/profiles")
public class UserController {
    private final UserService service;

    @Autowired
    public UserController(UserService service) {
        this.service = service;
    }

    /**
     * POST /user-service/api/v1/profiles
     * Creates a new profile.
     */
    @PostMapping
    @PreAuthorize("@userSecurity.emailsAreSame(#profile.email, principal.username)")
    public ResponseEntity<UserEntity> create(@P("profile") @RequestBody UserEntity profile) {
        try {
            UserEntity createdProfile = service.createProfile(profile);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdProfile);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
    * GET /user-service/api/v1/profiles/{id}
    * Retrieves a profile by ID.
    */
    @GetMapping("/{id}")
    @PreAuthorize("@userSecurity.isSelf(#id, principal.username)")
    public ResponseEntity<UserEntity> getById(@PathVariable Long id) {
        try {
            UserEntity profile = service.getProfileById(id);
            return ResponseEntity.ok(profile);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/email/{email}")
    @PreAuthorize("@userSecurity.emailsAreSame(#email, principal.username)")
    public ResponseEntity<UserEntity> getByEmail(@PathVariable String email) {
        try {
            UserEntity profile = service.getProfileByEmail(email);
            return ResponseEntity.ok(profile);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * PUT /user-service/api/v1/profiles/{id}
     * Updates a profile by ID.
     */
    @PutMapping("/{id}")
    @PreAuthorize("@userSecurity.isSelf(#id, principal.username)")
    public ResponseEntity<UserEntity> update(@PathVariable Long id, @RequestBody UserEntity profile) {
        try {
            UserEntity updated = service.updateProfile(id, profile);
            return ResponseEntity.ok(updated);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * DELETE /user-service/api/v1/profiles/{id}
     * Deletes a profile by ID.
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("@userSecurity.isSelf(#id, principal.username)")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (service.deleteProfile(id)) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}
