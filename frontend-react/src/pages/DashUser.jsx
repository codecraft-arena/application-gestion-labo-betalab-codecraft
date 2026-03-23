/**
 * Tableau de bord utilisateur BetaLab — refonte complète.
 * Vues : Accueil · Profil · Invitations · Contributions · Questions · Suggestions
 */
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import "./DashUser.css";

// Helper function to safely convert any error to string
const toErrorString = (err) => {
  if (typeof err === "string") return err;
  if (err === null || err === undefined) return "Une erreur est survenue";
  if (err instanceof Error) return err.message || String(err);
  if (typeof err === "object" && err.message) return String(err.message);
  if (typeof err === "object" && err.detail) return String(err.detail);
  return "Une erreur est survenue";
};

// ── Icône étoile cliquable ────────────────────────────────────────────────────
function StarRating({ value, onChange, readOnly = false }) {
  return (
    <div className={readOnly ? "star-display" : "star-rating"}>
      {[1, 2, 3, 4, 5].map((s) =>
        readOnly ? (
          <i key={s} className={`fas fa-star${s <= value ? " filled" : ""}`} />
        ) : (
          <span
            key={s}
            className={`star${s <= value ? " filled" : ""}`}
            onClick={() => onChange(s)}
          >
            ★
          </span>
        ),
      )}
    </div>
  );
}

// ── Mapping occupation → label ────────────────────────────────────────────────
const OCC_LABEL = {
  etudiant: "Étudiant",
  stagiaire: "Stagiaire",
  chercheur: "Chercheur",
};

// ── Nav items ─────────────────────────────────────────────────────────────────
const NAV = [
  { id: "home", icon: "fa-house", label: "Accueil" },
  { id: "profile", icon: "fa-user", label: "Mon Profil" },
  { id: "pending", icon: "fa-clock", label: "En Attente" },
  { id: "invitations", icon: "fa-envelope-open", label: "Invitations" },
  { id: "contributions", icon: "fa-layer-group", label: "Contributions" },
  { id: "questions", icon: "fa-circle-question", label: "Questions" },
  { id: "suggestions", icon: "fa-lightbulb", label: "Suggestions" },
];

