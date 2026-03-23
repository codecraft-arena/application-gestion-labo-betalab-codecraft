/**
 * Page FAQ de BetaLab.
 * Accélérateur de questions/réponses en format accordéon.
 * 4 questions courantes (rejoindre, stages, domaines, visites) + CTA Contact.
 */
import { useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";
import { Link } from "react-router-dom";
import "./FAQ.css";

/* Questions/réponses du FAQ — contenu JSX pour les réponses */
const faqs = [
  {
    icon: "fa-user-plus",
    question: "Comment rejoindre le laboratoire ?",
    answer: (
      <>
        <p>
          Plusieurs voies vous permettent de rejoindre notre laboratoire en tant
          qu’étudiant, chercheur ou collaborateur :
        </p>
        <ul>
          <li>
            Participer aux événements organisés ou soutenus par le laboratoire
            (hackathons, séminaires, ateliers)
          </li>
          <li>
            S’engager dans un projet de recherche conjoint avec l’une de nos
            équipes
          </li>
          <li>
            Être recommandé par un membre du laboratoire ou un partenaire
            institutionnel
          </li>
          <li>
            Répondre à un appel à candidatures ou une offre de stage publiée sur
            notre site
          </li>
        </ul>
        <p>
          Nous vous invitons à suivre nos actualités pour ne manquer aucune
          opportunité.
        </p>
      </>
    ),
  },
  {
    icon: "fa-graduation-cap",
    question: "Proposez-vous des stages pour les étudiants ?",
    answer: (
      <>
        <p>
          Oui, nous accueillons régulièrement des stagiaires à tous les niveaux
          (Licence, Master, Doctorat). Nos stages permettent de :
        </p>
        <ul>
          <li>Travailler sur des projets concrets et innovants</li>
          <li>Être encadré par des chercheurs expérimentés</li>
          <li>Développer des compétences techniques avancées</li>
          <li>Potentiellement déboucher sur une thèse ou un emploi</li>
        </ul>
        <p>
          Consultez notre page <strong>"Nous rejoindre"</strong> pour les offres
          en cours ou contactez-nous pour des opportunités spécifiques.
        </p>
      </>
    ),
  },
  {
    icon: "fa-flask",
    question: "Quels sont vos principaux domaines de recherche ?",
    answer: (
      <>
        <p>Nos principaux axes de recherche couvrent :</p>
        <ul>
          <li>
            <strong>Intelligence Artificielle</strong> — Deep learning,
            traitement du langage naturel, vision par ordinateur
          </li>
          <li>
            <strong>Cybersécurité</strong> — Cryptographie, détection
            d’intrusions, sécurité applicative
          </li>
          <li>
            <strong>Systèmes Distribués</strong> — Cloud computing, edge
            computing, technologies blockchain
          </li>
          <li>
            <strong>Génie Logiciel</strong> — DevOps, architecture logicielle,
            qualité du code
          </li>
        </ul>
        <p>
          Pour plus de détails, consultez notre page <strong>"À propos"</strong>
          .
        </p>
      </>
    ),
  },
  {
    icon: "fa-building",
    question: "Peut-on visiter votre laboratoire ?",
    answer: (
      <>
        <p>Nous organisons régulièrement des événements ouverts au public :</p>
        <ul>
          <li>
            <strong>Journées portes ouvertes</strong> — Deux fois par an
            (généralement en mars et octobre)
          </li>
          <li>
            <strong>Visites guidées</strong> — Sur rendez-vous pour les groupes
          </li>
          <li>
            <strong>Conférences publiques</strong> — Consultez notre calendrier
            d’événements
          </li>
        </ul>
        <p>
          Contactez-nous pour planifier une visite ou connaître les dates de nos
          prochains événements publics.
        </p>
      </>
    ),
  },
];

/** Composant accordéon individuel (question/réponse) */
function FAQItem({ faq, index, openIndex, setOpenIndex }) {
  const isOpen = openIndex === index;
  return (
    <div className={`faq-item ${isOpen ? "open" : ""}`}>
      <button
        className="faq-question"
        onClick={() => setOpenIndex(isOpen ? -1 : index)}
      >
        <div className="faq-question-left">
          <div className="faq-question-icon">
            <i className={`fas ${faq.icon}`}></i>
          </div>
          <h3>{faq.question}</h3>
        </div>
        <div className="faq-toggle">
          <i className="fas fa-chevron-down"></i>
        </div>
      </button>
      <div className="faq-answer">
        <div className="faq-answer-inner">{faq.answer}</div>
      </div>
    </div>
  );
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <>
      <Navbar />

      {/* Hero */}
      <section
        className="page-hero hero-with-slideshow faq-hero"
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
          <span className="hero-tag">FOIRE AUX QUESTIONS</span>
          <h1>
            Questions <span className="gradient">fréquentes</span>
          </h1>
          <p>
            Recherche informatique et innovations technologiques — retrouvez les
            réponses aux questions les plus posées.
          </p>
        </div>
      </section>

      {/* FAQ Accordion */}
      <section className="faq-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="faq-header">
            <span className="faq-badge">
              <i
                className="fas fa-comments"
                style={{ marginRight: "0.5rem" }}
              ></i>
              FAQ
            </span>
            <h2>Vos questions, nos réponses</h2>
            <p>
              Tout ce que vous devez savoir sur le laboratoire BetaLab et ses
              activités.
            </p>
          </div>
          <div className="faq-list">
            {faqs.map((faq, i) => (
              <FAQItem
                key={i}
                faq={faq}
                index={i}
                openIndex={openIndex}
                setOpenIndex={setOpenIndex}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="faq-cta-section" style={{ background: "#14213d" }}>
        <div className="container">
          <div className="faq-cta-box">
            <div className="faq-cta-icon">
              <i className="fas fa-envelope"></i>
            </div>
            <h2>Encore des questions ?</h2>
            <p>
              N’hésitez pas à nous contacter directement. Notre équipe se fera
              un plaisir de vous répondre.
            </p>
            <Link to="/contact" className="faq-cta-btn">
              <i className="fas fa-paper-plane"></i> Contactez-nous
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
