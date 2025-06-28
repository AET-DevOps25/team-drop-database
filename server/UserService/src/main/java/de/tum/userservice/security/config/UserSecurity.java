package de.tum.userservice.security.config;

import de.tum.userservice.conversation.ConversationEntity;
import de.tum.userservice.conversation.ConversationRepository;
import de.tum.userservice.user.UserEntity;
import de.tum.userservice.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Objects;

@Component("userSecurity")
@RequiredArgsConstructor
public class UserSecurity {
    private final UserRepository userRepository;
    private final ConversationRepository conversationRepository;

    public boolean emailsAreSame(String InputEmail, String tokenEmail) {
        return InputEmail.equals(tokenEmail);
    }

    public boolean isSelf(Long pathId, String email) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        if (auth == null || !auth.isAuthenticated()) {
            return false;
        }

        UserEntity current = userRepository.findByEmail(email);

        return current != null && Objects.equals(current.getId(), pathId);
    }

    public boolean canAccessConversation(Long conversationId, String email) {
        ConversationEntity conv = conversationRepository.findById(conversationId)
                .orElse(null);

        if (conv == null) {
            return true;
        }

        UserEntity caller = userRepository.findByEmail(email);
        if (caller == null) {
            return false;
        }

        return conv.getUserId().equals(caller.getId());
    }
}
