import {axiosAuth} from "./axios";
import exp from "node:constants";

interface LoginRequest {
    email: string;
    password: string;
}

interface LoginResponse {
    access_token: string;
    refresh_token: string;
}

export const sendLogin = async (
    credentials: LoginRequest,
): Promise<LoginResponse> => {
    const {data} = await axiosAuth.post<LoginResponse>(
        '/auth/authenticate',
        JSON.stringify(credentials),
        {
            headers: {'Content-Type': 'application/json'},
            withCredentials: true
        }
    );
    return data;
};

export const sendLogout = async (): Promise<void> => {
    await axiosAuth.post(
        '/auth/logout',
        {},
        {
            withCredentials: true,
        }
    );
}

export const sendRefresh = async (refreshToken: string): Promise<LoginResponse> => {
    const {data} = await axiosAuth.post(
        '/api/v1/auth/refresh-token',
        {},
        {
            headers: {Authorization: `Bearer ${refreshToken}`}
        }
    )
    return data;
}