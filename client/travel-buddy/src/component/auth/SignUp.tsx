import {
    Alert,
    Box,
    Button,
    Container,
    TextField,
    Typography
} from "@mui/material";
import { useState, useRef, useEffect, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { sendSignUp } from "../../api/auth";
import {UserEntity} from "../../dto/UserEntity";
import {useUserApi} from "../../api/userApi";
import {jwtDecode} from "jwt-decode";
import useAuth from "../../hooks/useAuth";

const Signup: React.FC = () => {
    const navigate = useNavigate();

    const { createUserProfile } = useUserApi();
    const {setAuth, auth} = useAuth();

    const emailRef = useRef<HTMLInputElement>(null);
    const errRef = useRef<HTMLDivElement>(null);

    const [email, setEmail] = useState('');
    const [pwd, setPwd] = useState('');
    const [confirmPwd, setConfirmPwd] = useState('');
    const [errMsg, setErrMsg] = useState('');

    const [pendingProfile, setPendingProfile] = useState<UserEntity | null>(null);

    useEffect(() => {
        emailRef.current?.focus();
    }, []);

    useEffect(() => {
        setErrMsg('');
    }, [email, pwd, confirmPwd]);

    useEffect(() => {
        if (!pendingProfile || !auth?.accessToken) return;

        let cancelled = false;

        (async () => {
            try {
                await createUserProfile(pendingProfile);
                if (!cancelled) navigate("/consult");
            } catch (err: any) {
                if (cancelled) return;

                if (!err?.response) {
                    setErrMsg("No User Server Response");
                } else if (err.response?.status === 403) {
                    setErrMsg("Not Authorized to Create User Profile");
                } else {
                    setErrMsg("Creating User Profile Failed");
                }
                errRef.current?.focus();
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [pendingProfile, auth, createUserProfile, navigate]);

    const isValid = email && pwd && confirmPwd && pwd === confirmPwd;

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            const {
                access_token: accessToken,
                refresh_token: refreshToken
            } = await sendSignUp({ email: email, password: pwd, role: "USER" });

            const decoded: { sub: string; roles: string[] } = jwtDecode(accessToken);

            setAuth({
                user: decoded.sub,
                roles: decoded.roles,
                accessToken,
                refreshToken
            });

            localStorage.setItem("refreshToken", refreshToken);
            localStorage.setItem("persist", "true");

            setEmail('');
            setPwd('');
            setConfirmPwd('');
        } catch (err: any) {
            if (!err?.response) {
                setErrMsg('No Auth Server Response');
            } else if (err.response?.status === 400) {
                setErrMsg('Email Already Registered');
            } else {
                setErrMsg('Signup Failed');
            }
            errRef.current?.focus();
        }

        const user: UserEntity = {
            id: null,
            email: email,
            firstName: "",
            lastName: "",
            profilePicture: "",
            preference: ""
        }

        setPendingProfile(user);
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
                    Sign Up
                </Typography>

                {errMsg && (
                    <Alert severity="error" ref={errRef} tabIndex={-1}>
                        {errMsg}
                    </Alert>
                )}

                <TextField
                    id="email"
                    label="Email"
                    inputRef={emailRef}
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    fullWidth
                />

                <TextField
                    id="password"
                    label="Password"
                    type="password"
                    value={pwd}
                    onChange={(e) => setPwd(e.target.value)}
                    required
                    fullWidth
                />

                <TextField
                    id="confirm-password"
                    label="Confirm Password"
                    type="password"
                    value={confirmPwd}
                    onChange={(e) => setConfirmPwd(e.target.value)}
                    required
                    fullWidth
                    error={confirmPwd !== '' && confirmPwd !== pwd}
                    helperText={
                        confirmPwd !== '' && confirmPwd !== pwd
                            ? "Passwords do not match"
                            : ''
                    }
                />

                <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={!isValid}
                >
                    Sign Up
                </Button>
            </Box>
        </Container>
    );
};

export default Signup;
