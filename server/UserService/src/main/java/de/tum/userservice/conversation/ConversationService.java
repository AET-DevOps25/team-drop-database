package de.tum.userservice.conversation;

import java.util.List;

public interface ConversationService {
    ChatResponse converse(Long userId, ChatRequest request);
    List<ChatMessage> history(Long userId);
}
