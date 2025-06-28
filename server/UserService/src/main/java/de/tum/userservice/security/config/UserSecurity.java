package de.tum.userservice.security.config;

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

        Long selfId = userRepository.findByEmail(email).getId();
        if (selfId == null) {
            return false;
        }

        Long ownerId = conversationRepository.findUserIdByConversationId(conversationId);
        if (ownerId == null) {
            return false;
        }

        return selfId.equals(ownerId);
    }
}
