// pages/Consult.tsx
import React, {useEffect, useState} from 'react';
import { Box, Toolbar } from '@mui/material';
import Sidebar from '../component/consult/Sidebar';
import InputBar from '../component/consult/InputBar';
import useAuth from "../hooks/useAuth";
import {useUserApi} from "../api/userApi";
import {ConversationDTO} from "../dto/ConversationDTO";

const Consult: React.FC = () => {
    const { auth } = useAuth();
    const { getConversationHistoryByEmail } = useUserApi();

    const [conversations, setConversations] = useState<ConversationDTO[]>([]);
    const [activeId, setActiveId] = useState<string | null>(null);

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
            {/* 左侧会话列表 */}
            <Sidebar
                conversations={conversations.map(c => ({ id: c.id.toString(), title: c.title }))}
                activeId={activeId ?? ''}
                onSelect={setActiveId}
                appBarOffset={64}
            />

            {/* 主内容区 */}
            <Box component="main" sx={{ flexGrow: 1, p: 2 }}>
                {/* 这行 Toolbar 把所有内容整体推到 AppBar 下方 */}
                <Toolbar />

                {/* 你原本的页面内容 */}
                <InputBar email={auth?.user || ""} />
            </Box>
        </Box>
    );
};

export default Consult;
