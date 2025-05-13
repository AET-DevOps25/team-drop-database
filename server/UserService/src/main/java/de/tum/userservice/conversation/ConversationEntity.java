package de.tum.userservice.conversation;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name = "conversation")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class ConversationEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long userId;

    @Column
    private String title;

    @Column(nullable = false)
    private Instant createdAt;

    @Column
    private Instant updatedAt;

    // Optional: fetch all messages with the conversation
    // Be mindful of performance implications for very long conversations
    // @OneToMany(mappedBy = "conversation", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    // private List<ChatMessageEntity> messages = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = Instant.now();
        updatedAt = Instant.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = Instant.now();
    }
}