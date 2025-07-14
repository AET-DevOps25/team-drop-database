package de.tum.userservice.conversation;

import de.tum.userservice.conversation.dto.ConversationDTO;
import de.tum.userservice.user.UserEntity;
import de.tum.userservice.user.UserRepository;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.MeterRegistry;


@Service
public class ConversationService {
    private final UserRepository userRepository;
    private final ConversationRepository conversationRepository;
    private final LlmClient llmClient;

    private final Counter createCounter;
    private final Counter createErrorCounter;
    private final Timer createTimer;

    private final Counter resumeCounter;
    private final Counter resumeErrorCounter;
    private final Timer resumeTimer;

    private final Counter deleteCounter;
    private final Counter deleteErrorCounter;
    private final Timer deleteTimer;

    private final Counter historyCounter;
    private final Counter historyErrorCounter;
    private final Timer historyTimer;

    private final Counter llmErrorCounter;
    private final Timer llmCallTimer;

    public ConversationService(UserRepository userRepository,
                               ConversationRepository conversationRepository,
                               LlmClient llmClient,
                               MeterRegistry registry) {
        this.userRepository = userRepository;
        this.conversationRepository = conversationRepository;
        this.llmClient = llmClient;

        this.createCounter = Counter
                .builder("conversation_service_create_total")
                .description("Total number of conversations created")
                .register(registry);
        this.createErrorCounter = Counter
                .builder("conversation_service_creation_errors_total")
                .description("Total number of errors when creating conversation")
                .register(registry);
        this.createTimer = Timer
                .builder("conversation_service_create_duration_seconds")
                .description("Time to create a new conversation")
                .publishPercentileHistogram()
                .register(registry);

        this.resumeCounter = Counter
                .builder("conversation_service_resume_total")
                .description("Total number of conversations resumed")
                .register(registry);
        this.resumeErrorCounter = Counter
                .builder("conversation_service_resume_errors_total")
                .description("Total number of errors when resuming conversation")
                .register(registry);
        this.resumeTimer = Timer
                .builder("conversation_service_resume_duration_seconds")
                .description("Time to resume a conversation")
                .publishPercentileHistogram()
                .register(registry);

        this.deleteCounter = Counter
                .builder("conversation_service_delete_total")
                .description("Total number of conversations deleted")
                .register(registry);
        this.deleteErrorCounter = Counter
                .builder("conversation_service_deletion_errors_total")
                .description("Total number of errors when deleting conversation")
                .register(registry);
        this.deleteTimer = Timer
                .builder("conversation_service_delete_duration_seconds")
                .description("Time to delete a conversation")
                .publishPercentileHistogram()
                .register(registry);

        this.historyCounter = Counter
                .builder("conversation_service_history_retrieval_total")
                .description("Total number of conversation history retrievals")
                .register(registry);
        this.historyErrorCounter = Counter
                .builder("conversation_service_history_retrieval_errors_total")
                .description("Total number of errors when retrieving history")
                .register(registry);
        this.historyTimer = Timer
                .builder("conversation_service_history_retrieval_duration_seconds")
                .description("Time to retrieve conversation history")
                .publishPercentileHistogram()
                .register(registry);

        this.llmErrorCounter = Counter
                .builder("conversation_service_llm_response_errors_total")
                .description("Total number of errors during LLM response generation")
                .register(registry);
        this.llmCallTimer = Timer.builder("conversation_service_llm_response_duration_seconds")
                .description("Time taken for LLM response generation and persistence")
                .publishPercentileHistogram()
                .register(registry);
    }

    @Transactional
    public ConversationEntity createNewConversation(Long userId, String prompt) {
        if (userRepository.findById(userId).isEmpty()) {
            throw new IllegalArgumentException("User not found");
        }
        ChatMessageEntity userMessage = ChatMessageEntity.builder()
                .role(Role.USER)
                .content(prompt)
                .build();
        ConversationEntity conversation = ConversationEntity.builder()
                .userId(userId)
                .title("New Conversation")
                .build();
        userMessage.setConversation(conversation);
        conversation.getMessages().add(userMessage);
        return conversationRepository.save(conversation);
    }

    @Transactional
    public ConversationEntity createNewConversationByEmail(String email, String prompt) {
        createCounter.increment();
        return createTimer.record(() -> {
            try {
                UserEntity user = userRepository.findByEmail(email);
                if (user == null) {
                    throw new IllegalArgumentException("User not found");
                }
                Long userId = user.getId();
                ChatMessageEntity userMessage = ChatMessageEntity.builder()
                        .role(Role.USER)
                        .content(prompt)
                        .build();
                ConversationEntity conversation = ConversationEntity.builder()
                        .userId(userId)
                        .title("New Conversation")
                        .build();
                userMessage.setConversation(conversation);
                conversation.getMessages().add(userMessage);
                conversation = conversationRepository.save(conversation);

                String llmText = callLlmAndPersistReply(conversation, prompt);
                conversation.setTitle(extractTitle(llmText));
                return conversation;
            } catch (Exception e) {
                createErrorCounter.increment();
                throw e;
            }
        });
//        UserEntity user = userRepository.findByEmail(email);
//        if (user == null) {
//            throw new IllegalArgumentException("User not found");
//        }
//        Long userId = user.getId();
//        ChatMessageEntity userMessage = ChatMessageEntity.builder()
//                .role(Role.USER)
//                .content(prompt)
//                .build();
//        ConversationEntity conversation = ConversationEntity.builder()
//                .userId(userId)
//                .title("New Conversation")
//                .build();
//        userMessage.setConversation(conversation);
//        conversation.getMessages().add(userMessage);
//        conversation = conversationRepository.save(conversation);
//
//        String llmText = callLlmAndPersistReply(conversation, prompt);
//        conversation.setTitle(extractTitle(llmText));
//        return conversation;
    }

