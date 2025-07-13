package de.tum.userservice;

import com.fasterxml.jackson.databind.ObjectMapper;
import de.tum.userservice.conversation.ConversationEntity;
import de.tum.userservice.conversation.ChatMessageEntity;
import de.tum.userservice.conversation.ConversationRepository;
import de.tum.userservice.conversation.Role;
import de.tum.userservice.conversation.dto.PromptDTO;
import de.tum.userservice.user.UserEntity;
import de.tum.userservice.user.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class ConversationControllerIT {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    UserRepository userRepository;

    @Autowired
    ConversationRepository conversationRepository;

    @Autowired
    ObjectMapper objectMapper;

    @BeforeEach
    void cleanDb() {
        conversationRepository.deleteAll();
        userRepository.deleteAll();
    }

    @Test
    @WithMockUser(username = "alice@tum.de")
    void createConversation_whenUserIsSelf_shouldReturnCreated() throws Exception {
        UserEntity alice = userRepository.save(new UserEntity(null, "alice@tum.de",
                "Alice", "Tester", null, null));

        mockMvc.perform(post("/conversations/{userId}", alice.getId())
                        .contentType(MediaType.TEXT_PLAIN)
                        .content("Hello, world!"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.userId").value(alice.getId()))
                .andExpect(jsonPath("$.messages[0].content").value("Hello, world!"));
    }

    @Test
    @WithMockUser(username = "mallory@tum.de")
    void createConversation_whenUserIsNotSelf_shouldBeForbidden() throws Exception {
        UserEntity alice = userRepository.save(new UserEntity(null, "alice@tum.de",
                "Alice", "Tester", null, null));

        mockMvc.perform(post("/conversations/{userId}", alice.getId())
                        .contentType(MediaType.TEXT_PLAIN)
                        .content("Should fail"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    @Disabled("Temporarily disabled until LLM API is live")
    void createConversationByEmail_whenEmailMatchesPrincipal_shouldReturnCreated() throws Exception {
        userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        PromptDTO prompt = new PromptDTO("Hi there");
        mockMvc.perform(post("/conversations/email/{email}", "test.user@tum.de")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(prompt)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.messages[0].content").value("Hi there"));
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void createConversationByEmail_whenEmailDoesNotMatch_shouldBeForbidden() throws Exception {
        userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        PromptDTO prompt = new PromptDTO("Should fail");
        mockMvc.perform(post("/conversations/email/{email}", "test.user@tum.de")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(prompt)))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void getConversation_whenOwner_shouldReturnOk() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        Instant now = Instant.now();

        ConversationEntity conv = ConversationEntity.builder()
                .userId(user.getId())
                .title("Chat")
                .createdAt(now)
                .updatedAt(now)
                .build();

        ChatMessageEntity msg = ChatMessageEntity.builder()
                .conversation(conv)
                .role(Role.USER)
                .content("Ping")
                .createdAt(now)
                .build();

        conv.getMessages().add(msg);
        conversationRepository.save(conv);

        mockMvc.perform(get("/conversations/{id}", conv.getConversationId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.conversationId").value(conv.getConversationId()));
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void getConversation_whenNotOwner_shouldBeForbidden() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        ConversationEntity conv = conversationRepository.save(
                ConversationEntity.builder()
                        .userId(user.getId())
                        .title("Chat")
                        .createdAt(Instant.now())
                        .updatedAt(Instant.now())
                        .build()
        );

        mockMvc.perform(get("/conversations/{id}", conv.getConversationId()))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "nobody@tum.de")
    void getConversation_whenConversationDoesNotExist_shouldReturnNotFound() throws Exception {
        mockMvc.perform(get("/conversations/{id}", 999L))
                .andExpect(status().isNotFound());
    }

    @Test
    @Disabled("Temporarily disabled until LLM API is live")
    @WithMockUser(username = "test.user@tum.de")
    void resumeConversation_whenOwner_shouldReturnOk() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        ConversationEntity conv = conversationRepository.save(
                ConversationEntity.builder()
                        .userId(user.getId())
                        .title("Chat")
                        .createdAt(Instant.now())
                        .updatedAt(Instant.now())
                        .build()
        );

        PromptDTO prompt = new PromptDTO("Second message");

        mockMvc.perform(put("/conversations/{id}", conv.getConversationId())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(prompt)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.messages[-1:].content").value("Second message")); // last message
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void deleteConversation_whenOwner_shouldReturnNoContent() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        ConversationEntity conv = conversationRepository.save(
                ConversationEntity.builder()
                        .userId(user.getId())
                        .title("Chat")
                        .createdAt(Instant.now())
                        .updatedAt(Instant.now())
                        .build()
        );

        mockMvc.perform(delete("/conversations/{id}", conv.getConversationId()))
                .andExpect(status().isNoContent());
    }

    @Test
    @WithMockUser(username = "attacker@tum.de")
    void deleteConversation_whenNotOwner_shouldBeForbidden() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        ConversationEntity conv = conversationRepository.save(
                ConversationEntity.builder()
                        .userId(user.getId())
                        .title("Chat")
                        .createdAt(Instant.now())
                        .updatedAt(Instant.now())
                        .build()
        );

        mockMvc.perform(delete("/conversations/{id}", conv.getConversationId()))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "test.user@tum.de")
    void getConversationHistory_whenOwner_shouldReturnOk() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        // store two dummy conversations
        conversationRepository.save(new ConversationEntity(null, user.getId(),
                "First", Instant.now(), Instant.now(), List.of()));
        conversationRepository.save(new ConversationEntity(null, user.getId(),
                "Second", Instant.now(), Instant.now(), List.of()));

        mockMvc.perform(get("/conversations/h/{userId}", user.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(2));
    }

    @Test
    @WithMockUser(username = "attakcer@tum.de")
    void getConversationHistory_whenNotOwner_shouldBeForbidden() throws Exception {
        UserEntity user = userRepository.save(new UserEntity(null, "test.user@tum.de",
                "Test", "User", null, null));

        mockMvc.perform(get("/conversations/h/{userId}", user.getId()))
                .andExpect(status().isForbidden());
    }
}
