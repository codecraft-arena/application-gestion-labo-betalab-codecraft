/**
 * Page formulaire d'adhésion BetaLab.
 * Accessible uniquement via un lien d'invitation : /adhesion/:token
 *
 * Flux :
 *  1. Vérifie le token auprès de l'API (GET /api/adhesion/:token)
 *  2. Pré-remplit nom + email depuis le token
 *  3. L'utilisateur complète le formulaire et choisit son mot de passe
 *  4. POST /api/adhesion/:token → compte créé → credentials envoyés par email
 *  5. Affiche la page de succès avec lien vers /login
 */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import "./AdhesionForm.css";

const OCCUPATIONS = [
  { value: "etudiant",  label: "Étudiant(e)" },
  { value: "stagiaire", label: "Stagiaire" },
  { value: "chercheur", label: "Chercheur / Enseignant-chercheur" },
];

const STEPS = ["Vérification", "Informations", "Finalisation"];

export default function AdhesionForm() {
  const { token } = useParams();

  // ── Token state ────────────────────────────────────────────────────────────
  const [tokenState, setTokenState] = useState("loading"); // loading | valid | invalid | expired | used
  const [prefilled,  setPrefilled]  = useState({ email: "", name: "" });

  // ── Form state ─────────────────────────────────────────────────────────────
  const [step, setStep] = useState(1); // 1 = identité, 2 = parcours, 3 = mot de passe
  const [form, setForm] = useState({
    name: "", birthdate: "", occupation: "etudiant",
    institution: "", level: "", domain: "", motivation: "",
    password: "", confirmPassword: "",
  });
  const [showPwd, setShowPwd] = useState(false);

  // ── Submit state ───────────────────────────────────────────────────────────
  const [submitting, setSubmitting] = useState(false);
  const [submitDone, setSubmitDone] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [error, setError] = useState("");

  // ── Verify token on mount ──────────────────────────────────────────────────
  useEffect(() => {
    if (!token) { setTokenState("invalid"); return; }
    (async () => {
      try {
        const res = await fetch(`/api/adhesion/${token}`, { credentials: "include" });
        if (!res.ok) {
          const d = await res.json().catch(() => ({}));
          const msg = (d.detail || "").toLowerCase();
          if (msg.includes("expiré"))  setTokenState("expired");
          else if (msg.includes("utilisé")) setTokenState("used");
          else setTokenState("invalid");
          return;
        }
        const data = await res.json();
        setPrefilled({ email: data.email, name: data.name || "" });
        setForm((f) => ({ ...f, name: data.name || "" }));
        setTokenState("valid");
      } catch {
        setTokenState("invalid");
      }
    })();
  }, [token]);

  const fc = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  // ── Validation par step ───────────────────────────────────────────────────
  const canNext = () => {
    if (step === 1) return form.name.trim() && form.birthdate && form.occupation;
    if (step === 2) return form.institution.trim();
    return false;
  };

  // ── Submit ────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      setError("Les mots de passe ne correspondent pas."); return;
    }
    if (form.password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères."); return;
    }
    setSubmitting(true); setError("");
    try {
      const res = await fetch(`/api/adhesion/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: form.name, birthdate: form.birthdate,
          occupation: form.occupation, institution: form.institution,
          level: form.level, domain: form.domain, motivation: form.motivation,
          password: form.password,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Erreur lors de la création du compte");
      setSubmitResult(data);
      setSubmitDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  // TOKEN STATES (loading / invalid / expired / used)
  // ══════════════════════════════════════════════════════════════════════════
  if (tokenState === "loading") {
    return (
      <div className="adh-page">
        <div className="adh-loading">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Vérification de votre invitation…</p>
        </div>
      </div>
    );
  }

  if (tokenState !== "valid") {
    const msgs = {
      invalid: { icon: "fa-link-slash",  title: "Lien invalide",       sub: "Ce lien d'invitation n'existe pas ou a été modifié." },
      expired: { icon: "fa-clock",       title: "Lien expiré",         sub: "Ce lien était valable 72 h. Contactez l'équipe BetaLab pour un nouveau lien." },
      used:    { icon: "fa-check-circle",title: "Lien déjà utilisé",   sub: "Un compte a déjà été créé avec ce lien. Connectez-vous directement." },
    };
    const m = msgs[tokenState] || msgs.invalid;
    return (
      <div className="adh-page">
        <div className="adh-error-card">
          <div className="adh-error-icon"><i className={`fas ${m.icon}`}></i></div>
          <h2>{m.title}</h2>
          <p>{m.sub}</p>
          <div className="adh-error-actions">
            <Link to="/contact" className="adh-btn-gold">Contacter BetaLab</Link>
            {tokenState === "used" && <Link to="/login" className="adh-btn-outline">Se connecter</Link>}
          </div>
        </div>
      </div>
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // SUCCESS STATE
  // ══════════════════════════════════════════════════════════════════════════
  if (submitDone) {
    return (
      <div className="adh-page">
        <div className="adh-success-card">
          <div className="adh-success-icon"><i className="fas fa-party-horn"></i></div>
          <h2>Bienvenue chez BetaLab&nbsp;! 🎉</h2>
          <p>{submitResult?.message}</p>
          <div className="adh-credentials-box">
            <div>
              <span className="adh-cred-label">Email</span>
              <span className="adh-cred-value">{prefilled.email}</span>
            </div>
            <div>
              <span className="adh-cred-label">Mot de passe</span>
              <span className="adh-cred-value adh-cred-pwd">Celui que vous venez de définir</span>
            </div>
          </div>
          <p style={{ fontSize: ".82rem", color: "#8892a4", marginBottom: "1.4rem" }}>
            📧 Vos identifiants vous ont été envoyés par email à <strong>{prefilled.email}</strong>.
          </p>
          <Link to="/login" className="adh-btn-gold">
            <i className="fas fa-arrow-right-to-bracket"></i> Accéder à la connexion
          </Link>
        </div>
      </div>
    );
  }

  // ══════════════════════════════════════════════════════════════════════════
  // FORM
  // ══════════════════════════════════════════════════════════════════════════
  return (
    <div className="adh-page">
      <div className="adh-card">
        {/* Header */}
        <div className="adh-header">
          <div className="adh-logo">
            <i className="fas fa-flask"></i>
          </div>
          <h1>Formulaire d'adhésion</h1>
          <p>Complétez votre dossier pour rejoindre <strong>BetaLab</strong></p>
        </div>

        {/* Invitation info */}
        <div className="adh-invite-banner">
          <i className="fas fa-envelope-open" style={{ color: "#e9b000", flexShrink: 0 }}></i>
          <div>
            <span style={{ fontWeight: 700, color: "#14213d", fontSize: ".88rem" }}>
              Invitation pour : {prefilled.email}
            </span>
            <span style={{ fontSize: ".78rem", color: "#8892a4", display: "block", marginTop: ".1rem" }}>
              Votre email de connexion sera <strong>{prefilled.email}</strong>
            </span>
          </div>
        </div>

        {/* Stepper */}
        <div className="adh-stepper">
          {STEPS.map((s, i) => (
            <div key={s} className={`adh-step ${step === i + 1 ? "active" : step > i + 1 ? "done" : ""}`}>
              <div className="adh-step-dot">
                {step > i + 1 ? <i className="fas fa-check"></i> : i + 1}
              </div>
              <span>{s}</span>
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="adh-alert-error">
            <i className="fas fa-exclamation-circle"></i> {error}
          </div>
        )}

        <form onSubmit={step < 3 ? (e) => { e.preventDefault(); setStep((s) => s + 1); } : handleSubmit}>

          {/* ── STEP 1 : Identité ── */}
          {step === 1 && (
            <div className="adh-fields">
              <div className="adh-field-group">
                <label>Nom complet *</label>
                <input name="name" type="text" placeholder="Prénom Nom"
                  value={form.name} onChange={fc} required />
              </div>
              <div className="adh-field-group">
                <label>Date de naissance *</label>
                <input name="birthdate" type="date" value={form.birthdate} onChange={fc} required />
              </div>
              <div className="adh-field-group adh-full">
                <label>Vous êtes *</label>
                <div className="adh-occ-grid">
                  {OCCUPATIONS.map((o) => (
                    <label key={o.value}
                      className={`adh-occ-card ${form.occupation === o.value ? "selected" : ""}`}>
                      <input type="radio" name="occupation" value={o.value}
                        checked={form.occupation === o.value} onChange={fc} />
                      {o.label}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ── STEP 2 : Parcours ── */}
          {step === 2 && (
            <div className="adh-fields">
              <div className="adh-field-group adh-full">
                <label>Institution / Établissement *</label>
                <input name="institution" type="text" placeholder="Nom de votre université, entreprise…"
                  value={form.institution} onChange={fc} required />
              </div>
              <div className="adh-field-group">
                <label>Niveau d'études</label>
                <input name="level" type="text" placeholder="Ex : M2, Doctorat, Ingénieur…"
                  value={form.level} onChange={fc} />
              </div>
              <div className="adh-field-group">
                <label>Domaine / Spécialité</label>
                <input name="domain" type="text" placeholder="Ex : Informatique, IA, Réseaux…"
                  value={form.domain} onChange={fc} />
              </div>
              <div className="adh-field-group adh-full">
                <label>Motivation pour rejoindre BetaLab</label>
                <textarea name="motivation"
                  placeholder="Décrivez ce qui vous attire dans BetaLab, vos objectifs, vos compétences…"
                  value={form.motivation} onChange={fc} rows={4} />
              </div>
            </div>
          )}

          {/* ── STEP 3 : Mot de passe ── */}
          {step === 3 && (
            <div className="adh-fields">
              <div className="adh-summary">
                <h4>Récapitulatif</h4>
                <div className="adh-summary-grid">
                  {[
                    ["Email", prefilled.email],
                    ["Nom", form.name],
                    ["Naissance", form.birthdate],
                    ["Statut", OCCUPATIONS.find((o) => o.value === form.occupation)?.label],
                    ["Institution", form.institution || "—"],
                    ["Domaine", form.domain || "—"],
                  ].map(([l, v]) => (
                    <div key={l}><span className="adh-sum-label">{l}</span><span className="adh-sum-value">{v}</span></div>
                  ))}
                </div>
              </div>

              <div className="adh-field-group adh-full">
                <label>Choisissez votre mot de passe * (8 caractères min)</label>
                <div className="adh-pwd-wrap">
                  <input name="password" type={showPwd ? "text" : "password"}
                    placeholder="Mot de passe" value={form.password} onChange={fc} required minLength={8} />
                  <button type="button" className="adh-pwd-toggle" onClick={() => setShowPwd((v) => !v)}>
                    <i className={`fas ${showPwd ? "fa-eye-slash" : "fa-eye"}`}></i>
                  </button>
                </div>
              </div>
              <div className="adh-field-group adh-full">
                <label>Confirmez le mot de passe *</label>
                <div className="adh-pwd-wrap">
                  <input name="confirmPassword" type={showPwd ? "text" : "password"}
                    placeholder="Répétez le mot de passe" value={form.confirmPassword} onChange={fc} required />
                </div>
                {form.confirmPassword && form.password !== form.confirmPassword && (
                  <span className="adh-pwd-mismatch">Les mots de passe ne correspondent pas</span>
                )}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="adh-nav">
            {step > 1 && (
              <button type="button" className="adh-btn-outline" onClick={() => setStep((s) => s - 1)}>
                <i className="fas fa-arrow-left"></i> Retour
              </button>
            )}
            {step < 3 ? (
              <button type="submit" className="adh-btn-gold" disabled={!canNext()}>
                Suivant <i className="fas fa-arrow-right"></i>
              </button>
            ) : (
              <button type="submit" className="adh-btn-gold"
                disabled={submitting || form.password !== form.confirmPassword || form.password.length < 8}>
                <i className={`fas ${submitting ? "fa-spinner fa-spin" : "fa-check"}`}></i>
                {submitting ? "Création du compte…" : "Créer mon compte"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
