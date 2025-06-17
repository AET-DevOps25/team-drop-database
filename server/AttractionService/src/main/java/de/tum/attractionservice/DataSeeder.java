package de.tum.attractionservice;

import net.datafaker.Faker;
import de.tum.attractionservice.model.*;
import de.tum.attractionservice.repository.AttractionRepository;
import de.tum.attractionservice.repository.CityRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.net.MalformedURLException;
import java.net.URL;
import java.time.DayOfWeek;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Insert ~120 mock attractions across 6 demo cities.
 * Disable (or guard with a profile) in production!
 */
@Component
@Profile("dev")
@RequiredArgsConstructor
public class DataSeeder implements CommandLineRunner {

    private final AttractionRepository attractionRepo;
    private final CityRepository cityRepo;

    private final Faker faker = new Faker();

    @Override
    public void run(String... args) throws Exception {

        if (attractionRepo.count() > 0) {
            System.out.println("[DataSeeder] Attractions already exist, skipping seeding.");
            return;
        }

        List<CityEntity> cities = seedCities();

        int perCity = 5;
        for (CityEntity city : cities) {
            for (int i = 0; i < perCity; i++) {
                AttractionEntity attr = buildRandomAttraction(city, i);
                attractionRepo.save(attr);
            }
        }

        System.out.printf("[DataSeeder] Inserted %d attractions across %d cities%n",
                perCity * cities.size(), cities.size());
    }

    /* ---------------------------------------------------------------------- */
    /* Helpers                                                                */
    /* ---------------------------------------------------------------------- */

    private List<CityEntity> seedCities() {
        List<String> names = List.of(
                "Washington, DC", "London", "Charleston",
                "Paris", "New York City", "New Orleans"
        );

        List<CityEntity> cities = new ArrayList<>();
        for (String name : names) {
            CityEntity city = new CityEntity();
            city.setName(name);
            city.setCountry(faker.country().name());
            cities.add(cityRepo.save(city));
        }
        return cities;
    }

    private AttractionEntity buildRandomAttraction(CityEntity city, int idx) throws MalformedURLException {
        AttractionEntity a = new AttractionEntity();
        a.setName(faker.company().catchPhrase() + " " + idx);
        a.setDescription(faker.lorem().sentence(15));

        // Location
        Location loc = new Location();
        loc.setCountry(faker.country().name());
        loc.setLatitude(randomInRange(-90, 90));
        loc.setLongitude(randomInRange(-180, 180));
        loc.setAddress(faker.address().streetAddress());
        a.setLocation(loc);

        // City
        a.setCity(city);

        // Opening hours — Mon-Sun 09:00-18:00
        List<OpeningHours> hoursList = new ArrayList<>();
        for (DayOfWeek dow : DayOfWeek.values()) {
            OpeningHours oh = new OpeningHours();
            oh.setDay(dow.name());
            oh.setFromTime("09:00");
            oh.setToTime("18:00");
            hoursList.add(oh);
        }
        a.setOpeningHours(hoursList);

        // Photos
        a.setPhotos(List.of(
                unsplash("attraction"), unsplash("travel"), unsplash(city.getName())
        ));

        // Website
        a.setWebsite("https://" + faker.internet().domainName());

        return a;
    }

    private String randomInRange(double min, double max) {
        return Double.toString(ThreadLocalRandom.current().nextDouble(min, max));
    }

    private URL unsplash(String keyword) throws MalformedURLException {
        return new URL("https://source.unsplash.com/random/800x600?" + keyword);
    }
}
