package de.tum.server.attraction;

import jakarta.persistence.*;

import java.net.URL;
import java.util.List;

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

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Location getLocation() {
        return location;
    }

    public void setLocation(Location location) {
        this.location = location;
    }

    public List<OpeningHours> getOpeningHours() {
        return openingHours;
    }

    public void setOpeningHours(List<OpeningHours> openingHours) {
        this.openingHours = openingHours;
    }

    public List<URL> getPhotos() {
        return photos;
    }

    public void setPhotos(List<URL> photos) {
        this.photos = photos;
    }

    public String getWebsite() {
        return website;
    }

    public void setWebsite(String website) {
        this.website = website;
    }
}
