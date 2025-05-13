package de.tum.userservice.conversation;

import lombok.NoArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;

// TODO: Implement the GenAIClient class
@Component
public class GenAIClient {
    public String sendPromptAndGetReply(List<ChatMessageEntity> history, String latestPrompt) {
        // TODO: integrate OpenAI SDK, build messages payload, call ChatCompletion, return content.

        return "This is a placeholder AI response to: " + latestPrompt;
    }
}
