import {axiosAuth} from "./axios";

interface LoginRequest {
    email: string;
    password: string;
}

interface LoginResponse {
    access_token: string;
    refresh_token: string;
}

export const login = async (
    credentials: LoginRequest,
): Promise<LoginResponse> => {
    const { data } = await axiosAuth.post<LoginResponse>(
        '/auth/authenticate',
        JSON.stringify(credentials),
    );
    return data;
};
