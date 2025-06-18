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

const Consult: React.FC = () => {
    const { auth } = useAuth();
    const { getConversationHistoryByEmail } = useUserApi();
    const [conversations, setConversations] = useState<ConversationDTO[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

    const toggleSidebar = () => setSidebarOpen((prev) => !prev);

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
            <Box component="main" sx={{ flexGrow: 1, p: 2 }}>
                <Toolbar />

                {/* Input row */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        width: '100%',
                        mt: 2,
                        px: isMobile ? 1 : 0,
                    }}
                >
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
    );
};

export default Consult;
