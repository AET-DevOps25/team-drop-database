import { Outlet } from "react-router-dom";
import React, { useState, useEffect } from "react";
import useRefreshToken from "../../hooks/useRefreshToken";
import useAuth from "../../hooks/useAuth";
import useLocalStorage from "../../hooks/useLocalStorage";

const PersistLogin: React.FC = () => {
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const refresh = useRefreshToken();
    const { auth } = useAuth();
    const [persist] = useLocalStorage<boolean>('persist', false);

    useEffect(() => {
        let isMounted = true;

        const verifyRefreshToken = async () => {
            try {
                await refresh();
            } catch (err) {
                console.error(err);
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        };

        if (!auth?.accessToken && persist) {
            verifyRefreshToken();
        } else {
            setIsLoading(false);
        }

        return () => {
            isMounted = false;
        };
    }, [auth?.accessToken, persist, refresh]);

    return (
        <>
            {!persist ? (
                <Outlet />
            ) : isLoading ? (
                <p>Loading...</p>
            ) : (
                <Outlet />
            )}
        </>
    );
};

export default PersistLogin;
