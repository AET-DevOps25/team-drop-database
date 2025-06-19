package de.tum.attractionservice.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Entity
public class Location {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String address;

    @Column(nullable = false)
    private String country;

    @Column(nullable = false)
    private String latitude;

    @Column(nullable = false)
    private String longitude;

    public Location() {
    }

}
