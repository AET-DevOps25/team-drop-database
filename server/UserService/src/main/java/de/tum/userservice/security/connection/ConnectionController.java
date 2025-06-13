package de.tum.userservice.security.connection;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/connection")
public class ConnectionController {

    @GetMapping("/ping")
    public ResponseEntity<String> checkConnection() {
        return ResponseEntity.ok("Pong");
    }

    @GetMapping("/user-ping")
    public ResponseEntity<String> checkUserConnection() {
        return ResponseEntity.ok("User Pong");
    }

    @GetMapping("/admin-ping")
    public ResponseEntity<String> checkAdminConnection() {
        return ResponseEntity.ok("Admin Pong");
    }

    @GetMapping("/manager-ping")
    public ResponseEntity<String> checkMangerConnection() {
        return ResponseEntity.ok("Manager Pong");
    }
}
