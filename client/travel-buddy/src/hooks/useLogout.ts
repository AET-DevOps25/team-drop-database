import useAuth from "./useAuth";
import {sendLogout} from "../api/auth";

const useLogout = (): (() => Promise<void>) => {
    const { setAuth } = useAuth();

    const logout = async (): Promise<void> => {
        setAuth({});
        try {
            await sendLogout();
        } catch (err) {
            console.error(err);
        }
    };

    return logout;
};

export default useLogout;
