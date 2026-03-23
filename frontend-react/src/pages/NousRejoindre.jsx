/**
 * Page Nous Rejoindre de BetaLab (en construction).
 * Affiche un hero avec slideshow et un message placeholder.
 */
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";

export default function NousRejoindre() {
  return (
    <>
      <Navbar />
      <section
        className="page-hero hero-with-slideshow"
        style={{
          minHeight: "60vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <HeroSlideshow />
        <NeuralCanvas
          nodeCount={60}
          connectionDist={130}
          mouseRadius={180}
          opacity={0.7}
        />
        <div
          className="container"
          style={{ textAlign: "center", position: "relative", zIndex: 1 }}
        >
          <h1>Nous rejoindre</h1>
          <p
            style={{ marginTop: "1rem", fontSize: "1.1rem", color: "#e9b000" }}
          >
            Page en construction
          </p>
        </div>
      </section>
      <Footer />
    </>
  );
}
