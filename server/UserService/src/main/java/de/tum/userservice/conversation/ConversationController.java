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

    @PostMapping("/{userId}")
    public ResponseEntity<ConversationEntity> createNewConversation(
            @RequestBody String prompt,
            @PathVariable Long userId
    ) {
        ConversationEntity conversation;
        try {
            conversation = service.createNewConversation(userId, prompt);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(conversation);
    }

    @GetMapping("/{conversationId}")
    public ResponseEntity<ConversationEntity> getConversationContext(
            @PathVariable Long conversationId
    ) {
        ConversationEntity conversation;
        try {
            conversation = service.getConversationContext(conversationId);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(conversation);
    }

    @PutMapping("/{conversationId}")
    public ResponseEntity<ConversationEntity> resumeConversation(
            @RequestBody String prompt,
            @PathVariable Long conversationId
    ) {
        ConversationEntity conversation;
        try {
            conversation = service.resumeConversation(conversationId, prompt);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(conversation);
    }

    @DeleteMapping("/{conversationId}")
    public ResponseEntity<Void> deleteConversation(@PathVariable Long conversationId) {
        if (service.deleteConversation(conversationId)) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/h/{userId}")
    public ResponseEntity<List<ConversationDTO>> getConversationHistory(
            @PathVariable Long userId
    ) {
        List<ConversationDTO> conversationHistory;
        try {
            conversationHistory = service.getConversationHistory(userId);
        } catch (IllegalArgumentException e) {
            if (e.getMessage().equals("User not found")) {
                return ResponseEntity.notFound().build();
            } else if (e.getMessage().equals("No conversations found for this user")) {
                return ResponseEntity.noContent().build();
            }
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(conversationHistory);
    }
}