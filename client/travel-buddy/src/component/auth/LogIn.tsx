import {
    Alert,
    Box,
    Button,
    Container,
    TextField,
    Typography,
    Checkbox,
    FormControlLabel
} from "@mui/material";
import useAuth from "../../hooks/useAuth";
import {useLocation, useNavigate} from "react-router-dom";
import React, {FormEvent, useEffect, useRef, useState} from "react";
import { jwtDecode } from "jwt-decode";
import {sendLogin} from "../../api/auth";

const Login: React.FC = () => {
    const {setAuth, persist, setPersist} = useAuth();

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

    useEffect(() => {
        localStorage.setItem("persist", JSON.stringify(persist));
    }, [persist]);

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const {
                access_token: accessToken,
                refresh_token: refreshToken
            } = await sendLogin({ email: email, password: pwd });

            const decoded: { sub: string; roles: string[] } = jwtDecode(accessToken);

            setAuth({
                user: decoded.sub,
                roles: decoded.roles,
                accessToken,
                refreshToken
            });

            if (persist) {
                localStorage.setItem("refreshToken", refreshToken);
            } else {
                localStorage.removeItem("refreshToken");
            }

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

                <FormControlLabel
                    control={
                        <Checkbox
                            checked={persist}
                            onChange={(e) => setPersist(e.target.checked)}
                            color="primary"
                        />
                    }
                    label="Keep me signed in"
                />

                <Button type="submit" variant="contained" size="large" fullWidth>
                    Sign In
                </Button>
            </Box>
        </Container>
    );
};

export default Login;
