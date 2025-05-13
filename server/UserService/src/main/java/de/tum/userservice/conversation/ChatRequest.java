package de.tum.userservice.conversation;

import lombok.Data;

@Data
public class ChatRequest {
    private String prompt;
    private Long conversationId; // Can be null to start a new conversation
}