import {ChatMessageEntity} from "./ChatMessageEntity";

export interface ConversationEntity {
    conversationId: number;
    userId: number;
    title: string | null;
    createdAt: string;
    updatedAt: string;
    messages: ChatMessageEntity[];
}
