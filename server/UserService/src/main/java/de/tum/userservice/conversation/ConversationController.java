package de.tum.userservice.conversation;

import de.tum.userservice.conversation.dto.ConversationDTO;
import de.tum.userservice.conversation.dto.PromptDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/conversations")
@RequiredArgsConstructor
public class ConversationController {

    private final ConversationService service;

    @PostMapping("/{userId}")
    @PreAuthorize("@userSecurity.isSelf(#userId, principal.username)")
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

    @PostMapping("/email/{email}")
    @PreAuthorize("@userSecurity.emailsAreSame(#email, principal.username)")
    public ResponseEntity<ConversationEntity> createNewConversationByEmail(
            @RequestBody PromptDTO prompt,
            @PathVariable String email
    ) {
        ConversationEntity conversation;
        try {
            conversation = service.createNewConversationByEmail(email, prompt.getPrompt());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.status(HttpStatus.CREATED).body(conversation);
    }

    @GetMapping("/{conversationId}")
    @PreAuthorize("@userSecurity.canAccessConversation(#conversationId, principal.username)")
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
    @PreAuthorize("@userSecurity.canAccessConversation(#conversationId, principal.username)")
    public ResponseEntity<ConversationEntity> resumeConversation(
            @RequestBody PromptDTO prompt,
            @PathVariable Long conversationId
    ) {
        ConversationEntity conversation;
        try {
            conversation = service.resumeConversation(conversationId, prompt.getPrompt());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(conversation);
    }

    @DeleteMapping("/{conversationId}")
    @PreAuthorize("@userSecurity.canAccessConversation(#conversationId, principal.username)")
    public ResponseEntity<Void> deleteConversation(@PathVariable Long conversationId) {
        if (service.deleteConversation(conversationId)) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/h/{userId}")
    @PreAuthorize("@userSecurity.isSelf(#userId, principal.username)")
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

    @GetMapping("/h/email/{email}")
    @PreAuthorize("@userSecurity.emailsAreSame(#email, principal.username)")
    public ResponseEntity<List<ConversationDTO>> getConversationHistoryByEmail(
            @PathVariable String email
    ) {
        List<ConversationDTO> conversationHistory;
        try {
            conversationHistory = service.getConversationHistoryByEmail(email);
        } catch (IllegalArgumentException e) {
            if (e.getMessage().equals("User not found")) {
                return ResponseEntity.notFound().build();
            }
            return ResponseEntity.badRequest().build();
        }
        return ResponseEntity.ok(conversationHistory);
    }
}
