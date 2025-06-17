import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { ConversationEntity } from '../dto/ConversationEntity';
import {UserEntity} from "../dto/UserEntity";

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

    const createUserProfile = async (user: UserEntity): Promise<UserEntity> => {
        const { data } = await axiosUser.post<UserEntity>(
            '/profiles',
            JSON.stringify(user),
            {
                headers: {'Content-Type': 'application/json'},
            }
        )
        return data;
    }

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
        createUserProfile,
        pingUserServer
    };
};
