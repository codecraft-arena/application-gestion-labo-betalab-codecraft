/**
 * Page Contact de BetaLab.
 * Le formulaire soumet les données à /api/contact.
 * Si l'objet mentionne "rejoindre / adhésion", l'admin reçoit
 * une demande d'adhésion et peut envoyer une invitation par email.
 */
import { useState } from "react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import NeuralCanvas from "../components/NeuralCanvas";
import HeroSlideshow from "../components/HeroSlideshow";
import "./Contact.css";

const contactInfo = [
  { icon: "fa-map-marker-alt", label: "Adresse",   lines: ["CHU, Faculté de Médecine", "Yaoundé, Cameroun"] },
  { icon: "fa-phone-alt",      label: "Téléphone", lines: ["+237 675 75 99 00", "+33 7 49 55 61 71"] },
  { icon: "fa-envelope",       label: "Email",     lines: ["contact@beta-lab.cm"], link: "mailto:contact@beta-lab.cm" },
];

/* Objets pré-définis — le premier déclenche is_join_request */
const SUBJECTS = [
  { value: "Rejoindre BetaLab — Demande d'adhésion", label: "🎓 Rejoindre BetaLab (adhésion)", isJoin: true },
  { value: "Partenariat",      label: "🤝 Partenariat" },
  { value: "Collaboration",    label: "🔬 Collaboration de recherche" },
  { value: "Renseignements",   label: "ℹ️  Renseignements généraux" },
  { value: "Autre",            label: "💬 Autre" },
];

