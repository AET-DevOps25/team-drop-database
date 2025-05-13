package de.tum.userservice.conversation;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ConversationRepository extends JpaRepository<ConversationEntity, Long> {
    List<ConversationEntity> findByUserIdOrderByUpdatedAtDesc(Long userId);
    Optional<ConversationEntity> findByIdAndUserId(Long id, Long userId);
}