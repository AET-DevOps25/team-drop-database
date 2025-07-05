package de.tum.attractionservice.importer;

import lombok.Data;
import java.util.List;

@Data
public class AttractionDTO {
    private String name;
    private String description;
    private String city;
    private String country;
    private List<String> openingHours;
    private List<String> photos;
    private String website;
    private String address;
    private String latitude;
    private String longitude;
}
