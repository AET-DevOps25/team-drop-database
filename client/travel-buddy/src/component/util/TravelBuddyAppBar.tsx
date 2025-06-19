import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import AirplaneTicketIcon from '@mui/icons-material/AirplaneTicket';
import {useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";
import {useUserApi} from "../../api/userApi";
import {ButtonGroup} from "@mui/material";
import LoginIcon from '@mui/icons-material/Login';
import AppRegistrationIcon from '@mui/icons-material/AppRegistration';
import useAuth from "../../hooks/useAuth";

const pages = [
    {label: 'Consult', path: '/consult'},
];

const settings = [
    {key: 'profile', label: 'Profile', path: '/profile'},
    {key: 'logout', label: 'Logout', path: '/logout'},
];

function TravelBuddyAppBar() {
    const navigate = useNavigate();

    const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

    const {pingUserServer} = useUserApi();
    const {auth, setAuth} = useAuth()

    const [anchorElNav, setAnchorElNav] = useState<null | HTMLElement>(null);
    const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElNav(event.currentTarget);
    };
    const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    const handleSettingsClick = (setting: { key: string; label: string; path: string }) => {
        switch (setting.key) {
            case 'profile':
                navigate(setting.path);
                break;
            case 'logout':
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('persist');
                setAuth(null);
                setIsLoggedIn(false);
                navigate('/login');
                break;
            default:
                navigate(setting.path);
                break;
        }
        handleCloseUserMenu();
    };

    useEffect(() => {
        const checkLogin = async () => {
            const success = await pingUserServer();
            setIsLoggedIn(success);
        };
        checkLogin();
    }, [auth]);

    return (
        <AppBar
            position="fixed"
            sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
        >
            <Container maxWidth="xl">
                <Toolbar
                    disableGutters
                    sx={{
                        minHeight: 64,
                        maxHeight: 64,
                    }}
                >
                    <AirplaneTicketIcon sx={{display: {xs: 'none', md: 'flex'}, mr: 1}}/>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        onClick={() => navigate('/')}
                        sx={{
                            mr: 2,
                            display: {xs: 'none', md: 'flex'},
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.3rem',
                            color: 'inherit',
                            textDecoration: 'none',
                            cursor: 'pointer',
                        }}
                    >
                        Travel Buddy
                    </Typography>

                    <Box sx={{flexGrow: 1, display: {xs: 'flex', md: 'none'}}}>
                        <IconButton
                            size="large"
                            aria-label="account of current user"
                            aria-controls="menu-appbar"
                            aria-haspopup="true"
                            onClick={handleOpenNavMenu}
                            color="inherit"
                        >
                            <MenuIcon/>
                        </IconButton>
                        <Menu
                            id="menu-appbar"
                            anchorEl={anchorElNav}
                            anchorOrigin={{
                                vertical: 'bottom',
                                horizontal: 'left',
                            }}
                            keepMounted
                            transformOrigin={{
                                vertical: 'top',
                                horizontal: 'left',
                            }}
                            open={Boolean(anchorElNav)}
                            onClose={handleCloseNavMenu}
                            sx={{display: {xs: 'block', md: 'none'}}}
                        >
                            {pages.map(({label, path}) => (
                                <MenuItem
                                    key={label}
                                    onClick={() => {
                                        navigate(path);
                                        handleCloseNavMenu();
                                    }}
                                >
                                    <Typography sx={{textAlign: 'center'}}>{label}</Typography>
                                </MenuItem>
                            ))}
                        </Menu>
                    </Box>
                    <AirplaneTicketIcon sx={{display: {xs: 'flex', md: 'none'}, mr: 1}}/>
                    <Typography
                        variant="h5"
                        noWrap
                        component="div"
                        onClick={() => navigate('/')}
                        sx={{
                            mr: 2,
                            display: {xs: 'flex', md: 'none'},
                            flexGrow: 1,
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.3rem',
                            color: 'inherit',
                            textDecoration: 'none',
                            cursor: 'pointer',
                        }}
                    >
                        Travel Buddy
                    </Typography>
                    <Box sx={{flexGrow: 1, display: {xs: 'none', md: 'flex'}}}>
                        {pages.map(({label, path}) => (
                            <Button
                                key={label}
                                onClick={() => {
                                    navigate(path);
                                    handleCloseNavMenu();
                                }}
                                sx={{my: 2, color: 'white', display: 'block'}}
                            >
                                {label}
                            </Button>
                        ))}
                    </Box>
                    <Box sx={{flexGrow: 0}}>
                        {isLoggedIn ? (
                            <>
                                <Tooltip title="Open settings">
                                    <IconButton onClick={handleOpenUserMenu} sx={{p: 0}}>
                                        <Avatar alt="User" src="/static/images/avatar/2.jpg"/>
                                    </IconButton>
                                </Tooltip>
                                <Menu
                                    sx={{mt: '45px'}}
                                    id="menu-appbar"
                                    anchorEl={anchorElUser}
                                    anchorOrigin={{
                                        vertical: 'top',
                                        horizontal: 'right',
                                    }}
                                    keepMounted
                                    transformOrigin={{
                                        vertical: 'top',
                                        horizontal: 'right',
                                    }}
                                    open={Boolean(anchorElUser)}
                                    onClose={handleCloseUserMenu}
                                >
                                    {settings.map((setting) => (
                                        <MenuItem
                                            key={setting.key}
                                            onClick={() => handleSettingsClick(setting)}
                                        >
                                            <Typography sx={{textAlign: 'center'}}>
                                                {setting.label}
                                            </Typography>
                                        </MenuItem>
                                    ))}
                                </Menu>
                            </>
                        ) : (
                            <>
                                <Box sx={{flexGrow: 0, display: {xs: 'none', sm: 'flex'}}}>
                                    <ButtonGroup variant="outlined">
                                        <Button color="inherit" onClick={() => navigate('/login')}>Login</Button>
                                        <Button color="inherit" onClick={() => navigate('/register')}>Register</Button>
                                    </ButtonGroup>
                                </Box>

                                <Box sx={{flexGrow: 0, display: {xs: 'flex', sm: 'none'}}}>
                                    <Tooltip title="Login">
                                        <IconButton color="inherit" onClick={() => navigate('/login')}>
                                            <LoginIcon fontSize="small"/>
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Register">
                                        <IconButton color="inherit" onClick={() => navigate('/register')}>
                                            <AppRegistrationIcon fontSize="small"/>
                                        </IconButton>
                                    </Tooltip>
                                </Box>
                            </>
                        )}
                    </Box>

                </Toolbar>
            </Container>
        </AppBar>
    )
        ;
}

export default TravelBuddyAppBar;
