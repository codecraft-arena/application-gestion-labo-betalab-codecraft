/**
 * Page À propos de BetaLab.
 * Sections : Hero, Histoire du labo, Mission (4 piliers), Valeurs (4 principes),
 * Partenaires (6 institutions) avec CTA vers la page Contact.
 */
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";
import { Link } from "react-router-dom";
import "./APropos.css";

/* Données des 4 piliers de mission */
const missions = [
  {
    icon: "fa-microscope",
    title: "Recherche de pointe",
    desc: "Promouvoir la recherche en informatique de pointe et repousser les frontières de la connaissance scientifique.",
  },
  {
    icon: "fa-user-graduate",
    title: "Formation",
    desc: "Développer les compétences des étudiants et chercheurs dans le domaine de l’informatique avancée.",
  },
  {
    icon: "fa-handshake",
    title: "Collaboration",
    desc: "Favoriser la collaboration entre chercheurs et professionnels de l’industrie pour des résultats d’exception.",
  },
  {
    icon: "fa-lightbulb",
    title: "Solutions innovantes",
    desc: "Contribuer à l’émergence de solutions technologiques innovantes pour les besoins spécifiques de l’Afrique.",
  },
];

/* Données des 4 valeurs fondamentales */
const values = [
  {
    icon: "fa-shield-alt",
    title: "Intégrité",
    desc: "Nous maintenons les plus hauts standards d’éthique et de transparence dans toutes nos activités de recherche.",
  },
  {
    icon: "fa-users",
    title: "Collaboration",
    desc: "Nous croyons en la puissance du travail d’équipe et des partenariats pour atteindre des résultats exceptionnels.",
  },
  {
    icon: "fa-rocket",
    title: "Innovation",
    desc: "Nous encourageons la pensée créative et l’exploration de nouvelles approches face aux défis technologiques.",
  },
  {
    icon: "fa-globe-africa",
    title: "Impact",
    desc: "Nous visons à créer des technologies ayant un impact positif sur la société et l’environnement.",
  },
];

/* Partenaires institutionnels */
const partners = [
  { icon: "fa-university", name: "Université de Paris" },
  { icon: "fa-microchip", name: "Tech Solutions" },
  { icon: "fa-flask", name: "Institut National de Recherche" },
  { icon: "fa-laptop-code", name: "Future Labs" },
  { icon: "fa-database", name: "Data Sciences Corp" },
  { icon: "fa-cogs", name: "Innovation Center" },
];

export default function APropos() {
  return (
    <>
      <Navbar />

      {/* Hero */}
      <section
        className="page-hero hero-with-slideshow apropos-hero"
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
          <span className="hero-tag">À PROPOS DU LABORATOIRE</span>
          <h1>
            Recherche informatique &{" "}
            <span className="gradient">innovations technologiques</span>
          </h1>
          <p>
            Découvrez l’histoire, la mission et les valeurs qui fondent
            l’identité de BetaLab.
          </p>
        </div>
      </section>

      {/* History */}
      <section className="apropos-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="history-grid">
            <div className="history-text">
              <span className="history-badge">
                <i
                  className="fas fa-landmark"
                  style={{ marginRight: "0.5rem" }}
                ></i>
                Notre histoire
              </span>
              <h2>
                Le Laboratoire <span className="gradient">BetaLab</span>
              </h2>
              <p>
                Le Laboratoire de Recherche Avancée en Informatique (Beta),
                dirigé par le Professeur Tchana Alain, est un espace dédié à la
                recherche et à l’innovation en informatique au Cameroun.
              </p>
              <p>
                Notre mission est de former des chercheurs et développeurs de
                haut niveau, capables de relever les défis technologiques et
                scientifiques du continent africain.
              </p>
              <div className="history-highlight">
                <i className="fas fa-award"></i>
                <span>
                  BetaLab offre un environnement propice à l’initiation à la
                  recherche et à l’innovation, avec une équipe de chercheurs
                  expérimentés et des collaborations internationales.
                </span>
              </div>
            </div>
            <div className="history-image">
              <img src="/about/about-lab.jpg" alt="Le laboratoire BetaLab" />
            </div>
          </div>
        </div>
      </section>

      <div style={{ padding: "0.5rem 0", background: "#f5f5f5" }}>
        <div className="apropos-divider" />
      </div>

      {/* Mission */}
      <section className="apropos-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="mission-header">
            <span className="history-badge">
              <i
                className="fas fa-bullseye"
                style={{ marginRight: "0.5rem" }}
              ></i>
              Notre mission
            </span>
            <h2>Ce qui nous anime</h2>
            <p>
              Quatre piliers fondamentaux guident chacune de nos actions et
              orientent notre recherche.
            </p>
          </div>
          <div className="mission-grid">
            {missions.map((m) => (
              <div className="mission-card" key={m.title}>
                <div className="mission-icon">
                  <i className={`fas ${m.icon}`}></i>
                </div>
                <h3>{m.title}</h3>
                <p>{m.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="apropos-section" style={{ background: "#14213d" }}>
        <div className="container">
          <div className="values-header">
            <span className="history-badge">
              <i className="fas fa-heart" style={{ marginRight: "0.5rem" }}></i>
              Nos valeurs
            </span>
            <h2>Ce en quoi nous croyons</h2>
            <p>
              Des principes qui orientent notre démarche scientifique et nos
              relations humaines.
            </p>
          </div>
          <div className="values-grid">
            {values.map((v) => (
              <div className="value-card" key={v.title}>
                <div className="value-icon">
                  <i className={`fas ${v.icon}`}></i>
                </div>
                <h3>{v.title}</h3>
                <p>{v.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Partners */}
      <section className="apropos-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="partners-header">
            <span className="history-badge">
              <i className="fas fa-globe" style={{ marginRight: "0.5rem" }}></i>
              Partenaires
            </span>
            <h2>Nos partenaires</h2>
            <p>
              Des institutions prestigieuses qui collaborent avec BetaLab pour
              faire avancer la recherche.
            </p>
          </div>
          <div className="partners-grid">
            {partners.map((p) => (
              <div className="partner-card" key={p.name}>
                <div className="partner-icon">
                  <i className={`fas ${p.icon}`}></i>
                </div>
                <span>{p.name}</span>
              </div>
            ))}
          </div>
          <div className="partners-cta">
            <Link to="/contact">
              <i className="fas fa-envelope"></i> Intéressé par un partenariat ?
              Contactez-nous
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
