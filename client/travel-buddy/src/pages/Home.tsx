import Container from "@mui/material/Container";
import InputBar from "../component/consult/InputBar";

const Home = () => (
    <Container>
        <h1>Welcome to Home Page</h1>
        <InputBar userId={123} />
    </Container>
);

export default Home;
