import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { ConversationEntity } from '../component/consult/ConversationEntity';

export const useUserApi = () => {
    const { axiosUser } = useAxiosPrivate();

    const pingUserServer = async (): Promise<boolean> => {
        try {
            const response = await axiosUser.get('/connection/user-ping');
            return response.status === 200;
        } catch (error) {
            return false;
        }
    };

    const createConversation = async (
        userId: number,
        prompt: string
    ): Promise<ConversationEntity> => {
        const { data } = await axiosUser.post<ConversationEntity>(
            `/conversation/${userId}`,
            prompt,
            {
                headers: {
                    'Content-Type': 'text/plain',
                },
            }
        );
        return data;
    };

    return {
        createConversation,
        pingUserServer
    };
};
