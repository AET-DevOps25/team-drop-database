import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { reportMetric } from '../metricsReporter';
import { Conversation } from '../dto/conversation/Conversation';
import { ConversationHistory } from '../dto/conversation/ConversationHistory';
import { Prompt } from '../dto/conversation/Prompt';

export const useConversationApi = () => {
    const { axiosUser } = useAxiosPrivate();

    /**
     * Create a new conversation by email
     */
    const createConversationByEmail = async (
        email: string,
        prompt: Prompt
    ): Promise<Conversation> => {
        const metricBase = 'frontend_create_conversation_by_email';
        const endpoint = `/conversations/email/${email}`;
        const labels = { endpoint };
        const start = performance.now();
        try {
            const { data } = await axiosUser.post<Conversation>(
                endpoint,
                prompt,
                { headers: { 'Content-Type': 'application/json' } }
            );
            const duration = (performance.now() - start) / 1000;
            reportMetric({ name: `${metricBase}_duration_seconds`, labels, value: duration });
            return data;
        } catch (error) {
            reportMetric({ name: `${metricBase}_errors_total`, labels, value: 1 });
            throw error;
        }
    };

    /**
     * Fetch a specific conversation
     */
    const getConversation = async (
        conversationId: number
    ): Promise<Conversation> => {
        const metricBase = 'frontend_get_conversation';
        const endpoint = `/conversations/${conversationId}`;
        const labels = { endpoint };
        const start = performance.now();
        try {
            const { data } = await axiosUser.get<Conversation>(endpoint);
            const duration = (performance.now() - start) / 1000;
            reportMetric({ name: `${metricBase}_duration_seconds`, labels, value: duration });
            return data;
        } catch (error) {
            reportMetric({ name: `${metricBase}_errors_total`, labels, value: 1 });
            throw error;
        }
    };

    /**
     * Submit a user message to resume a conversation
     */
    const resumeConversation = async (
        conversationId: number,
        prompt: Prompt
    ): Promise<Conversation> => {
        const metricBase = 'frontend_resume_conversation';
        const endpoint = `/conversations/${conversationId}`;
        const labels = { endpoint };
        const start = performance.now();
        try {
            const { data } = await axiosUser.put<Conversation>(
                endpoint,
                prompt,
                { headers: { 'Content-Type': 'application/json' } }
            );
            const duration = (performance.now() - start) / 1000;
            reportMetric({ name: `${metricBase}_duration_seconds`, labels, value: duration });
            return data;
        } catch (error) {
            reportMetric({ name: `${metricBase}_errors_total`, labels, value: 1 });
            throw error;
        }
    };

    /**
     * Retrieve conversation history by user email
     */
    const getConversationHistoryByEmail = async (
        email: string
    ): Promise<ConversationHistory[]> => {
        const metricBase = 'frontend_get_conversation_history_by_email';
        const endpoint = `/conversations/h/email/${email}`;
        const labels = { endpoint };
        const start = performance.now();
        try {
            const { data } = await axiosUser.get<ConversationHistory[]>(endpoint);
            const duration = (performance.now() - start) / 1000;
            reportMetric({ name: `${metricBase}_duration_seconds`, labels, value: duration });
            return data;
        } catch (error) {
            reportMetric({ name: `${metricBase}_errors_total`, labels, value: 1 });
            throw error;
        }
    };

    return {
        createConversationByEmail,
        getConversation,
        resumeConversation,
        getConversationHistoryByEmail
    };
};
