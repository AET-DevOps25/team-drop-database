package de.tum.userservice.conversation.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
@AllArgsConstructor
public class ConversationDTO {
    private Long id;
    private String title;
    private Instant updatedAt;
}
