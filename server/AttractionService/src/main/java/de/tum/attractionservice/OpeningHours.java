package de.tum.attractionservice;

import jakarta.persistence.Embeddable;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Embeddable
public class OpeningHours {
    private String day;

    private String fromTime;

    private String toTime;

    public OpeningHours() {
    }

}