package de.tum.userservice.security.config;

import de.tum.userservice.conversation.ConversationRepository;
import de.tum.userservice.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component("userSecurity")
@RequiredArgsConstructor
public class UserSecurity {
    private final UserRepository userRepository;
    private final ConversationRepository conversationRepository;

    public boolean isSelf(Long pathId, String email) {
        Long idOfEmail = userRepository.findByEmail(email).getId();
        return pathId.equals(idOfEmail);
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
