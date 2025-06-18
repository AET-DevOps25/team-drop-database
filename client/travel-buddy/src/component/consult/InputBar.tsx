import React, { useState } from "react";
import {
    IconButton,
    TextField,
    Paper,
    Box,
    Snackbar,
    Alert
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import { useUserApi } from "../../api/userApi";
import {PromptDTO} from "../../dto/PromptDTO";

interface ChatInputProps {
    email: string;
}

const ChatInput: React.FC<ChatInputProps> = ({ email }) => {
    const { createConversationByEmail } = useUserApi();
    const [inputValue, setInputValue] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [errorOpen, setErrorOpen] = useState<boolean>(false);

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(event.target.value);
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const trimmedPrompt = inputValue.trim();
        if (!trimmedPrompt) return;

        const prompt: PromptDTO = {
            prompt: trimmedPrompt
        };

        setLoading(true);
        try {
            const newConversation = await createConversationByEmail(email, prompt);
            setInputValue("");
        } catch (error) {
            setErrorOpen(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
                <Paper
                    component="form"
                    onSubmit={handleSubmit}
                    elevation={1}
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        padding: "8px",
                        borderRadius: "24px",
                        bgcolor: "#f5f5f5",
                        width: "100%",
                        maxWidth: 600,
                    }}
                >
                    <Box
                        sx={{
                            px: 1,
                            display: "flex",
                            alignItems: "flex-start",
                            justifyContent: "center",
                            pointerEvents: "none",
                            opacity: 0.3,
                            mt: 1,
                        }}
                    >
                        <QuestionAnswerIcon />
                    </Box>

                    <TextField
                        multiline
                        minRows={1}
                        maxRows={4}
                        placeholder="询问任何问题"
                        value={inputValue}
                        onChange={handleInputChange}
                        variant="standard"
                        InputProps={{
                            disableUnderline: true,
                        }}
                        sx={{ ml: 1, flex: 1 }}
                    />

                    <IconButton
                        type="submit"
                        color="primary"
                        disabled={!inputValue.trim() || loading}
                    >
                        <SendIcon />
                    </IconButton>
                </Paper>
            </Box>

            <Snackbar
                open={errorOpen}
                autoHideDuration={3000}
                onClose={() => setErrorOpen(false)}
                anchorOrigin={{ vertical: "top", horizontal: "right" }}
            >
                <Alert onClose={() => setErrorOpen(false)} severity="error" sx={{ width: "100%" }}>
                    发送失败，请稍后再试！
                </Alert>
            </Snackbar>
        </>
    );
};

export default ChatInput;
