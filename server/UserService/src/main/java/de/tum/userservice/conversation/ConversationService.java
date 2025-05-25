package de.tum.userservice.conversation;

import de.tum.userservice.profile.ProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;


@Service
@RequiredArgsConstructor
public class ConversationService {
    private final ProfileRepository profileRepository;
    private final ConversationRepository conversationRepository;

    @Transactional
    public ConversationEntity createNewConversation(Long userId, String prompt) {
        if (profileRepository.findById(userId).isEmpty()) {
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
        return conversationRepository.save(conversation);
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
        if (!profileRepository.existsById(userId)) {
            throw new IllegalArgumentException("User not found");
        }
        List<ConversationDTO> conversationDTOList = conversationRepository
                .findByUserIdOrderByUpdatedAtDesc(userId);
        if (conversationDTOList.isEmpty()) {
            throw new IllegalArgumentException("No conversations found for this user");
        }
        return conversationDTOList;
    }

    //    @Transactional
//    public ChatResponse converse(Long userId, ChatRequest request) {
//        ConversationEntity conversation;
//        // Start a new conversation
//        if (request.getConversationId() == null) {
//            String title = request.getPrompt().length() > 50 ? request.getPrompt().substring(0, 50) + "..." : request.getPrompt();
//            conversation = createNewConversation(userId, title);
//        } else {
//            // Add to existing conversation
//            conversation = conversationRepository.findByConversationId(request.getConversationId());
//            conversation.setUpdatedAt(Instant.now()); // Update timestamp
//            conversation = conversationRepository.save(conversation);
//        }
//
//        // Save user message
//        ChatMessageEntity userMessage = ChatMessageEntity.builder()
//                .conversation(conversation)
//                .role(Role.USER)
//                .content(request.getPrompt())
//                .build();
//        chatMessageRepository.save(userMessage);
//
//        // Get history for GenAI (for this specific conversation)
//        List<ChatMessageEntity> history = chatMessageRepository.findByChatMessageId(conversation.getConversationId());
//
//        // Get AI reply
//        String aiReplyContent = genAIClient.sendPromptAndGetReply(history, request.getPrompt());
//
//        // Save AI message
//        ChatMessageEntity aiMessage = ChatMessageEntity.builder()
//                .conversation(conversation)
//                .role(Role.SYSTEM)
//                .content(aiReplyContent)
//                .build();
//        chatMessageRepository.save(aiMessage);
//
//        return new ChatResponse(aiReplyContent);
//    }
}