export default function Contact() {
  const [form,    setForm]    = useState({ name: "", email: "", subject: SUBJECTS[0].value, message: "" });
  const [status,  setStatus]  = useState("idle"); // idle | sending | success | error
  const [errMsg,  setErrMsg]  = useState("");

  const isJoinSelected = SUBJECTS.find((s) => s.value === form.subject)?.isJoin ?? false;

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending"); setErrMsg("");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || "Erreur lors de l'envoi");
      }
      setStatus("success");
      setForm({ name: "", email: "", subject: SUBJECTS[0].value, message: "" });
    } catch (err) {
      setStatus("error"); setErrMsg(err.message);
    }
  };

  return (
    <>
      <Navbar />

      {/* Hero */}
      <section className="page-hero hero-with-slideshow contact-hero"
        style={{ position: "relative", overflow: "hidden" }}>
        <HeroSlideshow />
        <NeuralCanvas nodeCount={60} connectionDist={130} mouseRadius={180} opacity={0.5} />
        <div className="container" style={{ textAlign: "center", position: "relative", zIndex: 1 }}>
          <span className="hero-tag">NOUS CONTACTER</span>
          <h1>Contactez notre <span className="gradient">laboratoire</span></h1>
          <p>Recherche informatique et innovations technologiques — échangeons ensemble.</p>
        </div>
      </section>

      {/* Contact Grid */}
      <section className="contact-section" style={{ background: "#f5f5f5" }}>
        <div className="container">
          <div className="contact-grid">
            {/* Info Column */}
            <div className="contact-info-col">
              <span className="contact-badge">
                <i className="fas fa-headset" style={{ marginRight: ".5rem" }}></i>Informations
              </span>
              <h2>Nos coordonnées</h2>
              <p>N'hésitez pas à nous écrire, nous vous répondrons dans les meilleurs délais.</p>

              {/* Join notice */}
              <div style={{
                background: "rgba(233,176,0,.08)", border: "1px solid rgba(233,176,0,.25)",
                borderRadius: "14px", padding: "1.2rem 1.4rem", marginBottom: "1.5rem",
              }}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: ".75rem" }}>
                  <i className="fas fa-graduation-cap" style={{ color: "#e9b000", fontSize: "1.1rem", marginTop: ".1rem", flexShrink: 0 }}></i>
                  <div>
                    <p style={{ fontWeight: 700, color: "#14213d", margin: "0 0 .35rem", fontSize: ".92rem" }}>
                      Vous souhaitez rejoindre BetaLab ?
                    </p>
                    <p style={{ color: "#555", fontSize: ".82rem", lineHeight: 1.65, margin: 0 }}>
                      Sélectionnez l'objet <em>« Rejoindre BetaLab »</em> et décrivez votre profil.
                      L'équipe examinera votre demande et vous enverra un lien d'invitation par email
                      pour compléter votre dossier d'adhésion.
                    </p>
                  </div>
                </div>
              </div>

              <div className="contact-cards">
                {contactInfo.map((c) => (
                  <div className="contact-card" key={c.label}>
                    <div className="contact-card-icon"><i className={`fas ${c.icon}`}></i></div>
                    <div className="contact-card-text">
                      <h3>{c.label}</h3>
                      {c.link
                        ? <p><a href={c.link}>{c.lines[0]}</a></p>
                        : c.lines.map((l, i) => <p key={i}>{l}</p>)
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Form Column */}
            <div className="contact-form-col">
              <h2>
                <i className="fas fa-paper-plane" style={{ marginRight: ".6rem", color: "#e9b000" }}></i>
                Envoyez-nous un message
              </h2>

              {/* Success state */}
              {status === "success" && (
                <div style={{
                  background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "14px",
                  padding: "1.4rem 1.6rem", marginBottom: "1.2rem",
                  display: "flex", alignItems: "flex-start", gap: ".9rem",
                }}>
                  <i className="fas fa-check-circle" style={{ color: "#22c55e", fontSize: "1.3rem", flexShrink: 0, marginTop: ".1rem" }}></i>
                  <div>
                    <p style={{ fontWeight: 700, color: "#166534", margin: "0 0 .3rem" }}>Message envoyé !</p>
                    <p style={{ color: "#15803d", fontSize: ".85rem", margin: 0 }}>
                      Nous vous avons envoyé un accusé de réception par email.
                      {isJoinSelected && " Si votre demande est retenue, vous recevrez un lien d'invitation sous peu."}
                    </p>
                  </div>
                </div>
              )}

              {status === "error" && (
                <div style={{
                  background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "12px",
                  padding: "1rem 1.4rem", marginBottom: "1.2rem",
                  display: "flex", alignItems: "center", gap: ".7rem", color: "#dc2626", fontSize: ".85rem",
                }}>
                  <i className="fas fa-exclamation-circle"></i> {errMsg}
                </div>
              )}

              <form className="contact-form" onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="name">Nom *</label>
                    <input id="name" type="text" name="name" placeholder="Votre nom complet"
                      value={form.name} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label htmlFor="email">Email *</label>
                    <input id="email" type="email" name="email" placeholder="votre@email.com"
                      value={form.email} onChange={handleChange} required />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="subject">Objet *</label>
                  <select id="subject" name="subject" value={form.subject} onChange={handleChange} required
                    style={{
                      width: "100%", padding: ".9rem 1.2rem",
                      border: `1.5px solid ${isJoinSelected ? "rgba(233,176,0,.5)" : "rgba(20,33,61,.12)"}`,
                      borderRadius: "12px", fontFamily: "inherit", fontSize: ".95rem",
                      color: "#14213d", background: "#fff", outline: "none",
                      transition: "border-color .25s",
                    }}>
                    {SUBJECTS.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                  {isJoinSelected && (
                    <p style={{ fontSize: ".78rem", color: "#e9b000", margin: ".4rem 0 0", display: "flex", alignItems: "center", gap: ".35rem" }}>
                      <i className="fas fa-info-circle"></i>
                      Demande d'adhésion — décrivez votre profil, vos compétences et vos motivations.
                    </p>
                  )}
                </div>

                <div className="form-group">
                  <label htmlFor="message">Message *</label>
                  <textarea id="message" name="message"
                    placeholder={isJoinSelected
                      ? "Présentez-vous : formation, niveau d'études, domaine d'intérêt, motivations pour rejoindre BetaLab…"
                      : "Votre message…"}
                    value={form.message} onChange={handleChange} required></textarea>
                </div>

                <button type="submit" className="contact-submit" disabled={status === "sending"}>
                  <i className={`fas ${status === "sending" ? "fa-spinner fa-spin" : "fa-paper-plane"}`}></i>
                  {status === "sending" ? "Envoi en cours…" : "Envoyer le message"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Map */}
      <section className="contact-map-section" style={{ background: "#14213d" }}>
        <div className="container">
          <div className="contact-map-box">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3980.7663026037446!2d11.5020!3d3.8480!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zM8KwNTAnNTMuMCJOIDExwrAzMCcwNy4wIkU!5e0!3m2!1sfr!2scm!4v1"
              allowFullScreen="" loading="lazy" referrerPolicy="no-referrer-when-downgrade"
              title="Localisation BetaLab">
            </iframe>
            <div className="contact-map-footer">
              <div className="contact-map-info">
                <i className="fas fa-map-pin"></i>
                <div>
                  <h3>Campus Universitaire, Yaoundé</h3>
                  <p>CHU, Faculté de Médecine, Cameroun</p>
                </div>
              </div>
              <a href="https://www.google.com/maps/search/CHU+Faculté+de+Médecine+Yaoundé+Cameroun"
                target="_blank" rel="noopener noreferrer" className="contact-map-btn">
                <i className="fas fa-directions"></i> Itinéraire
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </>
  );
}
