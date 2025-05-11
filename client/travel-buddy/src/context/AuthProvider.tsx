import { createContext, useState, useEffect, ReactNode } from "react";

interface AuthProviderProps {
    children: ReactNode;
}

interface AuthData {
    user?: string;
    roles?: string[];
    accessToken?: string;
    refreshToken?: string;
}

interface AuthContextType {
    auth: AuthData | null;
    setAuth: React.Dispatch<React.SetStateAction<AuthData | null>>;
    persist: boolean;
    setPersist: React.Dispatch<React.SetStateAction<boolean>>;
}

const AuthContext = createContext<AuthContextType>({
    auth: null,
    setAuth: () => {},
    persist: false,
    setPersist: () => {},
});

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [auth, setAuth] = useState<AuthData | null>(() => {
        const rt = localStorage.getItem("refreshToken");
        return rt ? { refreshToken: rt } : null;
    });

    const [persist, setPersist] = useState<boolean>(() => {
        const stored = localStorage.getItem("persist");
        return stored ? (JSON.parse(stored) as boolean) : false;
    });

    useEffect(() => {
        localStorage.setItem("persist", JSON.stringify(persist));
    }, [persist]);

    return (
        <AuthContext.Provider value={{ auth, setAuth, persist, setPersist }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
