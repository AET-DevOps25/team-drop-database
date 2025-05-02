import ImageDisplay from "@/components/ImageDisplay";
import Container from "@mui/material/Container";

export default function Home() {
  return (
      <Container style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "80vh" }}>
        <ImageDisplay />
      </Container>
  );
}
