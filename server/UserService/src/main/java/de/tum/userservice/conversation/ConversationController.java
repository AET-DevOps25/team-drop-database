package de.tum.userservice.conversation;

import lombok.RequiredArgsConstructor;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ConversationController {
    private final ConversationService conversationService;

    /**
     * POST /api/chat
     * Body: { "prompt": "Where should I travel in Italy?" }
     * Header: Authorization: Bearer <JWT from AuthService>
     */
    @PostMapping
    public ResponseEntity<ChatResponse> chat(
//            @AuthenticationPrincipal Jwt jwt,
            @RequestBody ChatRequest request
    ) {
//        Long userId = Long.valueOf(jwt.getSubject());
        Long userId = 1L; // TODO: remove this line and uncomment the above line
        return ResponseEntity.ok(conversationService.converse(userId, request));
    }

    /**
     * GET /api/chat/history
     * Header: Authorization: Bearer <JWT>
     */
    @GetMapping("/history")
    public ResponseEntity<List<ChatMessage>> history(
//            @AuthenticationPrincipal Jwt jwt
    ) {
//        Long userId = Long.valueOf(jwt.getSubject());
        Long userId = 1L; // TODO: remove this line and uncomment the above line
        return ResponseEntity.ok(conversationService.history(userId));
    }

}
