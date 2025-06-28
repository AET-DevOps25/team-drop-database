package de.tum.userservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import de.tum.userservice.user.UserEntity;
import de.tum.userservice.user.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test") // Activate the test profile to use H2
class UserControllerIT {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ObjectMapper objectMapper;

    // Clean the repository before each test
    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    @WithMockUser(username = "test.user@tum.de", roles = "USER")
    void createProfile_whenEmailMatchesPrincipal_shouldCreateProfile() throws Exception {
        UserEntity newUser = new UserEntity(null, "test.user@tum.de", "Test", "User", null, null);

        mockMvc.perform(post("/profiles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(newUser)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.email").value("test.user@tum.de"))
                .andExpect(jsonPath("$.firstName").value("Test"));
    }

    @Test
    @WithMockUser(username = "another.user@tum.de", roles = "USER")
    void createProfile_whenEmailDoesNotMatchPrincipal_shouldBeForbidden() throws Exception {
        UserEntity newUser = new UserEntity(null, "test.user@tum.de", "Test", "User", null, null);

        mockMvc.perform(post("/profiles")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(newUser)))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void getById_whenUserIsSelf_shouldReturnProfile() throws Exception {
        UserEntity savedUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        mockMvc.perform(get("/profiles/{id}", savedUser.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(savedUser.getId()))
                .andExpect(jsonPath("$.email").value("test.user@tum.de"));
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void getById_whenUserIsNotSelf_shouldBeForbidden() throws Exception {
        // User created in the database
        UserEntity targetUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        // Attacker with a different email tries to access the profile
        mockMvc.perform(get("/profiles/{id}", targetUser.getId()))
                .andExpect(status().isForbidden());
    }


    @Test
    @WithMockUser(username = "test.user@tum.de")
    void getByEmail_whenUserIsSelf_shouldReturnProfile() throws Exception {
        userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        mockMvc.perform(get("/profiles/email/{email}", "test.user@tum.de"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value("test.user@tum.de"));
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void getByEmail_whenUserIsNotSelf_shouldBeForbidden() throws Exception {
        userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        mockMvc.perform(get("/profiles/email/{email}", "test.user@tum.de"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void updateProfile_whenUserIsSelf_shouldUpdateProfile() throws Exception {
        UserEntity savedUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));
        UserEntity updatedInfo = new UserEntity(null, "test.user@tum.de", "TestUpdated", "UserUpdated", "new-pic.jpg", "new-pref");


        mockMvc.perform(put("/profiles/{id}", savedUser.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updatedInfo)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.firstName").value("TestUpdated"))
                .andExpect(jsonPath("$.lastName").value("UserUpdated"));
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void updateProfile_whenUserIsNotSelf_shouldBeForbidden() throws Exception {
        UserEntity targetUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));
        UserEntity updatedInfo = new UserEntity(null, "test.user@tum.de", "TestUpdated", "UserUpdated", null, null);

        mockMvc.perform(put("/profiles/{id}", targetUser.getId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updatedInfo)))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void deleteProfile_whenUserIsSelf_shouldDeleteProfile() throws Exception {
        UserEntity savedUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        mockMvc.perform(delete("/profiles/{id}", savedUser.getId()))
                .andExpect(status().isNoContent());
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void deleteProfile_whenUserIsNotSelf_shouldBeForbidden() throws Exception {
        UserEntity targetUser = userRepository.save(new UserEntity(null, "test.user@tum.de", "Test", "User", null, null));

        mockMvc.perform(delete("/profiles/{id}", targetUser.getId()))
                .andExpect(status().isForbidden());
    }
}