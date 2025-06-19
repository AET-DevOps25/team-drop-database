import React from "react";
import {
    Box,
    Divider,
    Drawer as MuiDrawer,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Typography,
    useMediaQuery,
    useTheme,
} from "@mui/material";
import { styled, Theme, CSSObject } from "@mui/material/styles";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";

const DRAWER_WIDTH = 260;
const COLLAPSE_WIDTH = 64;

const openedMixin = (theme: Theme): CSSObject => ({
    width: DRAWER_WIDTH,
    transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
    }),
    overflowX: "hidden",
});

const closedMixin = (theme: Theme): CSSObject => ({
    width: COLLAPSE_WIDTH,
    transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: "hidden",
});

const Drawer = styled(MuiDrawer, {
    shouldForwardProp: (prop) => prop !== "open",
})<{ open: boolean }>(({ theme, open }) => ({
    flexShrink: 0,
    whiteSpace: "nowrap",
    boxSizing: "border-box",
    ...(open && {
        ...openedMixin(theme),
        "& .MuiDrawer-paper": openedMixin(theme),
    }),
    ...(!open && {
        ...closedMixin(theme),
        "& .MuiDrawer-paper": closedMixin(theme),
    }),
}));

interface Conversation {
    id: string;
    title: string;
}

interface SidebarProps {
    conversations: Conversation[];
    activeId?: string;
    onSelect?: (id: string) => void;

    mobileOpen?: boolean;
    onCloseMobile?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
                                             conversations,
                                             activeId,
                                             onSelect,
                                             mobileOpen = false,
                                             onCloseMobile,
                                         }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const [open, setOpen] = React.useState<boolean>(true);

    const handleToggle = () => setOpen((prev) => !prev);

    const drawerContent = (
        <>
            {/* Header */}
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: open ? "space-between" : "center",
                    p: 1,
                    height: 56,
                }}
            >
                {open && (
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <ChatBubbleOutlineIcon fontSize="small" />
                        <Typography variant="subtitle1" fontWeight={600} noWrap>
                            Chat History
                        </Typography>
                    </Box>
                )}
                <IconButton onClick={handleToggle} size="small">
                    <MenuOpenIcon
                        sx={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
                    />
                </IconButton>
            </Box>
            <Divider />

            {/* Conversation List */}
            <List disablePadding sx={{ px: open ? 0 : 0.5 }}>
                {conversations.map((c) => {
                    const selected = c.id === activeId;
                    return (
                        <ListItem key={c.id} disablePadding>
                            <ListItemButton
                                selected={selected}
                                onClick={() => {
                                    onSelect?.(c.id);
                                    if (isMobile) onCloseMobile?.();
                                }}
                                sx={{
                                    minHeight: 44,
                                    justifyContent: open ? "initial" : "center",
                                    px: 2,
                                }}
                            >
                                <ListItemIcon
                                    sx={{
                                        minWidth: 0,
                                        mr: open ? 2 : "auto",
                                        justifyContent: "center",
                                    }}
                                >
                                    <ChatBubbleOutlineIcon fontSize="small" />
                                </ListItemIcon>
                                <ListItemText
                                    primary={c.title}
                                    primaryTypographyProps={{ fontSize: 14 }}
                                    sx={{ opacity: open ? 1 : 0 }}
                                />
                            </ListItemButton>
                        </ListItem>
                    );
                })}
            </List>
        </>
    );

    return isMobile ? (
        <MuiDrawer
            variant="temporary"
            open={mobileOpen}
            onClose={onCloseMobile}
            ModalProps={{ keepMounted: true }}
            sx={{
                "& .MuiDrawer-paper": {
                    width: DRAWER_WIDTH,
                    top: 0,
                    height: "100%",
                },
            }}
        >
            {drawerContent}
        </MuiDrawer>
    ) : (
        <Drawer
            variant="permanent"
            open={open}
            sx={{
                "& .MuiDrawer-paper": {
                    top: 64,
                    height: "calc(100% - 64px)",
                    borderRight: `1px solid ${theme.palette.divider}`,
                },
            }}
        >
            {drawerContent}
        </Drawer>
    );
};

export default Sidebar;
