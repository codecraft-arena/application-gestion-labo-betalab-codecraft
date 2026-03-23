/**
 * Page d'accueil de BetaLab.
 * Structure : Hero (slideshow + NeuralCanvas + badge + CTA),
 * 4 cartes domaines, section Approche, section Activités, section Statistiques.
 * Seule page enveloppée par le Layout (Navbar/Footer via App.jsx).
 */
import { Link } from "react-router-dom";
import { GraduationCap, Microscope, BookOpen, Monitor } from "lucide-react";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="hero-section hero-with-slideshow" id="accueil">
        <HeroSlideshow />
        <NeuralCanvas />
        <div className="container">
          <div className="hero-content-center">
            <span className="hero-badge fade-in-up">
              <i className="fas fa-flask"></i> Laboratoire d'excellence en
              informatique
            </span>
            <h1 className="hero-title fade-in-up">
              Explorez. Innovez.
              <br />
              <span className="text-gradient">Transformez le futur.</span>
            </h1>
            <p
              className="hero-subtitle fade-in-up"
              style={{ animationDelay: "0.2s" }}
            >
              BetaLab est un laboratoire de recherche dédié à l'innovation
              technologique. Rejoignez une communauté de chercheurs, étudiants
              et stagiaires qui repoussent les limites du savoir en intelligence
              artificielle, cybersécurité, cloud computing et bien plus.
            </p>
            <div
              className="hero-cta-row fade-in-up"
              style={{ animationDelay: "0.4s" }}
            >
              <Link to="/nous-rejoindre" className="btn-primary-custom">
                <i
                  className="fas fa-user-plus"
                  style={{ marginRight: "0.5rem" }}
                ></i>
                Rejoindre BetaLab
              </Link>
              <Link to="/activites" className="btn-outline-custom">
                <i
                  className="fas fa-compass"
                  style={{ marginRight: "0.5rem" }}
                ></i>
                Découvrir nos travaux
              </Link>
            </div>
            <div
              className="hero-trust fade-in-up"
              style={{ animationDelay: "0.6s" }}
            >
              <div className="trust-avatars">
                <div className="trust-avatar">
                  <GraduationCap size={20} />
                </div>
                <div className="trust-avatar">
                  <Microscope size={20} />
                </div>
                <div className="trust-avatar">
                  <BookOpen size={20} />
                </div>
                <div className="trust-avatar">
                  <Monitor size={20} />
                </div>
              </div>
              <p>
                <strong>+15 membres actifs</strong> — chercheurs, étudiants &
                stagiaires
              </p>
            </div>
          </div>

          <div
            className="hero-cards-section fade-in-up"
            style={{
              animationDelay: "0.8s",
              position: "relative",
              overflow: "hidden",
              borderRadius: "24px",
            }}
          >
            <NeuralCanvas
              nodeCount={50}
              connectionDist={140}
              mouseRadius={180}
              opacity={0.7}
            />
            <div
              className="hero-cards-row"
              style={{ position: "relative", zIndex: 1 }}
            >
              {[
                {
                  icon: "fa-brain",
                  title: "Intelligence Artificielle",
                  desc: "Deep learning, NLP et réseaux de neurones au service de la recherche.",
                },
                {
                  icon: "fa-shield-alt",
                  title: "Cybersécurité",
                  desc: "Protection des données, cryptographie et audit de sécurité.",
                },
                {
                  icon: "fa-cloud",
                  title: "Cloud & Big Data",
                  desc: "Architectures distribuées, analyses prédictives et data science.",
                },
                {
                  icon: "fa-code",
                  title: "Génie Logiciel",
                  desc: "Développement d'applications innovantes et méthodologies agiles.",
                },
              ].map((card) => (
                <div className="hero-card" key={card.title}>
                  <div className="hero-card-icon">
                    <i className={`fas ${card.icon}`}></i>
                  </div>
                  <h3>{card.title}</h3>
                  <p>{card.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Approche Section */}
      <section className="design-section" id="design">
        <div className="container">
          <div className="design-row">
            <div className="design-col">
              <span className="section-label">NOTRE APPROCHE</span>
              <h2 className="section-title">
                La recherche au service
                <br />
                de l'innovation
              </h2>
              <p className="section-text">
                Chez BetaLab, nous croyons que la collaboration entre
                disciplines est le moteur de l'innovation. Notre équipe combine
                expertise scientifique et créativité technique pour développer
                des solutions qui répondent aux défis d'aujourd'hui et de
                demain.
              </p>
              <div className="services-grid">
                <div className="service-card">
                  <div className="service-icon">
                    <i className="fas fa-rocket"></i>
                  </div>
                  <h3>Innovation</h3>
                  <p>
                    Technologies de pointe pour des solutions avant-gardistes
                  </p>
                  <a href="#" className="service-link">
                    En savoir plus <i className="fas fa-arrow-right"></i>
                  </a>
                </div>
                <div className="service-card">
                  <div className="service-icon">
                    <i className="fas fa-chart-line"></i>
                  </div>
                  <h3>Performance</h3>
                  <p>Optimisation continue pour des résultats mesurables</p>
                  <a href="#" className="service-link">
                    En savoir plus <i className="fas fa-arrow-right"></i>
                  </a>
                </div>
              </div>
            </div>
            <div className="design-col">
              <img
                src="https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
                alt="Team meeting"
                style={{
                  width: "100%",
                  borderRadius: "1.5rem",
                  boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Activities Section */}
      <section
        className="activities-section"
        id="activites"
        style={{ position: "relative", overflow: "hidden" }}
      >
        <NeuralCanvas
          nodeCount={45}
          connectionDist={130}
          mouseRadius={170}
          opacity={0.7}
        />
        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <span className="section-label">NOS ACTIVITÉS</span>
            <h2 className="section-title">Domaines d'excellence</h2>
            <p
              className="section-text"
              style={{ maxWidth: "600px", margin: "0 auto" }}
            >
              Des solutions innovantes dans les domaines clés de l'informatique
              moderne
            </p>
          </div>
          <div className="activities-grid">
            {[
              {
                img: "photo-1677442136019-21780ecad995",
                tag: "IA & Machine Learning",
                title: "Intelligence Artificielle",
                desc: "Deep learning, réseaux de neurones, apprentissage automatique",
              },
              {
                img: "photo-1558494949-ef010cbdcc31",
                tag: "Infrastructure",
                title: "Cloud Computing",
                desc: "Architectures distribuées et solutions scalables",
              },
              {
                img: "photo-1563013544-824ae1b704d3",
                tag: "Sécurité",
                title: "Cybersécurité",
                desc: "Protection des données et infrastructure sécurisée",
              },
              {
                img: "photo-1551288049-bebda4e38f71",
                tag: "Analyse",
                title: "Big Data",
                desc: "Analyse prédictive et visualisation de données",
              },
            ].map((a) => (
              <div className="activity-card" key={a.title}>
                <img
                  src={`https://images.unsplash.com/${a.img}?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80`}
                  alt={a.title}
                  className="activity-image"
                />
                <div className="activity-overlay">
                  <span className="activity-tag">{a.tag}</span>
                  <h3>{a.title}</h3>
                  <p>{a.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section
        className="stats-section"
        id="statistiques"
        style={{ position: "relative", overflow: "hidden" }}
      >
        <NeuralCanvas
          nodeCount={35}
          connectionDist={120}
          mouseRadius={160}
          opacity={0.6}
        />
        <div className="container" style={{ position: "relative", zIndex: 1 }}>
          <div className="stats-grid">
            {[
              { num: "02", label: "Chercheurs" },
              { num: "5+", label: "Projets actifs" },
              { num: "7+", label: "Publications" },
              { num: "2+", label: "Collaborateurs" },
            ].map((s) => (
              <div className="stat-item" key={s.label}>
                <span className="stat-number">{s.num}</span>
                <span className="stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
