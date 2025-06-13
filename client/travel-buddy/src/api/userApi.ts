import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { ConversationEntity } from '../component/consult/ConversationEntity';

export const useUserApi = () => {
    const { axiosUser } = useAxiosPrivate();

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
        // 可以继续添加其他方法...
    };
};
