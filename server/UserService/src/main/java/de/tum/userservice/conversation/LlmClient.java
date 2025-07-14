package de.tum.userservice.conversation;

import de.tum.userservice.conversation.dto.ResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Collections;

@Component
@RequiredArgsConstructor
public class LlmClient {
    private final WebClient.Builder webClientBuilder;

    @Value("${llm.api.base-url}")
    private String baseUrl;
    @Value("${llm.api.key}")
    private String apiKey;

    public String generateResponse(String prompt) {
        System.out.println(prompt);
        return webClientBuilder
                .baseUrl(baseUrl)
//                .defaultHeader("X-API-KEY", apiKey)
                .build()
                .post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(Collections.singletonMap("question", prompt))
                .retrieve()
                .bodyToMono(ResponseDTO.class)
                .map(ResponseDTO::getAnswer)
                .block();
    }
}