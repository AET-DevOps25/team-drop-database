package de.tum.userservice.conversation;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/conversations")
@RequiredArgsConstructor
public class ConversationController {

    private final ConversationService service;

    /**
     * POST /api/v1/conversations/chat
     * Body: { "prompt": "Where should I travel?", "conversationId": 123 } (conversationId is optional)
     * If conversationId is null, a new conversation is started.
     * Header: Authorization: Bearer <JWT>
     */
    // TODO: combine resume chat and create new chat
    @PostMapping("/chat/{userId}")
    public ResponseEntity<ChatResponse> chat(
            @RequestBody ChatRequest request,
            @PathVariable Long userId
    ) {
        // If request.getConversationId() is null, service will create a new one.
        return ResponseEntity.ok(service.converse(userId, request));
    }

    /**
     * GET /api/v1/conversations
     * Retrieves all conversations for the logged-in user.
     * Header: Authorization: Bearer <JWT>
     */
    // TODO: use conversationDTO instead
    @GetMapping("/messages/{userId}")
    public ResponseEntity<List<ConversationEntity>> getUserConversations(
            @PathVariable Long userId
    ) {
        return ResponseEntity.ok(service.getUserConversations(userId));
    }

    /**
     * GET /api/v1/conversations/messages/{userId}/{conversationId}/
     * Retrieves all messages for a specific conversation.
     * Header: Authorization: Bearer <JWT>
     */
    @GetMapping("/messages/{userId}/{conversationId}/")
    public ResponseEntity<List<ChatMessageEntity>> getConversationMessages(
            @PathVariable Long userId,
            @PathVariable Long conversationId
    ) {
        return ResponseEntity.ok(service.getConversationMessages(userId, conversationId));
    }

//    /**
//     * POST /api/v1/conversations
//     * Explicitly creates a new conversation.
//     * Body: { "title": "My new trip plan" } (optional)
//     * Header: Authorization: Bearer <JWT>
//     * @return The created conversation.
//     */
//    @PostMapping(/)
//    public ResponseEntity<ConversationEntity> createConversation(
//            @RequestBody(required = false) CreateConversationRequest request // A new DTO for just a title
//    ) {
//        Long userId = 1L; // TODO: Replace with authenticated user ID
//        String title = (request != null && request.getTitle() != null) ? request.getTitle() : "New Conversation";
//        ConversationEntity conversation = service.createNewConversation(userId, title);
//        return ResponseEntity.status(HttpStatus.CREATED).body(conversation);
//    }
//
//    // DTO for creating a conversation with an optional title
//    @lombok.Data
//    static class CreateConversationRequest {
//        private String title;
//    }
}