import {createContext, useState, ReactNode} from "react";

interface AuthProviderProps {
    children: ReactNode;
}

interface AuthContextType {
    auth: AuthData | null;
    setAuth: React.Dispatch<React.SetStateAction<AuthData | null>>;
}

interface AuthData {
    user?: string;
    accessToken?: string;
    roles?: string[];
}

const AuthContext = createContext<AuthContextType>({
    auth: null,
    setAuth: () => {}
});

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [auth, setAuth] = useState<AuthData | null>(null);

    return (
        <AuthContext.Provider value={{ auth, setAuth }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;