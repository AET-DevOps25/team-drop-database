package de.tum.userservice.conversation;

import java.util.List;

public interface ConversationService {
    /**
     * Handles a chat message. If request.conversationId is null, starts a new conversation.
     * Otherwise, adds the message to the existing conversation.
     *
     * @param userId User sending the message
     * @param request The chat request containing the prompt and optional conversationId
     * @return The chat response from the AI
     */
    ChatResponse converse(Long userId, ChatRequest request);

    /**
     * Retrieves all messages for a specific conversation belonging to a user.
     *
     * @param userId User owning the conversation
     * @param conversationId The ID of the conversation
     * @return List of chat messages
     */
    List<ChatMessageEntity> getConversationMessages(Long userId, Long conversationId);

    /**
     * Retrieves all conversations for a specific user.
     *
     * @param userId The ID of the user
     * @return List of conversations
     */
    List<ConversationEntity> getUserConversations(Long userId);

    /**
     * Creates a new conversation. Typically called when the first message is sent
     * without a conversationId, but can be exposed if needed.
     * @param userId The ID of the user
     * @param title Optional title for the new conversation
     * @return The newly created conversation
     */
    ConversationEntity createNewConversation(Long userId, String title);

    // TODO: Delete a conversation
    // void deleteConversation(Long userId, Long conversationId);
}