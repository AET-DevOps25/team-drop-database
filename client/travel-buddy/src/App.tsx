import React from 'react';
import './App.css';
import TravelBuddyAppBar from "./component/util/TravelBuddyAppBar";
import {BrowserRouter, Route, Routes} from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import Explore from './pages/Explore';
import Layout from "./component/auth/Layout";
import RequireAuth from "./component/auth/RequireAuth";
import PersistLogin from "./component/auth/PersistLogin";
import LogIn from "./component/auth/LogIn";
import Consult from "./pages/Consult";
import Signup from "./component/auth/SignUp";
import Toolbar from "@mui/material/Toolbar";

const ROLES = {
    USER: 'USER',
    ADMIN: 'ADMIN',
    MANAGER: 'MANAGER',
}

function App() {
    return (
        <BrowserRouter>
            <TravelBuddyAppBar/>
            <Toolbar sx={{ minHeight: 64 }} />
            <Routes>
                <Route path="/" element={<Layout/>}>
                    <Route path="/" element={<Home/>}/>
                    <Route path="login" element={<LogIn/>}/>
                    <Route path="register" element={<Signup/>}/>
                    <Route path="explore" element={<Explore/>}/>
                    <Route path="about" element={<About/>}/>

                    {/* Protected Routes */}
                    <Route element={<PersistLogin/>}>
                        <Route element={<RequireAuth allowedRoles={[ROLES.USER]}/>}>
                            <Route path="/consult" element={<Consult />} />
                            <Route path="/consult/:conversationId" element={<Consult />} />

                        </Route>
                    </Route>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
