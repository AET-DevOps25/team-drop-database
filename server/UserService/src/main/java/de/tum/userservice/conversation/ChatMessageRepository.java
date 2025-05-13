package de.tum.userservice.conversation;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessageEntity, Long> {
     List<ChatMessageEntity> findByConversationIdOrderByTimestampAsc(Long conversationId); // Correctly queries by the foreign key
}