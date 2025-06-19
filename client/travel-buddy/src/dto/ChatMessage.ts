export interface ChatMessage {
    messageId: number;
    content: string;
    role: 'USER' | 'SYSTEM';
    createdAt: string;
}