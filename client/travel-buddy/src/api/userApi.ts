import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { ConversationEntity } from '../dto/ConversationEntity';
import {UserEntity} from "../dto/UserEntity";
import {ConversationDTO} from "../dto/ConversationDTO";

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

    const getUserProfileByEmail = async (email: string): Promise<UserEntity> => {
        const { data } = await axiosUser.get<UserEntity>(
            `/profiles/email/${email}`,
            {
                headers: {'Content-Type': 'application/json'},
            }
        );
        return data;
    }

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

    const getConversationHistory = async (userId: number): Promise<ConversationDTO[]> => {
        const { data } = await axiosUser.get<ConversationDTO[]>(
            `/conversation/h/${userId}`,
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        return data;
    };

    return {
        createConversation,
        createUserProfile,
        pingUserServer,
        getUserProfileByEmail,
        getConversationHistory
    };
};
