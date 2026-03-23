/**
 * Page Activités de recherche de BetaLab.
 * Affiche les 6 domaines d'excellence (IA, Cloud, Cyber, Big Data, Embarqué, Blockchain)
 * sous forme de cartes avec images Unsplash, tags et descriptions.
 */
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";
import "./Activites.css";

/* Données des 6 domaines de recherche */
const activities = [
  {
    icon: "fa-brain",
    tag: "IA & ML",
    title: "Intelligence Artificielle",
    desc: "Deep learning, traitement du langage naturel, vision par ordinateur et apprentissage par renforcement.",
    img: "photo-1677442136019-21780ecad995",
  },
  {
    icon: "fa-cloud",
    tag: "Infrastructure",
    title: "Cloud Computing",
    desc: "Architectures distribuées, microservices, containerisation et orchestration à grande échelle.",
    img: "photo-1558494949-ef010cbdcc31",
  },
  {
    icon: "fa-shield-halved",
    tag: "Sécurité",
    title: "Cybersécurité",
    desc: "Analyse de vulnérabilités, cryptographie appliquée, détection d'intrusions et sécurité des réseaux.",
    img: "photo-1563013544-824ae1b704d3",
  },
  {
    icon: "fa-chart-bar",
    tag: "Analyse",
    title: "Big Data",
    desc: "Analyse prédictive, traitement de données massives, visualisation et data engineering.",
    img: "photo-1551288049-bebda4e38f71",
  },
  {
    icon: "fa-microchip",
    tag: "Hardware",
    title: "Systèmes Embarqués",
    desc: "IoT, systèmes temps réel, conception de circuits et programmation bas niveau.",
    img: "photo-1518770660439-4636190af475",
  },
  {
    icon: "fa-cubes",
    tag: "Web3",
    title: "Blockchain",
    desc: "Smart contracts, DeFi, NFT et architectures décentralisées.",
    img: "photo-1639762681485-074b7f938ba0",
  },
];

export default function Activites() {
  return (
    <>
      <Navbar />
      {/* Hero */}
      <section
        className="page-hero activites-hero hero-with-slideshow"
        style={{ position: "relative", overflow: "hidden" }}
      >
        <HeroSlideshow />
        <NeuralCanvas
          nodeCount={60}
          connectionDist={130}
          mouseRadius={180}
          opacity={0.7}
        />
        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <span className="hero-tag">NOS DOMAINES</span>
          <h1>
            Activités de <span className="gradient">Recherche</span>
          </h1>
          <p>
            Explorez nos domaines d'excellence en informatique. Chaque activité
            est animée par des chercheurs passionnés qui repoussent les
            frontières de la connaissance.
          </p>
          <div className="hero-stats">
            {[
              { num: "6+", label: "Domaines" },
              { num: "15+", label: "Chercheurs" },
              { num: "10+", label: "Publications" },
            ].map((s) => (
              <div className="hero-stat-item" key={s.label}>
                <span className="hero-stat-num">{s.num}</span>
                <span className="hero-stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Activities Grid */}
      <section className="content-section" style={{ background: "white" }}>
        <div className="container">
          <div className="act-grid">
            {activities.map((a) => (
              <div className="act-card" key={a.title}>
                <div className="act-img-wrap">
                  <img
                    src={`https://images.unsplash.com/${a.img}?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80`}
                    alt={a.title}
                  />
                  <span className="act-tag">{a.tag}</span>
                </div>
                <div className="act-body">
                  <h3>
                    <i className={`fas ${a.icon}`}></i> {a.title}
                  </h3>
                  <p>{a.desc}</p>
                  <a href="#" className="act-link">
                    En savoir plus <i className="fas fa-arrow-right"></i>
                  </a>
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
