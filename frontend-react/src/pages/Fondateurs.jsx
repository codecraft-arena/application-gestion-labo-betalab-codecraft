/**
 * Page Fondateurs / Responsables de BetaLab.
 * Affiche les co-directeurs (Bessala, Tchana) et les collaborateurs externes
 * (Bromberg, Hagimont, Vuillerme) avec photos et affiliations.
 */
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";
import "./Fondateurs.css";

/* Co-directeurs du laboratoire */
const directors = [
  {
    name: "Parfait BESSALA BESSALA",
    title: "Information System & Software Engineering PhD",
    role: "Co-directeur",
    photo: "/fondateurs/parfait.png",
  },
  {
    name: "Alain TCHANA",
    title: "Professeur",
    role: "Co-directeur",
    photo: "/fondateurs/alain.png",
  },
];

/* Collaborateurs externes internationaux */
const collaborators = [
  {
    name: "David BROMBERG",
    title: "Professeur",
    affiliation: "Université de Rennes, France",
    photo: "/fondateurs/david.jpeg",
  },
  {
    name: "Daniel HAGIMONT",
    title: "Professeur",
    affiliation: "Toulouse INP, France",
    photo: "/fondateurs/daniel.png",
  },
  {
    name: "Nicolas VUILLERME",
    title: "Professeur",
    affiliation: "Université Grenoble Alpes, France",
    photo: "/fondateurs/nicolas.png",
  },
];

export default function Fondateurs() {
  return (
    <>
      <Navbar />
      <section
        className="page-hero hero-with-slideshow fondateurs-hero"
        style={{ position: "relative", overflow: "hidden" }}
      >
        <HeroSlideshow />
        <NeuralCanvas
          nodeCount={60}
          connectionDist={130}
          mouseRadius={180}
          opacity={0.5}
        />
        <div
          className="container"
          style={{ textAlign: "center", position: "relative", zIndex: 1 }}
        >
          <span className="hero-tag">ÉQUIPE DIRIGEANTE</span>
          <h1>
            Responsables & <span className="gradient">Collaborateurs</span>
          </h1>
          <p>
            Découvrez l'équipe dirigeante et les partenaires de recherche qui
            portent la vision de BetaLab au quotidien.
          </p>
        </div>
      </section>

      <section className="fondateurs-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="section-header">
            <span className="section-label">
              <i className="fas fa-users" style={{ marginRight: "0.5rem" }}></i>
              Direction
            </span>
            <h2>Co-directeurs</h2>
            <p>
              Les fondateurs à l'origine de la création de BetaLab et qui
              assurent la direction scientifique du laboratoire.
            </p>
          </div>
          <div className="directors-grid">
            {directors.map((d) => (
              <div className="founder-card" key={d.name}>
                <div className="founder-photo">
                  <img src={d.photo} alt={d.name} />
                  <div className="founder-photo-overlay" />
                </div>
                <div className="founder-info">
                  <span className="founder-role">{d.role}</span>
                  <h3>{d.name}</h3>
                  <p className="founder-title">{d.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div style={{ padding: "0.5rem 0", background: "#f5f5f5" }}>
        <div className="fondateurs-divider" />
      </div>

      <section className="fondateurs-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="section-header">
            <span className="section-label">
              <i
                className="fas fa-handshake"
                style={{ marginRight: "0.5rem" }}
              ></i>
              Partenaires
            </span>
            <h2>Collaborateurs Externes</h2>
            <p>
              Des chercheurs et professeurs de renommée internationale qui
              enrichissent la recherche de BetaLab.
            </p>
          </div>
          <div className="collaborators-grid">
            {collaborators.map((c) => (
              <div className="founder-card" key={c.name}>
                <div className="founder-photo">
                  <img src={c.photo} alt={c.name} />
                  <div className="founder-photo-overlay" />
                </div>
                <div className="founder-info">
                  <span className="founder-role">Collaborateur</span>
                  <h3>{c.name}</h3>
                  <p className="founder-title">{c.title}</p>
                  <p className="founder-affiliation">
                    <i className="fas fa-map-marker-alt"></i>
                    {c.affiliation}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
