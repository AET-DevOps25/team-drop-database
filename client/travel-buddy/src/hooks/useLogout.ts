import axios from "../api/axios";
import useAuth from "./useAuth";

const useLogout = (): (() => Promise<void>) => {
    const { setAuth } = useAuth();

    const logout = async (): Promise<void> => {
        setAuth({});
        try {
            await axios('/api/v1/auth/logout', {
                withCredentials: true,
            });
        } catch (err) {
            console.error(err);
        }
    };

    return logout;
};

export default useLogout;
