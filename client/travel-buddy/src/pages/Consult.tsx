import React, {useEffect, useRef, useState} from 'react';
import {
    Box,
    IconButton,
    useMediaQuery,
    useTheme
} from '@mui/material';
import Sidebar from '../component/consult/Sidebar';
import InputBar from '../component/consult/InputBar';
import useAuth from '../hooks/useAuth';
import {useConversationApi} from '../api/conversationApi';
import {ConversationHistory} from '../dto/ConversationHistory';
import HistoryIcon from '@mui/icons-material/History';
import {useNavigate, useParams} from "react-router-dom";
import {ChatMessage} from "../dto/ChatMessage";
import ChatMessageRow from "../component/consult/ChatMessageRow";
import {Conversation} from "../dto/Conversation";

const Consult: React.FC = () => {
    const {conversationId} = useParams<{ conversationId?: string }>();

    const {auth} = useAuth();
    const navigate = useNavigate();
    const {
        createConversationByEmail,
        resumeConversation,
        getConversation
    } = useConversationApi();

    const {getConversationHistoryByEmail} = useConversationApi();

    // State for conversation history for sidebar
    const [conversations, setConversations] = useState<ConversationHistory[]>([]);

    // State for active conversation ID
    const [activeId, setActiveId] = useState<string | null>(conversationId ?? null);

    // State for chat messages
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(false);

    // State for message polling
    const [awaitingMsgId, setAwaitingMsgId] = useState<number | null>(null);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

    const toggleSidebar = () => setSidebarOpen((prev) => !prev);
    const handleSelect = (id: string) => {
        setActiveId(id);
        navigate(`/consult/${id}`, {replace: false});
    };

    // sending message logic for input bar
    const handleSend = async (text: string) => {
        if (!auth?.user) return;

        setLoading(true);

        try {
            let conv: Conversation;
            if (!activeId) {
                // 没有会话 → 创建
                conv = await createConversationByEmail(auth.user, {prompt: text});
                setActiveId(String(conv.conversationId));
                navigate(`/consult/${conv.conversationId}`);
            } else {
                // 已有会话 → 追加
                conv = await resumeConversation(Number(activeId), {prompt: text});

            }
            setMessages(conv.messages);
            await refreshHistory(); // 新建成功 → 侧边栏重新拉，继续对话 → 最新排序

            // 获取最后一条用户消息 ID，用于后续轮询
            const lastUserMsg = conv.messages[conv.messages.length - 1];
            setAwaitingMsgId(lastUserMsg.messageId);
            startPolling(conv.conversationId, lastUserMsg.messageId);

        } catch (e) {
            console.error(e);
            // TODO: 做一个发送失败的snackbar
        } finally {
            setLoading(false);
        }
    };

    const refreshHistory = React.useCallback(async () => {
        if (!auth?.user) return;
        try {
            const history = await getConversationHistoryByEmail(auth.user);
            const sorted = history.sort(
                (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
            );
            setConversations(sorted);

        } catch (err) {
            console.error('刷新侧边栏失败:', err);
        }
    }, [auth?.user, getConversationHistoryByEmail, activeId]);

    const startPolling = (convId: number, userMsgId: number) => {
        // 避免并发轮询
        if (timerRef.current) clearInterval(timerRef.current);

        timerRef.current = setInterval(async () => {
            try {
                const conv = await getConversation(convId);
                const latest = conv.messages[conv.messages.length - 1];

                // 找到系统回复 → 停止轮询
                if (latest.role !== "USER" && latest.messageId > userMsgId) {
                    clearInterval(timerRef.current!);
                    timerRef.current = null;
                    setMessages(conv.messages);
                    setAwaitingMsgId(null);
                }
            } catch (e) {
                console.error('轮询失败:', e);
            }
        }, 2500);
    };

    useEffect(() => {
        // 当组件卸载或切换会话时，确保停止旧轮询
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, []);

    useEffect(() => {
        // 切换到新会话时，若仍在等待旧会话回复，则清掉旧轮询
        if (timerRef.current && awaitingMsgId === null) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, [activeId]);

    useEffect(() => { refreshHistory(); }, [refreshHistory]);

    useEffect(() => {
        if (conversationId && conversationId !== activeId) {
            setActiveId(conversationId);
        }
    }, [conversationId]);

    useEffect(() => {
        if (!activeId) return;
        (async () => {
            try {
                const conv = await getConversation(Number(activeId));
                setMessages(conv.messages);
            } catch (e) {
                console.error('加载会话失败', e);
            }
        })();
    }, [activeId]);

    return (
        <Box sx={{display: 'flex', height: '100vh'}}>
            {/* Sidebar */}
            <Sidebar
                conversations={conversations.map(c => ({id: c.id.toString(), title: c.title}))}
                activeId={activeId ?? ''}
                onSelect={handleSelect}
                mobileOpen={sidebarOpen}
                onCloseMobile={() => setSidebarOpen(false)}
            />

            {/* Main Content */}
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100vh',
                    maxWidth: 900,
                    mx: 'auto',
                    width: '100%',
                    p: 0
                }}
            >
                <Box
                    sx={{
                        px: 2,
                        pt: 2,
                    }}
                >
                    {messages.map(m => (
                        <ChatMessageRow
                            key={m.messageId}
                            sender={m.role}
                            content={m.content}
                        />
                    ))}
                </Box>

                {/* Input row */}
                <Box
                    sx={{
                        position: 'sticky',
                        bottom: 0,
                        py: 1,
                        px: isMobile ? 1 : 2,
                        bgcolor: 'background.paper',
                        zIndex: 10,
                    }}
                >
                    <Box sx={{display: 'flex', alignItems: 'center', gap: 1, paddingBottom: '20px'}}>
                        {isMobile && (
                            <IconButton
                                onClick={toggleSidebar}
                                sx={{
                                    height: 48,
                                    width: 48,
                                    mt: '20px'
                                }}
                            >
                                <HistoryIcon/>
                            </IconButton>
                        )}
                        <Box sx={{flexGrow: 1}}>
                            <InputBar onSend={handleSend} loading={loading}/>
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
};

export default Consult;
