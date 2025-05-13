package de.tum.userservice.conversation;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ConversationServiceImpl implements ConversationService {
    private final ConversationRepository conversationRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final GenAIClient genAIClient;

    @Override
    @Transactional
    public ChatResponse converse(Long userId, ChatRequest request) {
        ConversationEntity conversation;
        // Start a new conversation
        if (request.getConversationId() == null) {
            String title = request.getPrompt().length() > 50 ? request.getPrompt().substring(0, 50) + "..." : request.getPrompt();
            conversation = createNewConversation(userId, title);
        } else {
            // Add to existing conversation
            conversation = conversationRepository.findByIdAndUserId(request.getConversationId(), userId)
                    .orElseThrow(() -> new RuntimeException("Conversation not found or access denied."));
            conversation.setUpdatedAt(Instant.now()); // Update timestamp
            conversation = conversationRepository.save(conversation);
        }

        // Save user message
        ChatMessageEntity userMessage = ChatMessageEntity.builder()
                .conversation(conversation)
                .role(Role.USER)
                .content(request.getPrompt())
                .build();
        chatMessageRepository.save(userMessage);

        // Get history for GenAI (for this specific conversation)
        List<ChatMessageEntity> history = chatMessageRepository.findByConversationIdOrderByTimestampAsc(conversation.getId());

        // Get AI reply
        String aiReplyContent = genAIClient.sendPromptAndGetReply(history, request.getPrompt());

        // Save AI message
        ChatMessageEntity aiMessage = ChatMessageEntity.builder()
                .conversation(conversation)
                .role(Role.SYSTEM)
                .content(aiReplyContent)
                .build();
        chatMessageRepository.save(aiMessage);

        return new ChatResponse(aiReplyContent);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ChatMessageEntity> getConversationMessages(Long userId, Long conversationId) {
        // TODO: Ensure the user has access to this conversation
        conversationRepository.findByIdAndUserId(conversationId, userId)
                .orElseThrow(() -> new RuntimeException("Conversation not found or access denied.")); // Replace with specific exception
        return chatMessageRepository.findByConversationIdOrderByTimestampAsc(conversationId);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ConversationEntity> getUserConversations(Long userId) {
        return conversationRepository.findByUserIdOrderByUpdatedAtDesc(userId);
    }

    @Override
    @Transactional
    public ConversationEntity createNewConversation(Long userId, String title) {
        ConversationEntity newConversation = ConversationEntity.builder()
                .userId(userId)
                .title(title)
                .build();
        return conversationRepository.save(newConversation);
    }
}