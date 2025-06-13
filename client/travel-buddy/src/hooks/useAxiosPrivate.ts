import { useEffect } from 'react';
import { axiosAuth, axiosAttr, axiosUser } from '../api/axios';
import setupInterceptors from './setupInterceptors';
import useAuth from './useAuth';
import useRefreshToken from './useRefreshToken';

const useAxiosPrivate = () => {
    const { auth } = useAuth();
    const refresh = useRefreshToken();

    useEffect(() => {
        const getToken = () => auth?.accessToken ?? null;

        const ejectors = [
            // setupInterceptors(axiosAuth, refresh, getToken),
            // setupInterceptors(axiosAttr, refresh, getToken),
            setupInterceptors(axiosUser, refresh, getToken),
        ];

        return () => {
            ejectors.forEach(eject => eject());
        };
    }, [auth, refresh]);

    return {
        axiosAuth,
        axiosAttr,
        axiosUser,
    };
};

export default useAxiosPrivate;
