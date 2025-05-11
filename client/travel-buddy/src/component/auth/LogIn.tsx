import {Alert, Box, Button, Container, Link, TextField, Typography} from "@mui/material";
import useAuth from "../../hooks/useAuth";
import {useLocation, useNavigate} from "react-router-dom";
import {FormEvent, useEffect, useRef, useState} from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

interface LoginResponse {
    access_token: string;
    refresh_token: string;
}

const Login: React.FC = () => {
    const {setAuth} = useAuth();

    const navigate = useNavigate();
    const location = useLocation();
    const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

    const userRef = useRef<HTMLInputElement>(null);
    const errRef = useRef<HTMLDivElement>(null);

    const [email, setEmail] = useState<string>('');
    const [pwd, setPwd] = useState<string>('');
    const [errMsg, setErrMsg] = useState<string>('');

    useEffect(() => {
        userRef.current?.focus();
    }, []);

    useEffect(() => {
        setErrMsg('');
    }, [email, pwd]);

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const {data} = await axios.post<LoginResponse>(
                "http://localhost:8080/api/v1/auth/authenticate",
                JSON.stringify({
                    email: email,
                    password: pwd
                }),
                {
                    headers: {'Content-Type': 'application/json'},
                    withCredentials: true
                }
            );
            const {
                access_token: accessToken,
                refresh_token: refreshToken
            } = data;

            const decoded: { sub: string; roles: string[] } = jwtDecode(accessToken);

            setAuth({
                user: decoded.sub,
                roles: decoded.roles,
                accessToken
            })

            setEmail('');
            setPwd('');
            navigate(from, {replace: true});
        } catch (err: any) {
            if (!err?.response) {
                setErrMsg('No Server Response');
            } else if (err.response?.status === 400) {
                setErrMsg('Missing Username or Password');
            } else if (err.response?.status === 401) {
                setErrMsg('Unauthorized');
            } else {
                setErrMsg('Login Failed');
            }
            errRef.current?.focus();
        }
    };

    return (
        <Container maxWidth="xs">
            <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{
                    mt: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2
                }}
            >
                <Typography variant="h4" component="h1" align="center">
                    Sign In
                </Typography>

                {errMsg && (
                    <Alert severity="error" ref={errRef} tabIndex={-1}>
                        {errMsg}
                    </Alert>
                )}

                <TextField
                    id="username"
                    label="Username"
                    inputRef={userRef}
                    autoComplete="username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    fullWidth
                />

                <TextField
                    id="password"
                    label="Password"
                    type="password"
                    autoComplete="current-password"
                    value={pwd}
                    onChange={(e) => setPwd(e.target.value)}
                    required
                    fullWidth
                />

                <Button type="submit" variant="contained" size="large" fullWidth>
                    Sign In
                </Button>
            </Box>
        </Container>
    );
};

export default Login;