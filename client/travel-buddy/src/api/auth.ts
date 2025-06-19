import {axiosAuth} from "./axios";
import {LoginRequest} from "../dto/auth/LoginRequest";
import {LoginResponse} from "../dto/auth/LoginResponse";
import {SignUpRequest} from "../dto/auth/SignUpRequest";

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

export const sendSignUp = async (
    credentials: SignUpRequest,
): Promise<LoginResponse> => {
    const {data} = await axiosAuth.post<LoginResponse>(
        '/auth/register',
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
        '/auth/refresh-token',
        {},
        {
            headers: {Authorization: `Bearer ${refreshToken}`}
        }
    )
    return data;
}