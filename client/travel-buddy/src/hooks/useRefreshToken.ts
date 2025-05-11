import axios from '../api/axios';
import useAuth from './useAuth';
import {jwtDecode} from "jwt-decode";

const useRefreshToken = () => {
    const {auth, setAuth, persist} = useAuth();

    const refresh = async () => {
        const rt = auth?.refreshToken || localStorage.getItem("refreshToken");
        if (!rt) throw new Error("No refresh-token available");

        const response = await axios.post(
            "/api/v1/auth/refresh-token",
            {},
            {headers: { Authorization: `Bearer ${rt}` }}
        );

        setAuth(prev => {
            console.log(JSON.stringify(prev));
            console.log(response.data.access_token);
            const decoded: { sub: string; roles: string[] } = jwtDecode(response.data.access_token);
            return {
                ...prev,
                roles: decoded.roles,
                accessToken: response.data.access_token,
            }
        });

        if (persist) localStorage.setItem("refreshToken", response.data.refresh_token);

        return response.data.accessToken;
    }
    return refresh;
};

export default useRefreshToken;