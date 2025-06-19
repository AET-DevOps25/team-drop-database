import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { Conversation } from '../dto/conversation/Conversation';
import {ConversationHistory} from "../dto/conversation/ConversationHistory";
import {Prompt} from "../dto/conversation/Prompt";

export const useConversationApi = () => {
    const { axiosUser } = useAxiosPrivate();

    const createConversationByEmail = async (
        email: string,
        prompt: Prompt
    ): Promise<Conversation> => {
        const { data } = await axiosUser.post<Conversation>(
            `/conversations/email/${email}`,
            prompt,
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        return data;
    };

    const getConversation = async (conversationId: number): Promise<Conversation> => {
        const { data } = await axiosUser.get(
            `/conversations/${conversationId}`,
        );
        return data;
    }

    const resumeConversation = async (
        conversationId: number,
        prompt: Prompt
    ): Promise<Conversation> => {
        const { data } = await axiosUser.put<Conversation>(
            `/conversations/${conversationId}`,
            prompt,
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        return data;
    };

    const getConversationHistoryByEmail = async (email: string): Promise<ConversationHistory[]> => {
        const { data } = await axiosUser.get<ConversationHistory[]>(
            `/conversations/h/email/${email}`,
        );
        return data;
    };

    return {
        createConversationByEmail,
        getConversationHistoryByEmail,
        getConversation,
        resumeConversation
    };
};
