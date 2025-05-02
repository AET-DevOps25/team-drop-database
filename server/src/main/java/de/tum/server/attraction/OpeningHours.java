package de.tum.server.attraction;

import jakarta.persistence.Embeddable;

@Embeddable
public class OpeningHours {
    private String day;

    private String fromTime;

    private String toTime;

    public OpeningHours() {
    }

    public String getDay() {
        return day;
    }

    public void setDay(String day) {
        this.day = day;
    }

    public String getFromTime() {
        return fromTime;
    }

    public void setFromTime(String fromTime) {
        this.fromTime = fromTime;
    }

    public String getToTime() {
        return toTime;
    }

    public void setToTime(String toTime) {
        this.toTime = toTime;
    }
}
