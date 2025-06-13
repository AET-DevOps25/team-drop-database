import { AxiosInstance, AxiosRequestConfig, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { AxiosHeaders } from 'axios';

type RefreshTokenFn = () => Promise<string>;
type GetTokenFn = () => string | null;

const setupInterceptors = (
    axiosInstance: AxiosInstance,
    refreshToken: RefreshTokenFn,
    getAccessToken: GetTokenFn
): (() => void) => {
    const requestIntercept = axiosInstance.interceptors.request.use(
        (config: InternalAxiosRequestConfig) => {
            if (!config.headers) {
                config.headers = new AxiosHeaders();
            }

            if (!config.headers.has('Authorization')) {
                const token = getAccessToken();
                if (token) {
                    config.headers.set('Authorization', `Bearer ${token}`);
                }
            }

            return config;
        },
        (error: AxiosError) => Promise.reject(error)
    );

    const responseIntercept = axiosInstance.interceptors.response.use(
        (response) => response,
        async (error: AxiosError) => {
            const originalRequest = error.config as AxiosRequestConfig & { sent?: boolean };

            if (error?.response?.status === 403 && !originalRequest?.sent) {
                originalRequest.sent = true;
                const newAccessToken = await refreshToken();

                if (originalRequest.headers) {
                    originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
                }

                return axiosInstance(originalRequest);
            }

            return Promise.reject(error);
        }
    );

    return () => {
        axiosInstance.interceptors.request.eject(requestIntercept);
        axiosInstance.interceptors.response.eject(responseIntercept);
    };
};

export default setupInterceptors;
