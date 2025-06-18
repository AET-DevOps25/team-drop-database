import useAxiosPrivate from '../hooks/useAxiosPrivate';
import { ConversationEntity } from '../dto/ConversationEntity';
import {UserEntity} from "../dto/UserEntity";
import {ConversationDTO} from "../dto/ConversationDTO";
import {PromptDTO} from "../dto/PromptDTO";

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

    const createConversationByEmail = async (
        email: string,
        prompt: PromptDTO
    ): Promise<ConversationEntity> => {
        const { data } = await axiosUser.post<ConversationEntity>(
            `/conversations/email/${email}`,
            prompt,
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        return data;
    };

    const getConversationHistoryByEmail = async (email: string): Promise<ConversationDTO[]> => {
        const { data } = await axiosUser.get<ConversationDTO[]>(
            `/conversations/h/email/${email}`,
            {
                headers: { 'Content-Type': 'application/json' },
            }
        );
        return data;
    };

    return {
        createConversationByEmail,
        createUserProfile,
        pingUserServer,
        getUserProfileByEmail,
        getConversationHistoryByEmail
    };
};
