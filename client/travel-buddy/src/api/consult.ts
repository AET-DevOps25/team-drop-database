import {axiosUser} from './axios';
import {ConversationEntity} from "../component/consult/ConversationEntity";

export const createConversation = async (
    userId: number,
    prompt: string
): Promise<ConversationEntity> => {
    const {data} = await axiosUser.post<ConversationEntity>(
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
