import {ChatMessage} from "./ChatMessage";

export interface Conversation {
    conversationId: number;
    userId: number;
    title: string | null;
    createdAt: string;
    updatedAt: string;
    messages: ChatMessage[];
}
