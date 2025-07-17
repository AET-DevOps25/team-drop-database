import React, {useEffect} from 'react';
import './App.css';
import TravelBuddyAppBar from "./component/util/TravelBuddyAppBar";
import {BrowserRouter, Route, Routes} from 'react-router-dom';
import Attractions from "./pages/AttractionList";
import Layout from "./component/auth/Layout";
import RequireAuth from "./component/auth/RequireAuth";
import PersistLogin from "./component/auth/PersistLogin";
import LogIn from "./component/auth/LogIn";
import Consult from "./pages/Consult";
import AttractionDetails from './pages/AttractionDetails';
import Signup from "./component/auth/SignUp";
import Toolbar from "@mui/material/Toolbar";
import {useRouteTimer} from "./hooks/useRouteTimer";
import {initErrorMetrics} from "./errorReporter";

const ROLES = {
    USER: 'USER',
    ADMIN: 'ADMIN',
    MANAGER: 'MANAGER',
}
// Invisible component to hook into route changes
const RouteChangeTracker: React.FC = () => {
    useRouteTimer();
    return null;
};

function App() {
    useEffect(() => {
        initErrorMetrics();  // initialize JS error and unhandled rejection tracking
    }, []);

    return (
        <BrowserRouter>
            {/* Track all route changes */}
            <RouteChangeTracker />

            <TravelBuddyAppBar />
            <Toolbar sx={{ minHeight: 64 }} />
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route path="/" element={<Attractions />} />
                    <Route path="login" element={<LogIn />} />
                    <Route path="register" element={<Signup />} />
                    <Route path="attractions/:id" element={<AttractionDetails />} />

                    {/* Protected Routes */}
                    <Route element={<PersistLogin />}>
                        <Route element={<RequireAuth allowedRoles={[ROLES.USER]} />}>
                            <Route path="consult" element={<Consult />} />
                            <Route path="consult/:conversationId" element={<Consult />} />
                        </Route>
                    </Route>
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
