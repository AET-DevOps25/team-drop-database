'use client';

import React, {useState, MouseEvent} from 'react';
import Link from 'next/link';
import {useRouter} from 'next/navigation';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import MenuIcon from '@mui/icons-material/Menu';
// import { useTranslation } from "react-i18next";
// import i18n from "i18next";
// import LanguageDetector from "i18next-browser-languagedetector";

interface Page {
    key: string;
    route: string;
}

interface Language {
    code: string;
    name: string;
    icon: string;
}

function MyAppBar() {
    // const { t } = useTranslation();
    const router = useRouter();

    const pages: Page[] = [
        {key: "navBar.projects", route: "/projects"},
        {key: "navBar.contact", route: "/contact"}
    ];

    const languages: Language[] = [
        {code: 'zh', name: '中文', icon: '🇨🇳'},
        {code: 'en', name: 'English', icon: '🇺🇸'},
        {code: 'de', name: 'Deutsch', icon: '🇩🇪'},
    ];

    // const getInitialLanguage = (): Language => {
    //     const storedLanguage = typeof window !== 'undefined' ? localStorage.getItem('appLanguage') : null;
    //     if (storedLanguage) {
    //         return languages.find(lang => lang.code === storedLanguage) || languages[1];
    //     }
    //     const detectedLanguage = new LanguageDetector().detect();
    //     return languages.find(lang => lang.code === detectedLanguage) || languages[1];
    // };

    const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
    const [anchorElLang, setAnchorElLang] = useState<null | HTMLElement>(null);
    // const [currentLanguage, setCurrentLanguage] = useState<Language>(getInitialLanguage);
    // todo: 把这个改了
    const [currentLanguage] = useState<Language>(languages[0]);

    // useEffect(() => {
    //     i18n.changeLanguage(currentLanguage.code);
    //     document.title = t("navBar.title");
    // }, [currentLanguage, t]);

    const handleToggleDrawer = () => {
        setDrawerOpen(!drawerOpen);
    };

    const handleOpenLanguageMenu = (event: MouseEvent<HTMLElement>) => {
        setAnchorElLang(event.currentTarget);
    };

    const handleCloseLanguageMenu = () => {
        setAnchorElLang(null);
    };

    // const handleLanguageChange = (language: Language) => {
    //     setCurrentLanguage(language);
    //     if (typeof window !== 'undefined') {
    //         localStorage.setItem('appLanguage', language.code);
    //     }
    //     i18n.changeLanguage(language.code);
    //     handleCloseLanguageMenu();
    // };

    const handleNavigation = (route: string) => {
        router.push(route); // 使用 Next.js router 快速跳转，不刷新页面
        setDrawerOpen(false); // 如果是 Drawer 里的，跳转后顺便关掉 Drawer
    };

    return (
        <AppBar position="static">
            <Container maxWidth="xl">
                <Toolbar disableGutters>
                    <AssignmentIndIcon sx={{display: {xs: 'none', md: 'flex'}, mr: 1}}/>
                    {/* Logo按钮，用 Link 包裹 */}
                    <Link href="/" style={{textDecoration: 'none', color: 'inherit'}}>
                        <Typography
                            variant="h6"
                            noWrap
                            sx={{
                                mr: 2,
                                display: {xs: 'none', md: 'flex'},
                                flexGrow: 0,
                                fontFamily: 'serif',
                                fontWeight: 700,
                                letterSpacing: '.3rem',
                                cursor: 'pointer',
                            }}
                        >
                            DropTable Team
                        </Typography>
                    </Link>

                    {/* 移动端汉堡按钮 */}
                    <Box sx={{flexGrow: 1, display: {xs: 'flex', md: 'none'}}}>
                        <IconButton size="large" aria-label="open drawer" onClick={handleToggleDrawer} color="inherit">
                            <MenuIcon/>
                        </IconButton>
                    </Box>

                    {/* 手机端 Logo */}
                    <Link href="/" style={{textDecoration: 'none', color: 'inherit'}}>
                        <Typography
                            variant="h6"
                            noWrap
                            sx={{
                                mr: 2,
                                display: {xs: 'flex', md: 'none'},
                                flexGrow: 1,
                                fontFamily: 'serif',
                                fontWeight: 700,
                                letterSpacing: '.3rem',
                                cursor: 'pointer',
                            }}
                        >
                            DropTable Team
                        </Typography>
                    </Link>

                    {/* 普通菜单 */}
                    <Box sx={{flexGrow: 1, display: {xs: 'none', md: 'flex'}}}>
                        {pages.map((page) => (
                            <Button
                                key={page.key}
                                sx={{my: 2, color: 'white', display: 'block'}}
                                onClick={() => handleNavigation(page.route)}
                            >
                                {/*todo: 改这个*/}
                                {/*{t(page.key)}*/}
                                Item
                            </Button>
                        ))}
                    </Box>

                    {/* 语言切换 */}
                    <Box sx={{flexGrow: 0}}>
                        <Tooltip title="选择语言">
                            <Button
                                variant="outlined"
                                color="inherit"
                                onClick={handleOpenLanguageMenu}
                                startIcon={<span>{currentLanguage.icon}</span>}
                                sx={{display: {xs: 'flex'}, justifyContent: 'center', alignItems: 'center'}}
                            >
                                <Typography sx={{display: {xs: 'none', md: 'block'}}}>
                                    {currentLanguage.name}
                                </Typography>
                            </Button>
                        </Tooltip>

                        <Menu
                            sx={{mt: '45px'}}
                            anchorEl={anchorElLang}
                            anchorOrigin={{vertical: 'top', horizontal: 'right'}}
                            keepMounted
                            transformOrigin={{vertical: 'top', horizontal: 'right'}}
                            open={Boolean(anchorElLang)}
                            onClose={handleCloseLanguageMenu}
                        >
                            {languages.map((language) => (
                                <MenuItem
                                    key={language.code}
                                    // onClick={() => handleLanguageChange(language)}
                                >
                                    <Box sx={{display: 'flex', alignItems: 'center', gap: 1}}>
                                        <span>{language.icon}</span>
                                        <Typography>{language.name}</Typography>
                                    </Box>
                                </MenuItem>
                            ))}
                        </Menu>
                    </Box>
                </Toolbar>
            </Container>

            {/* Drawer 侧边栏 */}
            <Drawer anchor="left" open={drawerOpen} onClose={handleToggleDrawer}>
                <Box
                    sx={{width: 250}}
                    role="presentation"
                    onClick={handleToggleDrawer}
                    onKeyDown={handleToggleDrawer}
                >
                    <List>
                        {pages.map((page) => (
                            <ListItem key={page.key} disablePadding>
                                <ListItemButton onClick={() => handleNavigation(page.route)}>
                                    {/*<ListItemText primary={t(page.key)}/>*/}
                                    {/*todo: 改这个*/}
                                    <ListItemText primary={"item"}/>
                                </ListItemButton>
                            </ListItem>
                        ))}
                    </List>
                </Box>
            </Drawer>
        </AppBar>
    );
}

export default MyAppBar;
