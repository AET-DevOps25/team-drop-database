export interface ChatMessage {
    messageId: number;
    content: string;
    sender: 'USER' | 'SYSTEM';
    createdAt: string;
}