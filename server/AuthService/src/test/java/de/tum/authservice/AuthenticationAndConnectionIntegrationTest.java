package de.tum.authservice;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@TestInstance(Lifecycle.PER_CLASS)
@Transactional
@ActiveProfiles("test")
class AuthenticationAndConnectionIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    // ============== helper ==============

    /**
     * Registers a user with the given credentials and returns a valid
     * JWT produced by a subsequent authentication call.
     */
    private String registerAndLogin(String email, String password, String role) throws Exception {
        // 直接用 register 的响应，不再手动调用 authenticate
        String registerBody = objectMapper.createObjectNode()
                .put("email", email)
                .put("password", password)
                .put("role", role)
                .toString();

        String json = mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(registerBody))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        return objectMapper.readTree(json).get("access_token").asText();
    }

    // ============== authentication flow ==============

    @Test
    @DisplayName("Registering an already existing e‑mail should return 400 Bad Request")
    void duplicateEmailReturnsBadRequest() throws Exception {
        String email = "duplicate_user@tum.de";
        String password = "123456";

        // first registration is fine
        registerAndLogin(email, password, "USER");

        // second registration triggers 400
        String body = objectMapper.createObjectNode()
                .put("email", email)
                .put("password", password)
                .put("role", "USER")
                .toString();

        mockMvc.perform(post("/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest());
    }

    // ============== role‑based endpoints ==============

    @Test
    @DisplayName("Anonymous users can access /connection/ping")
    void pingIsPublic() throws Exception {
        mockMvc.perform(get("/connection/ping"))
                .andExpect(status().isOk())
                .andExpect(content().string("Pong"));
    }

    @Test
    @DisplayName("Users with role USER can hit /connection/user‑ping, but not /admin‑ping or /manager‑ping")
    void userRoleAccess() throws Exception {
        String token = registerAndLogin("user@tum.de", "123456", "USER");

        mockMvc.perform(get("/connection/user-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(content().string("User Pong"));

        mockMvc.perform(get("/connection/admin-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        mockMvc.perform(get("/connection/manager-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Users with role ADMIN can hit /connection/admin‑ping as well as /user‑ping, but not /manager‑ping")
    void adminRoleAccess() throws Exception {
        String token = registerAndLogin("admin@tum.de", "123456", "ADMIN");

        mockMvc.perform(get("/connection/admin-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(content().string("Admin Pong"));

        mockMvc.perform(get("/connection/user-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        mockMvc.perform(get("/connection/manager-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("Users with role MANAGER can hit /connection/manager‑ping and /user‑ping, but not /admin‑ping")
    void managerRoleAccess() throws Exception {
        String token = registerAndLogin("manager@tum.de", "123456", "MANAGER");

        mockMvc.perform(get("/connection/manager-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(content().string("Manager Pong"));

        mockMvc.perform(get("/connection/user-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());

        mockMvc.perform(get("/connection/admin-ping")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isForbidden());
    }
}

