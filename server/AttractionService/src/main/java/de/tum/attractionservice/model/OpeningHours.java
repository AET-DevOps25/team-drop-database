package de.tum.attractionservice.model;

import jakarta.persistence.Embeddable;
import lombok.Getter;
import lombok.Setter;

import java.time.DayOfWeek;

@Setter
@Getter
@Embeddable
public class OpeningHours {
    private DayOfWeek day;

    private String fromTime;

    private String toTime;

    public OpeningHours() {
    }

}