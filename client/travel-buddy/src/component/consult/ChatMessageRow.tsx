import React from 'react';
import { Box, Avatar, Typography, Paper } from '@mui/material';

interface ChatMessageProps {
    sender: 'USER' | 'SYSTEM';
    content: string;
}

const ChatMessageRow: React.FC<ChatMessageProps> = ({ sender, content }) => {
    const isUser = sender === 'USER';

    return (
        <Box
            display="flex"
            justifyContent={isUser ? 'flex-end' : 'flex-start'}
            alignItems="flex-end"
            mb={2}
        >
            {!isUser && (
                <Avatar sx={{ mr: 1 }}>AI</Avatar>
            )}

            <Paper
                elevation={3}
                sx={{
                    p: 1.5,
                    maxWidth: '75%',
                    bgcolor: isUser ? 'primary.main' : 'grey.100',
                    color: isUser ? 'white' : 'black',
                    borderRadius: 2,
                }}
            >
                <Typography variant="body1">{content}</Typography>
            </Paper>

        </Box>
    );
};

export default ChatMessageRow;
