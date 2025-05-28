import useAuth from './useAuth';
import {jwtDecode} from "jwt-decode";
import {sendRefresh} from "../api/auth";

const useRefreshToken = () => {
    const {auth, setAuth, persist} = useAuth();

    const refresh = async () => {
        const rt = auth?.refreshToken || localStorage.getItem("refreshToken");
        if (!rt) throw new Error("No refresh-token available");

        const {access_token, refresh_token} = await sendRefresh(rt);

        setAuth(prev => {
            console.log(JSON.stringify(prev));
            console.log(access_token);
            const decoded: { sub: string; roles: string[] } = jwtDecode(access_token);
            return {
                ...prev,
                roles: decoded.roles,
                accessToken: access_token,
            }
        });

        if (persist) localStorage.setItem("refreshToken", refresh_token);

        return access_token;
    }
    return refresh;
};

export default useRefreshToken;