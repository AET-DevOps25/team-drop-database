package de.tum.attractionservice.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("City Controller Integration Tests")
public class CityControllerIntegrationTest extends BaseIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("获取所有城市 - 匿名用户可以访问")
    void getAllCities_AsAnonymousUser_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/cities"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("创建城市 - 需要管理员权限")
    void createCity_AsAdmin_ShouldReturnCreated() throws Exception {
        String cityJson = """
            {
                "name": "Test City",
                "country": "Germany",
                "description": "A test city for integration testing"
            }
            """;

        mockMvc.perform(post("/cities")
                .contentType(MediaType.APPLICATION_JSON)
                .content(cityJson))
                .andExpect(status().isCreated());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("创建城市 - 普通用户应该被拒绝")
    void createCity_AsUser_ShouldReturnForbidden() throws Exception {
        String cityJson = """
            {
                "name": "Forbidden City",
                "country": "Germany",
                "description": "This should not be created by user"
            }
            """;

        mockMvc.perform(post("/cities")
                .contentType(MediaType.APPLICATION_JSON)
                .content(cityJson))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("创建城市 - 匿名用户应该被拒绝")
    void createCity_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        String cityJson = """
            {
                "name": "München",
                "country": "Germany",
                "description": "A city in Germany",
                "latitude": 48.1303,
                "longitude": 11.5840
            }
            """;

        mockMvc.perform(post("/cities")
                .contentType(MediaType.APPLICATION_JSON)
                .content(cityJson))
                .andExpect(status().isUnauthorized());
    }
}
