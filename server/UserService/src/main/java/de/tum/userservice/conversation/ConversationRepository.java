package de.tum.userservice.conversation;

import de.tum.userservice.conversation.dto.ConversationDTO;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ConversationRepository extends JpaRepository<ConversationEntity, Long> {
    @Query("""
        SELECT new de.tum.userservice.conversation.dto.ConversationDTO(
                c.conversationId,
                c.title,
                c.createdAt
        )
        FROM ConversationEntity c
        WHERE c.userId = :userId 
        ORDER BY c.updatedAt DESC
        """)
    List<ConversationDTO> findByUserIdOrderByUpdatedAtDesc(@Param("userId") Long userId);

    @Query("select c.userId from ConversationEntity c where c.conversationId = :cid")
    Long findUserIdByConversationId(@Param("cid") Long conversationId);
}