// ═════════════════════════════════════════════════════════════════════════════
export default function DashUser() {
  const navigate = useNavigate();

  // ── Data state ──────────────────────────────────────────────────────────────
  const [user, setUser] = useState(null);
  const [contributions, setContributions] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [pendingMods, setPendingMods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("home");
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  // ── Profile edit state ──────────────────────────────────────────────────────
  const [editMode, setEditMode] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [editSaving, setEditSaving] = useState(false);

  // ── Question form state ─────────────────────────────────────────────────────
  const [qOpen, setQOpen] = useState(false);
  const [qForm, setQForm] = useState({
    libele_question: "",
    description_question: "",
  });
  const [qSending, setQSending] = useState(false);

  // ── Suggestion form state ───────────────────────────────────────────────────
  const [sOpen, setSOpen] = useState(false);
  const [sForm, setSForm] = useState({
    libele: "",
    description_suggest: "",
    note: 0,
  });
  const [sSending, setSSending] = useState(false);

  // ── Invitation action loading ───────────────────────────────────────────────
  const [invLoading, setInvLoading] = useState({});

  // ── Load all data ───────────────────────────────────────────────────────────
  const loadAll = useCallback(async () => {
    try {
      const me = await apiFetch("/api/me");
      setUser(me);
      const enc = encodeURIComponent(me.email);
      const [contribs, invs, qs, ss, pending] = await Promise.all([
        apiFetch(`/api/contributions/${enc}`),
        apiFetch(`/api/invitations/${enc}`),
        apiFetch(`/api/questions/user/${enc}`),
        apiFetch(`/api/suggestions/user/${enc}`),
        apiFetch(`/api/users/${enc}/pending-modifications`),
      ]);
      setContributions(contribs);
      setInvitations(invs);
      setQuestions(qs);
      setSuggestions(ss);
      setPendingMods(pending);
    } catch (err) {
      const errMsg = toErrorString(err);
      if (errMsg.includes("401") || errMsg.includes("authentifié")) {
        navigate("/login");
      } else {
        setError(errMsg);
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // ── Auto-clear action message ───────────────────────────────────────────────
  useEffect(() => {
    if (!actionMsg) return;
    const t = setTimeout(() => setActionMsg(""), 3500);
    return () => clearTimeout(t);
  }, [actionMsg]);

  // ── Déconnexion ─────────────────────────────────────────────────────────────
  const handleLogout = async () => {
    try {
      await apiFetch("/logout");
    } catch {
      /* ignore */
    }
    navigate("/");
  };

  // ── Modifier le profil ──────────────────────────────────────────────────────
  const startEdit = () => {
    setEditForm({
      name: user.name || "",
      occupation: user.occupation || "",
      institution: user.institution || "",
      level: user.level || "",
      domain: user.domain || "",
      motivation: user.motivation || "",
    });
    setEditMode(true);
  };

  const handleEditChange = (e) =>
    setEditForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleEditSave = async () => {
    setEditSaving(true);
    setError("");
    try {
      const updated = await apiFetch(
        `/api/users/${encodeURIComponent(user.email)}/profile`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(editForm),
        },
      );
      setUser(updated);
      setEditMode(false);
      setActionMsg("✓ Profil mis à jour avec succès");
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setEditSaving(false);
    }
  };

  // ── Invitations ─────────────────────────────────────────────────────────────
  const handleInvitation = async (activityId, action) => {
    setInvLoading((prev) => ({ ...prev, [activityId]: true }));
    setError("");
    try {
      const enc = encodeURIComponent(user.email);
      const actEnc = encodeURIComponent(activityId);
      await apiFetch(`/api/invitations/${enc}/${actEnc}/${action}`, {
        method: "PUT",
      });
      setActionMsg(
        action === "accept"
          ? `✓ Invitation acceptée — vous participez à cette activité`
          : `✓ Invitation refusée`,
      );
      // Refresh invitations + contributions
      const [invs, contribs] = await Promise.all([
        apiFetch(`/api/invitations/${enc}`),
        apiFetch(`/api/contributions/${enc}`),
      ]);
      setInvitations(invs);
      setContributions(contribs);
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setInvLoading((prev) => ({ ...prev, [activityId]: false }));
    }
  };

  // ── Poser une question ──────────────────────────────────────────────────────
  const handleQuestionSubmit = async () => {
    if (!qForm.libele_question.trim()) return;
    setQSending(true);
    setError("");
    try {
      await apiFetch("/api/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(qForm),
      });
      setQForm({ libele_question: "", description_question: "" });
      setQOpen(false);
      setActionMsg("✓ Question envoyée");
      const qs = await apiFetch(
        `/api/questions/user/${encodeURIComponent(user.email)}`,
      );
      setQuestions(qs);
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setQSending(false);
    }
  };

  // ── Apporter une suggestion ─────────────────────────────────────────────────
  const handleSuggestionSubmit = async () => {
    if (!sForm.libele.trim()) return;
    setSSending(true);
    setError("");
    try {
      await apiFetch("/api/suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sForm),
      });
      setSForm({ libele: "", description_suggest: "", note: 0 });
      setSOpen(false);
      setActionMsg("✓ Suggestion envoyée");
      const ss = await apiFetch(
        `/api/suggestions/user/${encodeURIComponent(user.email)}`,
      );
      setSuggestions(ss);
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setSSending(false);
    }
  };

  // ── Helpers ─────────────────────────────────────────────────────────────────
  const initial = user ? user.name.charAt(0).toUpperCase() : "U";
  const firstName = user ? user.name.split(" ")[0] : "—";
  const occLabel = user ? OCC_LABEL[user.occupation] || "Membre" : "—";
  const pendingCount = invitations.length;

  const PAGE_TITLES = {
    home: { title: "Mon Espace", sub: "Tableau de bord personnel" },
    profile: { title: "Mon Profil", sub: "Informations personnelles" },
    pending: {
      title: "En Attente",
      sub: "Mes demandes en attente d'approbation",
    },
    invitations: {
      title: "Invitations",
      sub: "Activités en attente de réponse",
    },
    contributions: {
      title: "Contributions",
      sub: "Activités auxquelles vous participez",
    },
    questions: { title: "Questions", sub: "Posez vos questions à l'équipe" },
    suggestions: {
      title: "Suggestions",
      sub: "Partagez vos idées d'amélioration",
    },
  };

  // ════════════════════════════════════════════════════════════════════════════
  // VIEWS
  // ════════════════════════════════════════════════════════════════════════════

  // ── Accueil ──────────────────────────────────────────────────────────────────
  const renderHome = () => (
    <>
      <div className="welcome-banner">
        <div className="welcome-text">
          <h2>
            Bonjour, <span>{firstName}</span> 👋
          </h2>
          <p>
            Bienvenue dans votre espace BetaLab. Gérez votre profil, répondez
            aux invitations et contribuez à la recherche.
          </p>
        </div>
        <div className="welcome-badge">
          <div className="wb-icon">
            {user?.occupation === "etudiant"
              ? "🎓"
              : user?.occupation === "chercheur"
                ? "🔬"
                : "📋"}
          </div>
          <div className="wb-label">{occLabel}</div>
        </div>
      </div>

      <div
        className={`status-bar ${user?.validated ? "validated" : "not-validated"}`}
      >
        <div className={`status-icon ${user?.validated ? "green" : "orange"}`}>
          <i className={`fas ${user?.validated ? "fa-check" : "fa-clock"}`}></i>
        </div>
        <div className={`status-text ${user?.validated ? "green" : "orange"}`}>
          <h3>
            {user?.validated
              ? "Compte validé et actif"
              : "Validation en attente"}
          </h3>
          <p>
            {user?.validated
              ? "Vous avez accès à toutes les fonctionnalités du laboratoire."
              : "Un administrateur doit valider votre inscription avant l'accès complet."}
          </p>
        </div>
      </div>

      <div className="quick-stats">
        <div className="qs-card" onClick={() => setView("invitations")}>
          <div className="qs-icon gold">
            <i className="fas fa-envelope-open"></i>
          </div>
          <div className="qs-value">{pendingCount}</div>
          <div className="qs-label">
            Invitation{pendingCount !== 1 ? "s" : ""} en attente
          </div>
        </div>
        <div className="qs-card" onClick={() => setView("contributions")}>
          <div className="qs-icon blue">
            <i className="fas fa-layer-group"></i>
          </div>
          <div className="qs-value">{contributions.length}</div>
          <div className="qs-label">
            Contribution{contributions.length !== 1 ? "s" : ""}
          </div>
        </div>
        <div className="qs-card" onClick={() => setView("questions")}>
          <div className="qs-icon green">
            <i className="fas fa-circle-question"></i>
          </div>
          <div className="qs-value">{questions.length}</div>
          <div className="qs-label">
            Question{questions.length !== 1 ? "s" : ""} posée
            {questions.length !== 1 ? "s" : ""}
          </div>
        </div>
        <div className="qs-card" onClick={() => setView("suggestions")}>
          <div className="qs-icon purple">
            <i className="fas fa-lightbulb"></i>
          </div>
          <div className="qs-value">{suggestions.length}</div>
          <div className="qs-label">
            Suggestion{suggestions.length !== 1 ? "s" : ""}
          </div>
        </div>
      </div>
    </>
  );

  // ── Profil ───────────────────────────────────────────────────────────────────
  const renderProfile = () => (
    <div className="profile-card">
      <div className="profile-header">
        <div className="profile-avatar-lg">{initial}</div>
        <div className="profile-header-info">
          <h3>{user?.name}</h3>
          <p>{user?.email}</p>
        </div>
        <div className="profile-header-actions">
          {!editMode && (
            <button className="btn-edit" onClick={startEdit}>
              <i className="fas fa-pen"></i> Modifier le profil
            </button>
          )}
        </div>
      </div>

      <div className="pf-section-label">
        <i className="fas fa-info-circle"></i> Informations personnelles
      </div>
      <div className="pf-grid">
        {[
          { label: "Nom complet", val: user?.name },
          { label: "Email", val: user?.email, cls: "gold" },
          { label: "Date de naissance", val: user?.birthdate },
          { label: "Occupation", val: occLabel },
        ].map((f) => (
          <div className="pf-item" key={f.label}>
            <div className="pf-label">{f.label}</div>
            <div className={`pf-value${f.cls ? " " + f.cls : ""}`}>
              {f.val || "—"}
            </div>
          </div>
        ))}
      </div>

      <div className="pf-section-label">
        <i className="fas fa-graduation-cap"></i> Parcours académique
      </div>
      <div className="pf-grid">
        {[
          { label: "Institution", val: user?.institution },
          { label: "Niveau", val: user?.level },
          { label: "Domaine", val: user?.domain },
        ].map((f) => (
          <div className="pf-item" key={f.label}>
            <div className="pf-label">{f.label}</div>
            <div className="pf-value">{f.val || "—"}</div>
          </div>
        ))}
      </div>

      {user?.motivation && (
        <>
          <div className="pf-section-label">
            <i className="fas fa-star"></i> Motivation
          </div>
          <div className="pf-item" style={{ gridColumn: "1/-1" }}>
            <div className="pf-value">{user.motivation}</div>
          </div>
        </>
      )}

      {/* ── Formulaire d'édition inline ── */}
      {editMode && (
        <div className="edit-form">
          <h4>
            <i className="fas fa-pen" style={{ color: "var(--gold)" }}></i>{" "}
            Modifier vos informations
          </h4>
          <div className="edit-grid">
            {[
              { name: "name", label: "Nom complet", type: "text" },
              { name: "institution", label: "Institution", type: "text" },
              { name: "level", label: "Niveau", type: "text" },
              { name: "domain", label: "Domaine", type: "text" },
            ].map((f) => (
              <div className="form-group" key={f.name}>
                <label>{f.label}</label>
                <input
                  type={f.type}
                  name={f.name}
                  value={editForm[f.name] || ""}
                  onChange={handleEditChange}
                  placeholder={f.label}
                />
              </div>
            ))}
            <div className="form-group">
              <label>Occupation</label>
              <select
                name="occupation"
                value={editForm.occupation || ""}
                onChange={handleEditChange}
              >
                <option value="etudiant">Étudiant</option>
                <option value="stagiaire">Stagiaire</option>
                <option value="chercheur">Chercheur</option>
              </select>
            </div>
            <div className="form-group full">
              <label>Motivation</label>
              <textarea
                name="motivation"
                value={editForm.motivation || ""}
                onChange={handleEditChange}
                placeholder="Décrivez votre motivation..."
              />
            </div>
          </div>
          <div className="form-actions">
            <button
              className="btn-save"
              onClick={handleEditSave}
              disabled={editSaving}
            >
              <i
                className={`fas ${editSaving ? "fa-spinner fa-spin" : "fa-check"}`}
              ></i>
              {editSaving ? "Enregistrement..." : "Enregistrer"}
            </button>
            <button className="btn-cancel" onClick={() => setEditMode(false)}>
              <i className="fas fa-times"></i> Annuler
            </button>
          </div>
        </div>
      )}
    </div>
  );

  // ── Invitations ───────────────────────────────────────────────────────────────
  const renderInvitations = () => (
    <>
      <div className="view-header">
        <h2>Invitations reçues</h2>
        <span>
          {invitations.length} invitation{invitations.length !== 1 ? "s" : ""}{" "}
          en attente
        </span>
      </div>
      {invitations.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-envelope-open"></i>
          <p>Aucune invitation en attente pour le moment.</p>
        </div>
      ) : (
        <div className="inv-grid">
          {invitations.map((inv) => {
            const busy = !!invLoading[inv.id_activity];
            return (
              <div className="inv-card" key={inv.id_activity}>
                <div className="inv-card-header">
                  <div className="inv-avatar">
                    <i className="fas fa-flask"></i>
                  </div>
                  <div className="inv-info">
                    <h4>{inv.name_activity}</h4>
                    <p>
                      ID : {inv.id_activity}{" "}
                      {inv.class_activity && `· ${inv.class_activity}`}
                    </p>
                  </div>
                  <span className="inv-badge">En attente</span>
                </div>
                {inv.description && (
                  <div className="inv-desc">{inv.description}</div>
                )}
                {inv.period && (
                  <p
                    style={{
                      fontSize: ".75rem",
                      color: "var(--muted)",
                      marginBottom: ".8rem",
                    }}
                  >
                    <i
                      className="fas fa-calendar-alt"
                      style={{ marginRight: ".35rem", color: "var(--gold)" }}
                    ></i>
                    Période : {inv.period}
                  </p>
                )}
                <div className="inv-actions">
                  <button
                    className="btn-accept"
                    disabled={busy}
                    onClick={() => handleInvitation(inv.id_activity, "accept")}
                  >
                    <i
                      className={`fas ${busy ? "fa-spinner fa-spin" : "fa-check"}`}
                    ></i>
                    Accepter
                  </button>
                  <button
                    className="btn-refuse"
                    disabled={busy}
                    onClick={() => handleInvitation(inv.id_activity, "refuse")}
                  >
                    <i
                      className={`fas ${busy ? "fa-spinner fa-spin" : "fa-times"}`}
                    ></i>
                    Refuser
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );

  // ── Contributions ─────────────────────────────────────────────────────────────
  const renderContributions = () => (
    <>
      <div className="view-header">
        <h2>Mes contributions</h2>
        <span>
          {contributions.length} activité{contributions.length !== 1 ? "s" : ""}
        </span>
      </div>
      {contributions.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-layer-group"></i>
          <p>Vous ne participez à aucune activité pour l'instant.</p>
        </div>
      ) : (
        <div className="contrib-list">
          {contributions.map((c) => (
            <div className="contrib-item" key={c.id_activity}>
              <div className="contrib-left">
                <div className="contrib-dot"></div>
                <div>
                  <div className="contrib-name">{c.name_activity}</div>
                  {c.description && (
                    <div className="contrib-desc">{c.description}</div>
                  )}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                {c.class_activity && (
                  <span className="contrib-badge">{c.class_activity}</span>
                )}
                {c.period && <div className="contrib-date">{c.period}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );

  // ── Questions ─────────────────────────────────────────────────────────────────
  const renderQuestions = () => (
    <>
      {/* Formulaire nouvelle question */}
      <div className="new-item-card">
        <button
          className="new-item-trigger"
          onClick={() => setQOpen((o) => !o)}
        >
          <i className="fas fa-plus trigger-icon"></i>
          Poser une nouvelle question
          <i
            className={`fas fa-chevron-down chevron${qOpen ? " open" : ""}`}
          ></i>
        </button>
        {qOpen && (
          <div className="new-item-form">
            <div className="form-group">
              <label>Intitulé de la question *</label>
              <input
                type="text"
                placeholder="Ex : Comment rejoindre un projet de recherche ?"
                value={qForm.libele_question}
                onChange={(e) =>
                  setQForm((f) => ({ ...f, libele_question: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Description (contexte, détails)</label>
              <textarea
                placeholder="Donnez plus de contexte à votre question..."
                value={qForm.description_question}
                onChange={(e) =>
                  setQForm((f) => ({
                    ...f,
                    description_question: e.target.value,
                  }))
                }
              />
            </div>
            <button
              className="btn-submit"
              onClick={handleQuestionSubmit}
              disabled={qSending || !qForm.libele_question.trim()}
            >
              <i
                className={`fas ${qSending ? "fa-spinner fa-spin" : "fa-paper-plane"}`}
              ></i>
              {qSending ? "Envoi..." : "Envoyer la question"}
            </button>
          </div>
        )}
      </div>

      {/* Liste des questions */}
      <div className="view-header">
        <h2>Mes questions</h2>
        <span>
          {questions.length} question{questions.length !== 1 ? "s" : ""}
        </span>
      </div>
      {questions.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-circle-question"></i>
          <p>Vous n'avez posé aucune question pour l'instant.</p>
        </div>
      ) : (
        <div className="question-list">
          {questions.map((q) => (
            <div className="question-card" key={q.id_question}>
              <div className="question-card-header">
                <div className="q-icon">
                  <i className="fas fa-question"></i>
                </div>
                <div>
                  <div className="q-title">{q.libele_question}</div>
                  {q.description_question && (
                    <div className="q-desc">{q.description_question}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );

  // ── Suggestions ───────────────────────────────────────────────────────────────
  const renderSuggestions = () => (
    <>
      {/* Formulaire nouvelle suggestion */}
      <div className="new-item-card">
        <button
          className="new-item-trigger"
          onClick={() => setSOpen((o) => !o)}
        >
          <i className="fas fa-plus trigger-icon"></i>
          Apporter une suggestion
          <i
            className={`fas fa-chevron-down chevron${sOpen ? " open" : ""}`}
          ></i>
        </button>
        {sOpen && (
          <div className="new-item-form">
            <div className="form-group">
              <label>Titre de la suggestion *</label>
              <input
                type="text"
                placeholder="Ex : Ajouter un espace de travail collaboratif"
                value={sForm.libele}
                onChange={(e) =>
                  setSForm((f) => ({ ...f, libele: e.target.value }))
                }
              />
            </div>
            <div className="form-group">
              <label>Description détaillée</label>
              <textarea
                placeholder="Expliquez votre suggestion en détail..."
                value={sForm.description_suggest}
                onChange={(e) =>
                  setSForm((f) => ({
                    ...f,
                    description_suggest: e.target.value,
                  }))
                }
              />
            </div>
            <div className="form-group">
              <label>Note d'importance (optionnel)</label>
              <StarRating
                value={sForm.note}
                onChange={(n) => setSForm((f) => ({ ...f, note: n }))}
              />
            </div>
            <button
              className="btn-submit"
              onClick={handleSuggestionSubmit}
              disabled={sSending || !sForm.libele.trim()}
            >
              <i
                className={`fas ${sSending ? "fa-spinner fa-spin" : "fa-paper-plane"}`}
              ></i>
              {sSending ? "Envoi..." : "Envoyer la suggestion"}
            </button>
          </div>
        )}
      </div>

      {/* Liste des suggestions */}
      <div className="view-header">
        <h2>Mes suggestions</h2>
        <span>
          {suggestions.length} suggestion{suggestions.length !== 1 ? "s" : ""}
        </span>
      </div>
      {suggestions.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-lightbulb"></i>
          <p>Vous n'avez encore apporté aucune suggestion.</p>
        </div>
      ) : (
        <div className="suggestion-list">
          {suggestions.map((s) => (
            <div className="suggestion-card" key={s.id_suggest}>
              <div className="suggestion-card-header">
                <div
                  style={{
                    display: "flex",
                    gap: ".75rem",
                    alignItems: "flex-start",
                  }}
                >
                  <div className="s-icon">
                    <i className="fas fa-lightbulb"></i>
                  </div>
                  <div>
                    <div className="s-title">{s.libele}</div>
                    {s.description_suggest && (
                      <div className="s-desc">{s.description_suggest}</div>
                    )}
                  </div>
                </div>
                {s.note > 0 && (
                  <div style={{ flexShrink: 0 }}>
                    <StarRating value={s.note} readOnly />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );

  // ── En Attente ───────────────────────────────────────────────────────────────
  const renderPending = () => {
    // Filtrer les questions et suggestions en attente
    const pendingQuestions = questions.filter(
      (q) => q.visibility === "pending",
    );
    const pendingSuggestions = suggestions.filter(
      (s) => s.visibility === "pending",
    );

    const totalPending =
      pendingQuestions.length + pendingSuggestions.length + pendingMods.length;

    return (
      <>
        <div className="view-header">
          <h2>Mes demandes en attente</h2>
          <span>
            {totalPending} demande{totalPending !== 1 ? "s" : ""} en attente
            d'approbation
          </span>
        </div>

        {totalPending === 0 ? (
          <div className="empty-state">
            <i className="fas fa-clock"></i>
            <p>Aucune demande en attente d'approbation.</p>
          </div>
        ) : (
          <div className="pending-grid">
            {/* Modifications de profil en attente */}
            {pendingMods.length > 0 && (
              <div className="pending-section">
                <h3>
                  <i className="fas fa-user-edit"></i> Modifications de profil
                </h3>
                {pendingMods.map((mod) => (
                  <div className="pending-card" key={mod.id}>
                    <div className="pending-card-header">
                      <div className="pending-icon">
                        <i className="fas fa-user-edit"></i>
                      </div>
                      <div className="pending-info">
                        <h4>Modification : {mod.field_name}</h4>
                        <p>
                          Demandée le{" "}
                          {new Date(mod.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <span className="pending-badge">En attente</span>
                    </div>
                    <div className="pending-details">
                      <div className="pending-change">
                        <span className="old-value">
                          Ancien : {mod.old_value || "—"}
                        </span>
                        <i className="fas fa-arrow-right"></i>
                        <span className="new-value">
                          Nouveau : {mod.new_value}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Questions en attente */}
            {pendingQuestions.length > 0 && (
              <div className="pending-section">
                <h3>
                  <i className="fas fa-circle-question"></i> Questions
                </h3>
                {pendingQuestions.map((q) => (
                  <div className="pending-card" key={q.id_question}>
                    <div className="pending-card-header">
                      <div className="pending-icon">
                        <i className="fas fa-circle-question"></i>
                      </div>
                      <div className="pending-info">
                        <h4>{q.libele_question}</h4>
                        <p>
                          Posée le{" "}
                          {new Date(q.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <span className="pending-badge">En attente</span>
                    </div>
                    {q.description_question && (
                      <div className="pending-desc">
                        {q.description_question}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Suggestions en attente */}
            {pendingSuggestions.length > 0 && (
              <div className="pending-section">
                <h3>
                  <i className="fas fa-lightbulb"></i> Suggestions
                </h3>
                {pendingSuggestions.map((s) => (
                  <div className="pending-card" key={s.id_suggest}>
                    <div className="pending-card-header">
                      <div className="pending-icon">
                        <i className="fas fa-lightbulb"></i>
                      </div>
                      <div className="pending-info">
                        <h4>{s.libele}</h4>
                        <p>
                          Proposée le{" "}
                          {new Date(s.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <span className="pending-badge">En attente</span>
                    </div>
                    {s.description_suggest && (
                      <div className="pending-desc">
                        {s.description_suggest}
                      </div>
                    )}
                    {s.note > 0 && (
                      <div className="pending-rating">
                        <span className="rating-label">Importance :</span>
                        <div className="star-display">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <i
                              key={star}
                              className={`fas fa-star${star <= s.note ? " filled" : ""}`}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </>
    );
  };

  // ── Dispatch view ────────────────────────────────────────────────────────────
  const renderView = () => {
    switch (view) {
      case "home":
        return renderHome();
      case "profile":
        return renderProfile();
      case "pending":
        return renderPending();
      case "invitations":
        return renderInvitations();
      case "contributions":
        return renderContributions();
      case "questions":
        return renderQuestions();
      case "suggestions":
        return renderSuggestions();
      default:
        return renderHome();
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // LAYOUT
  // ════════════════════════════════════════════════════════════════════════════
  return (
    <div className="dash-layout">
      {/* ── SIDEBAR ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <img
            src="/betalabs.png"
            alt="BetaLab"
            className="sidebar-logo-img"
          />
          <span className="logo-text">BetaLab</span>
        </div>

        <div className="nav-section">Menu</div>
        {NAV.map((n) => (
          <button
            key={n.id}
            className={`nav-item${view === n.id ? " active" : ""}`}
            onClick={() => setView(n.id)}
          >
            <i className={`fas ${n.icon}`}></i>
            {n.label}
            {n.id === "invitations" && pendingCount > 0 && (
              <span className="nav-badge">{pendingCount}</span>
            )}
          </button>
        ))}

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">{initial}</div>
            <div className="user-details">
              <div className="name">{user?.name || "Chargement…"}</div>
              <div className="role-label">{occLabel}</div>
            </div>
            <button
              className="logout-btn"
              title="Se déconnecter"
              onClick={handleLogout}
            >
              <i className="fas fa-sign-out-alt"></i>
            </button>
          </div>
        </div>
      </aside>

      {/* ── MAIN ── */}
      <div className="main">
        <div className="topbar">
          <div className="page-title">
            <h1>{PAGE_TITLES[view]?.title}</h1>
            <p>{PAGE_TITLES[view]?.sub}</p>
          </div>
          <div className="topbar-right">
            <span className="topbar-greeting">
              Connecté : <strong>{user?.name || "—"}</strong>
            </span>
            <div className="topbar-avatar">{initial}</div>
          </div>
        </div>

        <div className="content">
          {actionMsg && (
            <div className="alert alert-success">
              <i className="fas fa-check-circle"></i> {actionMsg}
            </div>
          )}
          {error && (
            <div className="alert alert-error">
              <i className="fas fa-exclamation-circle"></i> {error}
            </div>
          )}

          {loading ? (
            <div className="loading-state">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Chargement de votre espace…</p>
            </div>
          ) : (
            renderView()
          )}
        </div>
      </div>
    </div>
  );
}
