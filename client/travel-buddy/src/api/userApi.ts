import useAxiosPrivate from '../hooks/useAxiosPrivate';
import {User} from "../dto/User";

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

    const getUserProfileByEmail = async (email: string): Promise<User> => {
        const { data } = await axiosUser.get<User>(
            `/profiles/email/${email}`,
            {
                headers: {'Content-Type': 'application/json'},
            }
        );
        return data;
    }

    const createUserProfile = async (user: User): Promise<User> => {
        const { data } = await axiosUser.post<User>(
            '/profiles',
            JSON.stringify(user),
            {
                headers: {'Content-Type': 'application/json'},
            }
        )
        return data;
    }

    return {
        createUserProfile,
        pingUserServer,
        getUserProfileByEmail,
    };
};
