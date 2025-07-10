package de.tum.userservice.conversation;

import de.tum.userservice.conversation.dto.ConversationDTO;
import de.tum.userservice.user.UserEntity;
import de.tum.userservice.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;


@Service
@RequiredArgsConstructor
public class ConversationService {
    private final UserRepository userRepository;
    private final ConversationRepository conversationRepository;
    private final LlmClient llmClient;

    @Transactional
    public ConversationEntity createNewConversation(Long userId, String prompt) {
        if (userRepository.findById(userId).isEmpty()) {
            throw new IllegalArgumentException("User not found");
        }
        ChatMessageEntity userMessage = ChatMessageEntity.builder()
                .role(Role.USER)
                .content(prompt)
                .build();
        ConversationEntity conversation = ConversationEntity.builder()
                .userId(userId)
                .title("New Conversation")
                .build();
        userMessage.setConversation(conversation);
        conversation.getMessages().add(userMessage);
        return conversationRepository.save(conversation);
    }

    @Transactional
    public ConversationEntity createNewConversationByEmail(String email, String prompt) {
        UserEntity user = userRepository.findByEmail(email);
        if (user == null) {
            throw new IllegalArgumentException("User not found");
        }
        Long userId = user.getId();
        ChatMessageEntity userMessage = ChatMessageEntity.builder()
                .role(Role.USER)
                .content(prompt)
                .build();
        ConversationEntity conversation = ConversationEntity.builder()
                .userId(userId)
                .title("New Conversation")
                .build();
        userMessage.setConversation(conversation);
        conversation.getMessages().add(userMessage);
        conversation = conversationRepository.save(conversation);

        String llmText = callLlmAndPersistReply(conversation, prompt);
        conversation.setTitle(extractTitle(llmText));
        return conversation;
    }

    @Transactional(readOnly = true)
    public ConversationEntity getConversationContext(Long conversationId) {
        return conversationRepository
                .findById(conversationId)
                .orElseThrow(() -> new IllegalArgumentException("Conversation not found"));
    }

    @Transactional
    public ConversationEntity resumeConversation(Long conversationId, String prompt) {
        ConversationEntity conversation = conversationRepository
                .findById(conversationId)
                .orElseThrow(() -> new IllegalArgumentException("Conversation not found"));
        ChatMessageEntity userMessage = ChatMessageEntity.builder()
                .role(Role.USER)
                .content(prompt)
                .build();
        conversation.getMessages().add(userMessage);
        userMessage.setConversation(conversation);
        conversation.setUpdatedAt(Instant.now());
        conversationRepository.save(conversation);

        callLlmAndPersistReply(conversation, prompt);
        return conversation;
    }

    @Transactional
    public boolean deleteConversation(Long conversationId) {
        if (!conversationRepository.existsById(conversationId)) {
            return false;
        }
        conversationRepository.deleteById(conversationId);
        return true;
    }

    @Transactional(readOnly = true)
    public List<ConversationDTO> getConversationHistory(Long userId) {
        if (!userRepository.existsById(userId)) {
            throw new IllegalArgumentException("User not found");
        }
        List<ConversationDTO> conversationDTOList = conversationRepository
                .findByUserIdOrderByUpdatedAtDesc(userId);
        if (conversationDTOList.isEmpty()) {
            throw new IllegalArgumentException("No conversations found for this user");
        }
        return conversationDTOList;
    }

    @Transactional(readOnly = true)
    public List<ConversationDTO> getConversationHistoryByEmail(String email) {
        UserEntity user = userRepository.findByEmail(email);
        if (user == null) {
            throw new IllegalArgumentException("User not found");
        }
        Long userId = user.getId();
        return conversationRepository
                .findByUserIdOrderByUpdatedAtDesc(userId);
    }

    private String callLlmAndPersistReply(ConversationEntity conversation, String prompt) {
        String llmResponse = llmClient.generateResponse(prompt);

        ChatMessageEntity llmMessage = ChatMessageEntity.builder()
                .role(Role.SYSTEM)
                .content(llmResponse)
                .build();
        llmMessage.setConversation(conversation);
        conversation.getMessages().add(llmMessage);

        conversation.setUpdatedAt(Instant.now());
        conversationRepository.save(conversation);

        return llmResponse;
    }

    private String extractTitle(String llmText) {
        String[] lines = llmText.split("\n", 2);
        return lines[0].length() > 50
                ? lines[0].substring(0, 47) + "..."
                : lines[0];
    }

}
