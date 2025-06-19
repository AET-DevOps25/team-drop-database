import * as React from "react";
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
} from "@mui/material";
import { styled, Theme, CSSObject, useTheme } from "@mui/material/styles";
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
    appBarOffset?: number; // 默认 64(px)，与固定 AppBar 保持一致
}

const Sidebar: React.FC<SidebarProps> = ({
                                             conversations,
                                             activeId,
                                             onSelect,
                                             appBarOffset = 64,
                                         }) => {
    const [open, setOpen] = React.useState<boolean>(true);
    const theme = useTheme();

    const handleToggle = () => setOpen((prev) => !prev);

    return (
        <Drawer
            variant="permanent"
            open={open}
            sx={{
                "& .MuiDrawer-paper": {
                    top: appBarOffset,
                    height: `calc(100% - ${appBarOffset}px)`,
                    borderRight: `1px solid ${theme.palette.divider}`,
                },
            }}
        >
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

            {/* Conversation list */}
            <List disablePadding sx={{ px: open ? 0 : 0.5 }}>
                {conversations.map((c) => {
                    const selected = c.id === activeId;
                    return (
                        <ListItem key={c.id} disablePadding>
                            <ListItemButton
                                selected={selected}
                                onClick={() => onSelect?.(c.id)}
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
        </Drawer>
    );
};

export default Sidebar;
