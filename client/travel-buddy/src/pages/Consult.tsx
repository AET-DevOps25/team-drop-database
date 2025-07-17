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
import {ConversationHistory} from '../dto/conversation/ConversationHistory';
import HistoryIcon from '@mui/icons-material/History';
import {useNavigate, useParams} from "react-router-dom";
import {ChatMessage} from "../dto/conversation/ChatMessage";
import ChatMessageRow from "../component/consult/ChatMessageRow";
import {Conversation} from "../dto/conversation/Conversation";

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
                // created new conversation if missing
                conv = await createConversationByEmail(auth.user, {prompt: text});
                setActiveId(String(conv.conversationId));
                navigate(`/consult/${conv.conversationId}`);
            } else {
                // continued new conversation if present
                conv = await resumeConversation(Number(activeId), {prompt: text});

            }
            setMessages(conv.messages);
            await refreshHistory();

            // get last message id for polling
            const lastUserMsg = conv.messages[conv.messages.length - 1];
            setAwaitingMsgId(lastUserMsg.messageId);
            startPolling(conv.conversationId, lastUserMsg.messageId);

        } catch (e) {
            console.error(e);
            // TODO: add a snackbar for this
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
            console.error('Failed to refresh sidebar:', err);
        }
    }, [auth?.user, getConversationHistoryByEmail, activeId]);

    const startPolling = (convId: number, userMsgId: number) => {
        // avoid concurrent polling
        if (timerRef.current) clearInterval(timerRef.current);

        timerRef.current = setInterval(async () => {
            try {
                const conv = await getConversation(convId);
                const latest = conv.messages[conv.messages.length - 1];

                // stop polling if hits a system response
                if (latest.role !== "USER" && latest.messageId > userMsgId) {
                    clearInterval(timerRef.current!);
                    timerRef.current = null;
                    setMessages(conv.messages);
                    setAwaitingMsgId(null);
                }
            } catch (e) {
                console.error('Failed to poll response:', e);
            }
        }, 2500);
    };

    useEffect(() => {
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, []);

    useEffect(() => {
        // stop old polling if switch to new conversation
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
                console.error('Failed to load conversation', e);
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
                        flexGrow: 1,
                        overflowY: 'auto',
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
