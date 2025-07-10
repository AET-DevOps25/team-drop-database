package de.tum.userservice.conversation.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResponseDTO {
    private boolean success;
    private String question;
    private String answer;
    @JsonProperty("result_count")
    private int resultCount;
}
