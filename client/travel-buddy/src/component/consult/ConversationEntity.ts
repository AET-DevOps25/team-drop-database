export interface ChatMessageEntity {
    messageId: number;
    content: string;
    sender: string;
    createdAt: string;
}

export interface ConversationEntity {
    conversationId: number;
    userId: number;
    title: string | null;
    createdAt: string;
    updatedAt: string;
    messages: ChatMessageEntity[];
}