    @Transactional(readOnly = true)
    public ConversationEntity getConversationContext(Long conversationId) {
        return conversationRepository
                .findById(conversationId)
                .orElseThrow(() -> new IllegalArgumentException("Conversation not found"));
    }

    @Transactional
    public ConversationEntity resumeConversation(Long conversationId, String prompt) {
        resumeCounter.increment();
        return resumeTimer.record(() -> {
            try {
                ConversationEntity conversation = conversationRepository
                        .findById(conversationId)
                        .orElseThrow(() -> new IllegalArgumentException("Conversation not found"));
                ChatMessageEntity userMessage = ChatMessageEntity.builder()
                        .role(Role.USER)
                        .content(prompt)
                        .build();
                conversation.getMessages().add(userMessage);
                userMessage.setConversation(conversation);
                conversation.setUpdatedAt(Instant.now());
                conversationRepository.save(conversation);

                callLlmAndPersistReply(conversation, prompt);
                return conversation;
            } catch (Exception e) {
                resumeErrorCounter.increment();
                throw e;
            }
        });
//        ConversationEntity conversation = conversationRepository
//                .findById(conversationId)
//                .orElseThrow(() -> new IllegalArgumentException("Conversation not found"));
//        ChatMessageEntity userMessage = ChatMessageEntity.builder()
//                .role(Role.USER)
//                .content(prompt)
//                .build();
//        conversation.getMessages().add(userMessage);
//        userMessage.setConversation(conversation);
//        conversation.setUpdatedAt(Instant.now());
//        conversationRepository.save(conversation);
//
//        callLlmAndPersistReply(conversation, prompt);
//        return conversation;
    }

    @Transactional
    public boolean deleteConversation(Long conversationId) {
        deleteCounter.increment();
        return deleteTimer.record(() -> {
            try {
                if (!conversationRepository.existsById(conversationId)) {
                    return false;
                }
                conversationRepository.deleteById(conversationId);
                return true;
            } catch (Exception e) {
                deleteErrorCounter.increment();
                throw e;
            }
        });
//        if (!conversationRepository.existsById(conversationId)) {
//            return false;
//        }
//        conversationRepository.deleteById(conversationId);
//        return true;
    }

    @Transactional(readOnly = true)
    public List<ConversationDTO> getConversationHistory(Long userId) {
        historyCounter.increment();
        return historyTimer.record(() -> {
            try {
                if (!userRepository.existsById(userId)) {
                    throw new IllegalArgumentException("User not found");
                }
                List<ConversationDTO> conversationDTOList = conversationRepository
                        .findByUserIdOrderByUpdatedAtDesc(userId);
                if (conversationDTOList.isEmpty()) {
                    throw new IllegalArgumentException("No conversations found for this user");
                }
                return conversationDTOList;
            } catch (Exception e) {
                historyErrorCounter.increment();
                throw e;
            }
        });
//        if (!userRepository.existsById(userId)) {
//            throw new IllegalArgumentException("User not found");
//        }
//        List<ConversationDTO> conversationDTOList = conversationRepository
//                .findByUserIdOrderByUpdatedAtDesc(userId);
//        if (conversationDTOList.isEmpty()) {
//            throw new IllegalArgumentException("No conversations found for this user");
//        }
//        return conversationDTOList;
    }

    @Transactional(readOnly = true)
    public List<ConversationDTO> getConversationHistoryByEmail(String email) {
        historyCounter.increment();
        return historyTimer.record(() -> {
            try {
                UserEntity user = userRepository.findByEmail(email);
                if (user == null) {
                    throw new IllegalArgumentException("User not found");
                }
                Long userId = user.getId();
                return conversationRepository
                        .findByUserIdOrderByUpdatedAtDesc(userId);
            } catch (Exception e) {
                historyErrorCounter.increment();
                throw e;
            }
        });
//        UserEntity user = userRepository.findByEmail(email);
//        if (user == null) {
//            throw new IllegalArgumentException("User not found");
//        }
//        Long userId = user.getId();
//        return conversationRepository
//                .findByUserIdOrderByUpdatedAtDesc(userId);
    }

    private String callLlmAndPersistReply(ConversationEntity conversation, String prompt) {
        return llmCallTimer.record(() -> {
            try {
                String llmResponse = llmClient.generateResponse(prompt);

                ChatMessageEntity llmMessage = ChatMessageEntity.builder()
                        .role(Role.SYSTEM)
                        .content(llmResponse)
                        .build();
                llmMessage.setConversation(conversation);
                conversation.getMessages().add(llmMessage);

                conversation.setUpdatedAt(Instant.now());
                conversationRepository.save(conversation);

                return llmResponse;
            } catch (Exception e) {
                llmErrorCounter.increment();
                throw e;
            }
        });
//        String llmResponse = llmClient.generateResponse(prompt);
//
//        ChatMessageEntity llmMessage = ChatMessageEntity.builder()
//                .role(Role.SYSTEM)
//                .content(llmResponse)
//                .build();
//        llmMessage.setConversation(conversation);
//        conversation.getMessages().add(llmMessage);
//
//        conversation.setUpdatedAt(Instant.now());
//        conversationRepository.save(conversation);
//
//        return llmResponse;
    }

    private String extractTitle(String llmText) {
        String[] lines = llmText.split("\n", 2);
        return lines[0].length() > 50
                ? lines[0].substring(0, 47) + "..."
                : lines[0];
    }

}
