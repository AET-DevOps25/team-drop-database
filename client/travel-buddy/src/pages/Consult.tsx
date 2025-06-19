import React, { useEffect, useState } from 'react';
import {
    Box,
    IconButton,
    Toolbar,
    useMediaQuery,
    useTheme
} from '@mui/material';
import Sidebar from '../component/consult/Sidebar';
import InputBar from '../component/consult/InputBar';
import useAuth from '../hooks/useAuth';
import { useUserApi } from '../api/userApi';
import { ConversationDTO } from '../dto/ConversationDTO';
import HistoryIcon from '@mui/icons-material/History';
import ChatMessage from "../component/consult/ChatMessage";

const Consult: React.FC = () => {
    const { auth } = useAuth();
    const { getConversationHistoryByEmail } = useUserApi();
    const [conversations, setConversations] = useState<ConversationDTO[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

    const toggleSidebar = () => setSidebarOpen((prev) => !prev);

    const messages = [
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
        { sender: 'user', content: '我想去意大利旅游5天' },
        { sender: 'system', content: '推荐你参观罗马、佛罗伦萨和威尼斯。' },
    ];

    useEffect(() => {
        const fetchConversations = async () => {
            if (auth?.user != null) {
                try {
                    const history = await getConversationHistoryByEmail(auth.user);
                    const sorted = history.sort(
                        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
                    );
                    setConversations(sorted);
                    if (sorted.length > 0) {
                        setActiveId(sorted[0].id.toString());
                    }
                } catch (error) {
                    console.error('Failed to fetch conversation history:', error);
                }
            }
        };
        fetchConversations();
    }, []);

    return (
        <Box sx={{ display: 'flex' }}>
            {/* Sidebar */}
            <Sidebar
                conversations={conversations.map(c => ({ id: c.id.toString(), title: c.title }))}
                activeId={activeId ?? ''}
                onSelect={setActiveId}
                mobileOpen={sidebarOpen}
                onCloseMobile={() => setSidebarOpen(false)}
            />

            {/* Main Content */}
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100vh',
                    maxWidth: '900px',
                    margin: '0 auto',
                    width: '100%'
                }}
            >

                <Box
                    sx={{
                        flexGrow: 1,
                        overflowY: 'auto',
                        px: 2,
                        pt: 2,
                    }}
                >
                    {messages.map((msg, idx) => (
                        <ChatMessage key={idx} sender={msg.sender as 'user' | 'system'} content={msg.content} />
                    ))}
                </Box>

                {/* Input row */}
                <Box
                    sx={{
                        borderTop: '1px solid #ccc',
                        px: isMobile ? 1 : 2,
                        py: 1,
                        bgcolor: 'background.paper',
                        position: 'sticky',
                        bottom: 20,
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {isMobile && (
                            <IconButton
                                onClick={toggleSidebar}
                                sx={{
                                    height: 48,
                                    width: 48,
                                    mt: '20px'
                                }}
                            >
                                <HistoryIcon />
                            </IconButton>
                        )}
                        <Box sx={{ flexGrow: 1 }}>
                            <InputBar email={auth?.user || ''} />
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default Consult;
