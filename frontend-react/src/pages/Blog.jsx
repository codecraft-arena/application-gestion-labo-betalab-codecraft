/**
 * Page Blog de BetaLab (en construction).
 * Affiche un hero avec slideshow et un message placeholder.
 */
import { useState, useEffect, useRef } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";

// Carousel automatique pour les 4 images
const ImageCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const images = [
    "/Report/betalab15.JPG",
    "/Report/betalab14.JPG",
    "/Report/betalab7.MP4",
    "/Report/betalab1.MP4",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 4000); // Change toutes les 4 secondes

    return () => clearInterval(interval);
  }, [images.length]);

  const goToSlide = (index) => {
    setCurrentIndex(index);
  };

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const prevSlide = () => {
    setCurrentIndex(
      (prevIndex) => (prevIndex - 1 + images.length) % images.length,
    );
  };

  return (
    <div className="image-carousel">
      <div className="carousel-container">
        <div
          className="carousel-track"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {images.map((image, index) => (
            <div key={index} className="carousel-slide">
              {image.includes(".MP4") ? (
                <video
                  autoPlay
                  muted
                  loop
                  playsInline
                  src={image}
                  alt={`Slide ${index + 1}`}
                />
              ) : (
                <img src={image} alt={`Slide ${index + 1}`} />
              )}
            </div>
          ))}
        </div>

        {/* Navigation buttons */}
        <button className="carousel-btn carousel-btn-prev" onClick={prevSlide}>
          <i className="fas fa-chevron-left"></i>
        </button>
        <button className="carousel-btn carousel-btn-next" onClick={nextSlide}>
          <i className="fas fa-chevron-right"></i>
        </button>

        {/* Indicators */}
        <div className="carousel-indicators">
          {images.map((_, index) => (
            <button
              key={index}
              className={`carousel-indicator ${index === currentIndex ? "active" : ""}`}
              onClick={() => goToSlide(index)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const BlogCard = ({ type, url, title, desc }) => (
  <div className="blog-card">
    <div className="blog-card-media">
      {type === "video" ? (
        <video controls src={url} />
      ) : (
        <img src={url} alt={title} />
      )}
    </div>
    <div className="blog-card-body">
      <div className="blog-card-type">
        {type === "video" ? "Vidéo" : "Photo"}
      </div>
      <h4>{title}</h4>
      <p>{desc}</p>
    </div>
  </div>
);

export default function Blog() {
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
          <h1 className="blog-main-title">
            École de Terrain &{" "}
            <span className="highlight-gold">Réalisations 2026</span>
          </h1>
          <p className="blog-main-subtitle">
            L'immersion professionnelle au cœur de l'innovation BetaLab
          </p>
        </div>
      </section>

      <section className="blog-content-section">
        <div className="container blog-container-padding">
          <div className="blog-intro-premium-card">
            <h2>L'Informatique au Cœur du Métier</h2>
            <div className="intro-text-content">
              <p>
                Participer à une école de terrain chez BetaLab n'est pas qu'un
                simple stage technique. C'est une exploration de la posture
                professionnelle de l'informaticien. Entre rigueur analytique,
                force de proposition et travail d'équipe, nos stagiaires ont été
                confrontés aux réalités concrètes du terrain : gestion des
                imprévus, optimisation de ressources et communication
                interdisciplinaire.
              </p>
              <p>
                Ce journal de bord témoigne de leur évolution, depuis les
                premières sessions de formation sur l'intelligence artificielle
                jusqu'à la présentation finale de solutions d'hébergement
                innovantes.
              </p>
            </div>
          </div>

          {/* SECTION CAROUSEL AUTOMATIQUE */}
          <div className="blog-category-header">
            <i className="fas fa-images"></i>
            <h3>
              Galerie <span className="highlight-gold">Multimédia</span>
            </h3>
          </div>
          <ImageCarousel />

          {/* SECTION 1: L'ÉQUIPE ET LE CADRE */}
          <div className="blog-category-header">
            <i className="fas fa-users-gear"></i>
            <h3>
              L'Équipe &{" "}
              <span className="highlight-gold">Accueil Professionnel</span>
            </h3>
          </div>
          <div className="blog-grid grid-centered">
            <BlogCard
              type="image"
              url="/Report/betalab15.JPG"
              title="Accueil des Stagiaires"
              desc="Première prise de contact avec le responsable BetaLab. Un moment clé pour définir les attentes et l'éthique de travail au laboratoire."
            />
            <BlogCard
              type="image"
              url="/Report/betalab14.JPG"
              title="L'Esprit BetaLab"
              desc="Portrait d'une équipe soudée. La cohésion est le premier pilier de la réussite de nos projets informatiques."
            />
            <BlogCard
              type="video"
              url="/Report/betalab7.MP4"
              title="Le Cadre de Recherche"
              desc="Une vue d'ensemble de l'environnement où se mêlent innovation technologique et travail collaboratif."
            />
          </div>

          {/* SECTION 2: QUOTIDIEN */}
          <div className="blog-category-header">
            <i className="fas fa-camera-retro"></i>
            <h3>
              Immersion <span className="highlight-gold">au Quotidien</span>
            </h3>
          </div>
          <div className="blog-grid grid-2-cols grid-centered">
            <BlogCard
              type="video"
              url="/Report/betalab1.MP4"
              title="Vie au Labo - Épisode 1"
              desc="Séquences spontanées capturées durant le stage : entre moments de concentration intense et échanges productifs."
            />
            <BlogCard
              type="video"
              url="/Report/betalab12.MP4"
              title="Vie au Labo - Épisode 2"
              desc="Le rôle de l'informaticien va au-delà du code : il s'agit d'observer, d'apprendre et de s'adapter au milieu professionnel."
            />
          </div>

          {/* SECTION 3: FORMATION IA */}
          <div className="blog-category-header">
            <i className="fas fa-microchip"></i>
            <h3>
              Maîtrise de{" "}
              <span className="highlight-gold">
                l'Intelligence Artificielle
              </span>
            </h3>
          </div>
          <div className="blog-grid grid-4-cols">
            {[
              { url: "/Report/betalab2.JPG", title: "Apprentissage Continu" },
              { url: "/Report/betalab8.JPG", title: "Théorie de l'IA" },
              { url: "/Report/betalab9.JPG", title: "Outils de Génération" },
              { url: "/Report/betalab13.JPG", title: "Débat & Application" },
            ].map((m, i) => (
              <BlogCard
                key={i}
                type="image"
                url={m.url}
                title={m.title}
                desc="Focus sur l'utilisation avancée de l'IA générative pour booster la productivité et la créativité logicielle durant les meetups."
              />
            ))}
          </div>

          {/* SECTION 4: RÉALISATIONS TECHNIQUES */}
          <div className="blog-category-header">
            <i className="fas fa-code"></i>
            <h3>
              Soutenance &{" "}
              <span className="highlight-gold">Démonstrations Techniques</span>
            </h3>
          </div>
          <p className="section-intro-text center">
            Démonstrations de fin de parcours sous l'expertise de nos directeurs
            scientifiques.
          </p>
          <div className="blog-grid grid-4-cols">
            <BlogCard
              type="image"
              url="/Report/betalab6.JPG"
              title="Expertise Scientifique"
              desc="Le Professeur Alain Tchana et le Dr Bessala Bessala Parfait apportent leur feedback critique sur les projets."
            />
            <BlogCard
              type="image"
              url="/Report/betalab16.jpg"
              title="Projet : Hébergement Mobile"
              desc="Présentation de la solution inédite permettant de transformer un appareil mobile en serveur web autonome."
            />
            <BlogCard
              type="image"
              url="/Report/betalab4.JPG"
              title="Site Web de Gestion Labo"
              desc="Développement d'un outil complet de suivi de matériel et de gestion des ressources de laboratoire."
            />
            <BlogCard
              type="image"
              url="/Report/betalab10.JPG"
              title="Interface & UX Design"
              desc="Focus sur l'expérience utilisateur et les fonctionnalités métier intégrées dans les livrables."
            />
          </div>
        </div>
      </section>

      <style
        dangerouslySetInnerHTML={{
          __html: `
        /* Dégradé blanc/or pour tous les titres */
        .blog-main-title,
        .blog-category-header h3,
        .blog-intro-premium-card h2,
        .blog-card-body h4 {
          background: linear-gradient(135deg, #ffffff, #e9b000);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          text-fill-color: transparent;
        }
        
        .highlight-gold {
          color: var(--gold);
          font-weight: 900;
        }
        
        /* Carousel Styles */
        .image-carousel {
          margin: 4rem 0;
          padding: 0 2rem;
        }
        
        .carousel-container {
          position: relative;
          max-width: 1200px;
          margin: 0 auto;
          border-radius: 20px;
          overflow: hidden;
          box-shadow: 0 20px 60px rgba(0,0,0,0.4);
          background: #000;
        }
        
        .carousel-track {
          display: flex;
          transition: transform 0.6s ease-in-out;
          height: 600px;
        }
        
        .carousel-slide {
          min-width: 100%;
          height: 600px;
          position: relative;
        }
        
        .carousel-slide video,
        .carousel-slide img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .carousel-btn {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          background: rgba(0,0,0,0.7);
          color: white;
          border: none;
          width: 50px;
          height: 50px;
          border-radius: 50%;
          cursor: pointer;
          font-size: 1.2rem;
          z-index: 10;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .carousel-btn:hover {
          background: var(--gold);
          color: var(--dark);
          transform: translateY(-50%) scale(1.1);
        }
        
        .carousel-btn-prev {
          left: 20px;
        }
        
        .carousel-btn-next {
          right: 20px;
        }
        
        .carousel-indicators {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 12px;
          z-index: 10;
        }
        
        .carousel-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          border: 2px solid rgba(255,255,255,0.5);
          background: transparent;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        
        .carousel-indicator.active {
          background: var(--gold);
          border-color: var(--gold);
          transform: scale(1.2);
        }
        
        .blog-main-title {
          font-size: clamp(2.2rem, 8vw, 3.8rem);
          font-weight: 900;
          color: #fff;
          margin: 0;
          letter-spacing: -2px;
          line-height: 1.1;
        }
        .blog-main-subtitle {
          font-size: clamp(1rem, 3vw, 1.3rem);
          color: rgba(255,255,255,0.7);
          margin-top: 1.2rem;
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
          font-weight: 400;
        }
        .blog-content-section {
          padding: 6rem 0;
          background: #060d17;
          min-height: 100vh;
        }
        .blog-container-padding {
          padding-left: 4%;
          padding-right: 4%;
          max-width: 1500px;
          margin-left: auto;
          margin-right: auto;
        }
        
        /* INTRO CARD REDESIGN (Inspired by Activities Page) */
        .blog-intro-premium-card {
          background: #f8f9fa; /* Lighter background */
          padding: 4rem;
          border-radius: 30px;
          margin-bottom: 6rem;
          box-shadow: 0 20px 50px rgba(0,0,0,0.3);
          border: 1px solid rgba(0,0,0,0.05);
        }
        .blog-intro-premium-card h2 {
          color: #14213d; /* Dark blue title */
          font-size: 2.5rem;
          margin-bottom: 2.5rem;
          font-weight: 800;
          text-align: center;
          position: relative;
        }
        .blog-intro-premium-card h2::after {
          content: "";
          position: absolute;
          bottom: -12px;
          left: 50%;
          transform: translateX(-50%);
          width: 80px;
          height: 4px;
          background: var(--gold);
          border-radius: 2px;
        }
        .intro-text-content p {
          color: #4a5568; /* Mid-gray text for readability */
          max-width: 950px;
          margin: 1.5rem auto;
          font-size: 1.2rem;
          line-height: 1.9;
          text-align: center;
        }

        .blog-category-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.2rem;
          margin-bottom: 4rem;
          margin-top: 7rem;
        }
        .blog-category-header i {
          color: var(--gold);
          font-size: 2.5rem;
        }
        .blog-category-header h3 {
          font-size: 2.4rem;
          color: #fff;
          margin: 0;
          text-transform: uppercase;
          letter-spacing: 4px;
          font-weight: 800;
        }
        
        /* GRID LOGIC - Forced Horizontal */
        .blog-grid {
          display: flex;
          flex-wrap: nowrap;
          gap: 3.5rem;
          padding: 1rem 0 3rem 0;
          overflow-x: auto;
          scrollbar-width: thin;
          scrollbar-color: var(--gold) rgba(255,255,255,0.05);
          justify-content: flex-start; /* Default start for scroll */
        }
        
        .blog-grid::-webkit-scrollbar {
          height: 6px;
        }
        .blog-grid::-webkit-scrollbar-track {
          background: rgba(255,255,255,0.02);
          border-radius: 10px;
        }
        .blog-grid::-webkit-scrollbar-thumb {
          background: var(--gold);
          border-radius: 10px;
        }

        .grid-centered {
          justify-content: center;
        }

        /* Enforce same size for all cards (now 450px) */
        .blog-card {
           min-width: 450px;
           width: 450px;
           flex-shrink: 0;
           background: #0d1a2d;
           border-radius: 26px;
           overflow: hidden;
           border: 1px solid rgba(255,255,255,0.04);
           transition: all 0.5s ease;
           display: flex;
           flex-direction: column;
           height: 650px; /* Fixed height adjusted for width */
        }
        
        .blog-card:hover {
           transform: translateY(-15px);
           border-color: var(--gold);
           box-shadow: 0 30px 60px rgba(0,0,0,0.7);
        }
        .blog-card-media {
           position: relative;
           height: 280px; /* Fixed media height */
           overflow: hidden;
           background: #000;
           display: flex;
           align-items: center;
           justify-content: center;
        }
        .blog-card-media video, .blog-card-media img {
           width: 100%;
           height: 100%;
           object-fit: cover;
           transition: transform 0.8s ease;
        }
        .blog-card-body {
           padding: 2.5rem;
           flex-grow: 1;
           display: flex;
           flex-direction: column;
           align-items: center;
           text-align: center;
           justify-content: flex-start;
        }
        
        /* BRIGHT BADGES */
        .blog-card-type {
           font-size: 0.75rem;
           font-weight: 900;
           text-transform: uppercase;
           color: #000;              /* Black text for contrast */
           background: var(--gold);   /* Solid Gold background */
           letter-spacing: 1.5px;
           padding: 0.5rem 1.4rem;
           border-radius: 30px;
           width: fit-content;
           margin-bottom: 2rem;
           box-shadow: 0 4px 10px rgba(233,176,0,0.4);
        }
        .blog-card-body h4 {
           font-size: 1.6rem;
           color: #fff;
           margin: 0 0 1.2rem 0;
           font-weight: 800;
        }
        .blog-card-body p {
           font-size: 1.05rem;
           color: rgba(255,255,255,0.7);
           line-height: 1.8;
           margin: 0;
        }
        
        /* Responsive Carousel */
        @media (max-width: 768px) {
          .carousel-container {
            margin: 0 1rem;
            border-radius: 15px;
          }
          
          .carousel-track,
          .carousel-slide {
            height: 400px;
          }
          
          .carousel-btn {
            width: 40px;
            height: 40px;
            font-size: 1rem;
          }
          
          .carousel-btn-prev {
            left: 10px;
          }
          
          .carousel-btn-next {
            right: 10px;
          }
        }
      `,
        }}
      />
      <Footer />
    </>
  );
}
