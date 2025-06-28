package de.tum.attractionservice.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("Authentication Integration Tests")
public class AuthenticationIntegrationTest extends BaseIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("Ping test - Anonymous user can access")
    void connectionPing_AsAnonymous_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/ping"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("User connection test - As user should return success")
    void userPing_AsUser_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/user-ping"))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("User connection test - Anonymous user should be unauthorized")
    void userPing_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        mockMvc.perform(get("/connection/user-ping"))
                .andExpect(status().isUnauthorized());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("Admin connection test - As admin should return success")
    void adminPing_AsAdmin_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("Admin connection test - As user should return forbidden")
    void adminPing_AsUser_ShouldReturnForbidden() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Admin connection test - Anonymous user should be unauthorized")
    void adminPing_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isUnauthorized());
    }

    @WithMockUser(username = "manager", roles = {"MANAGER"})
    @Test
    @DisplayName("Manager connection test - As manager should return success")
    void managerPing_AsManager_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/manager-ping"))
                .andExpect(status().isOk());
    }
}
