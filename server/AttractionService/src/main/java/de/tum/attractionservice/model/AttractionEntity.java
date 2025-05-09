package de.tum.attractionservice.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.net.URL;
import java.util.List;

@Setter
@Getter
@Entity
@Table(name = "attractions")
public class AttractionEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String name;

    @Column(nullable = false)
    private String description;

    @Embedded
    private Location location;

    @ManyToOne
    @JoinColumn(name = "city_id", nullable = false)
    private CityEntity city;

    @ElementCollection
    @CollectionTable(
            name = "opening_hours",
            joinColumns = @JoinColumn(name = "id")
    )
    private List<OpeningHours> openingHours;

    @ElementCollection
    @CollectionTable(
            name = "photos",
            joinColumns = @JoinColumn(name = "id")
    )
    private List<URL> photos;

    private String website;

    public AttractionEntity() {
    }

}
