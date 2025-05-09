package de.tum.userservice.conversation;

import java.util.List;

// TODO: Implement the GenAIClient class
public class GenAIClient {
    public String sendPromptAndGetReply(List<ChatMessage> history, String latestPrompt) {
        // TODO: integrate OpenAI SDK, build messages payload, call ChatCompletion, return content.
        return "This is a placeholder AI response to: " + latestPrompt;
    }
}
