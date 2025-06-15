import React from 'react';
import { Link } from 'react-router-dom';
import Container from "@mui/material/Container";
import InputBar from "../component/consult/InputBar";

const Home: React.FC = () => (
    <Container>
        <h1>Welcome to Home Page</h1>
        <Link to="/attractions"></Link>
    </Container>
);

export default Home;
