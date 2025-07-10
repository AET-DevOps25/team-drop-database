package de.tum.attractionservice.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import de.tum.attractionservice.model.AttractionEntity;
import de.tum.attractionservice.model.CityEntity;
import de.tum.attractionservice.repository.AttractionRepository;
import de.tum.attractionservice.repository.CityRepository;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;


@AutoConfigureMockMvc
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("Attraction Controller Integration Tests")
@Transactional
public class AttractionControllerIntegrationTest {

    @Autowired
    private CityRepository cityRepository;
    @Autowired
    private AttractionRepository attractionRepository;

    private Long testCityId;
    private Long testAttractionId;

    @BeforeEach
    void setUp() {
        // Clean up database
        attractionRepository.deleteAll();
        cityRepository.deleteAll();

        // Create test city data
        CityEntity testCity = new CityEntity();
        testCity.setName("Munich");
        testCity.setCountry("Germany");
        testCity.setDescription("Capital of Bavaria");
        testCity.setLatitude(48.1351);
        testCity.setLongitude(11.5820);
        testCity = cityRepository.save(testCity);
        testCityId = testCity.getId();

        // Create test attraction data
        AttractionEntity testAttraction = new AttractionEntity();
        testAttraction.setName("Test Attraction");
        testAttraction.setDescription("A test attraction for integration tests");
        testAttraction.setCity(testCity);
        testAttraction.setWebsite("https://test.com");

        // Create location information
        de.tum.attractionservice.model.Location location = new de.tum.attractionservice.model.Location();
        location.setAddress("Test Address");
        location.setCountry("Germany");
        location.setLatitude("48.1351");
        location.setLongitude("11.5820");
        testAttraction.setLocation(location);

        testAttraction = attractionRepository.save(testAttraction);
        testAttractionId = testAttraction.getId();
    }


    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("Get all attractions - Anonymous user can access")
    void getAllAttractions_AsAnonymousUser_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/attractions"))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("Get attractions by city - Anonymous user can access")
    void getAttractionsByCity_AsAnonymousUser_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/attractions/city/Munich"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("Create attraction - Requires admin privileges")
    void createAttraction_AsAdmin_ShouldReturnCreated() throws Exception {
        String attractionJson = """
            {
            "name": "New Deutsches Museum",
            "description": "One of the world's largest science and technology museums.",
            "city": {
                "id": %d
                },
            "location": {
                "address": "Museumsinsel 1",
                "country": "Germany",
                "latitude": "48.1303",
                "longitude": "11.5840"
            },
            "openingHours": [
                {
                "day": "MONDAY",
                "from": "09:00",
                "to": "17:00"
                },
                {
                "day": "TUESDAY",
                "from": "09:00",
                "to": "17:00"
                }
            ],
            "photos": [
                "https://example.com/photo1.jpg",
                "https://example.com/photo2.jpg"
            ],
            "website": "https://www.deutsches-museum.de"
            }
            """.formatted(testCityId);

        mockMvc.perform(post("/attractions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(attractionJson))
                .andExpect(status().isCreated());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("Create attraction - Requires admin privileges")
    void createAttractions_AsAdmin_ShouldReturnCreated() throws Exception {
        String attractionJson = """
            [
                {
                "name": "New Deutsches Museum",
                "description": "One of the world's largest science and technology museums.",
                "city": "Munich",
                "country": "Germany",
                "openingHours": [
                    "Monday: 09:00 - 18:00",
                    "Tuesday: 09:00 - 18:00",
                    "Wednesday: 09:00 - 18:00",
                    "Thursday: 09:00 - 18:00",
                    "Friday: 09:00 - 18:00",
                    "Saturday: 09:00 - 18:00",
                    "Sunday: 09:00 - 18:00"
                ],
                "photos": [
                    "https://example.com/photo1.jpg",
                    "https://example.com/photo2.jpg"
                ],
                "website": "https://www.deutsches-museum.de",
                "address": "Museumsinsel 1, 80538 München",
                "latitude": "48.131381",
                "longitude": "11.585605"
                }
            ]
            """;

        mockMvc.perform(post("/attractions/list")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(attractionJson))
                .andExpect(status().isCreated());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("Create attraction - Regular user should be forbidden")
    void createAttraction_AsUser_ShouldReturnForbidden() throws Exception {
        String attractionJson = """
                {
                    "name": "User Test Attraction",
                    "description": "A test attraction",
                    "city": {"id": %d},
                    "location": {
                        "address": "Test Address 1",
                        "country": "Germany",
                        "latitude": "48.1351",
                        "longitude": "11.5820"
                    }
                }
                """.formatted(testCityId);

        mockMvc.perform(post("/attractions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(attractionJson))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Create attraction - Anonymous user should be unauthorized")
    void createAttraction_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        String attractionJson = """
                {
                    "name": "Anonymous Test Attraction",
                    "description": "A test attraction",
                    "city": {"id": %d},
                    "location": {
                        "address": "Test Address",
                        "country": "Germany",
                        "latitude": "48.1351",
                        "longitude": "11.5820"
                    }
                }
                """.formatted(testCityId);

        mockMvc.perform(post("/attractions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(attractionJson))
                .andExpect(status().isUnauthorized());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("Delete attraction - Requires admin privileges")
    void deleteAttraction_AsAdmin_ShouldReturnNoContent() throws Exception {
        mockMvc.perform(delete("/attractions/" + testAttractionId))
                .andExpect(status().isNoContent());
    }

    @Test
    @DisplayName("Get specific attraction - Anonymous user can access")
    void getAttractionById_AsAnonymousUser_ShouldReturnAttraction() throws Exception {
        mockMvc.perform(get("/attractions/id/" + testAttractionId))
                .andExpect(status().isOk());
    }
}
