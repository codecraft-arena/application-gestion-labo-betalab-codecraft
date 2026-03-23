/**
 * Tableau de bord administrateur BetaLab — refonte complète.
 * Vues : Dashboard · Utilisateurs · Validation · Activités · Événements ·
 *        Questions · Contributions · Statistiques · Paramètres
 */
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import "./DashAdmin.css";

// ══════════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ══════════════════════════════════════════════════════════════════════════════
const VIEWS = [
  {
    id: "dashboard",
    icon: "fa-gauge-high",
    label: "Dashboard",
    section: "principal",
  },
  {
    id: "users",
    icon: "fa-users",
    label: "Utilisateurs",
    section: "principal",
  },
  {
    id: "validation",
    icon: "fa-user-check",
    label: "Validation",
    section: "principal",
  },
  {
    id: "approvals",
    icon: "fa-clipboard-check",
    label: "Approbations",
    section: "principal",
  },
  {
    id: "contacts",
    icon: "fa-envelope",
    label: "Messages",
    section: "principal",
  },
  {
    id: "activities",
    icon: "fa-flask",
    label: "Activités",
    section: "contenu",
  },
  {
    id: "events",
    icon: "fa-calendar-days",
    label: "Événements",
    section: "contenu",
  },
  {
    id: "questions",
    icon: "fa-circle-question",
    label: "Questions",
    section: "contenu",
  },
  {
    id: "contributions",
    icon: "fa-layer-group",
    label: "Contributions",
    section: "contenu",
  },
  {
    id: "stats",
    icon: "fa-chart-bar",
    label: "Statistiques",
    section: "analyse",
  },
  { id: "settings", icon: "fa-gear", label: "Paramètres", section: "analyse" },
];

const ROLES = ["membre", "chercheur", "responsable", "admin"];
const ROLE_BADGE = {
  membre: "blue",
  chercheur: "purple",
  responsable: "gold",
  admin: "red",
};

const PAGE_META = {
  dashboard: { title: "Dashboard", sub: "Vue d'ensemble du laboratoire" },
  users: { title: "Utilisateurs", sub: "Gestion de tous les comptes" },
  validation: { title: "Validation", sub: "Demandes en attente d'approbation" },
  approvals: {
    title: "Approbations",
    sub: "Approuver ou rejeter les demandes utilisateur",
  },
  contacts: {
    title: "Messages de Contact",
    sub: "Demandes de contact et adhésion reçues",
  },
  activities: {
    title: "Activités & Projets",
    sub: "Créer, gérer et suivre les projets",
  },
  events: { title: "Événements", sub: "Conférences, ateliers, hackathons" },
  questions: { title: "Questions", sub: "Répondre aux questions des membres" },
  contributions: {
    title: "Contributions",
    sub: "Toutes les participations aux activités",
  },
  stats: { title: "Statistiques", sub: "Analyse et répartition des données" },
  settings: { title: "Paramètres", sub: "Informations système" },
};

// ══════════════════════════════════════════════════════════════════════════════
// MODAL COMPONENT
// ══════════════════════════════════════════════════════════════════════════════
function Modal({ title, onClose, children }) {
  return (
    <div
      className="modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal">
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════════════════════════════════════

// Helper function to safely convert any error to string
const toErrorString = (err) => {
  if (typeof err === "string") return err;
  if (err === null || err === undefined) return "Une erreur est survenue";
  if (err instanceof Error) return err.message || String(err);
  if (typeof err === "object" && err.message) return String(err.message);
  if (typeof err === "object" && err.detail) return String(err.detail);
  return "Une erreur est survenue";
};

export default function DashAdmin() {
  const navigate = useNavigate();
  const [view, setView] = useState("dashboard");

  // ── Data ──────────────────────────────────────────────────────────────────
  const [users, setUsers] = useState([]);
  const [pending, setPending] = useState([]);
  const [activities, setActivities] = useState([]);
  const [events, setEvents] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [contributions, setContributions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  // ── UI state ──────────────────────────────────────────────────────────────
  const [search, setSearch] = useState("");
  const [valTab, setValTab] = useState("pending");

  // ── Modal state ───────────────────────────────────────────────────────────
  const [modal, setModal] = useState(null);
  // modal: null | { type: 'createActivity'|'createEvent'|'createUser'|'editUser'|'roleUser'|'inviteUser'|'answerQuestion'|'editActivity', data? }

  // ── Form state (modals) ───────────────────────────────────────────────────
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);

  // ── Load all ──────────────────────────────────────────────────────────────
  const loadAll = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [allU, pend, acts, evts, qs, contribs, suggs, conts, pendingAppr] =
        await Promise.all([
          apiFetch("/api/users"),
          apiFetch("/api/users/pending"),
          apiFetch("/api/activities"),
          apiFetch("/api/admin/events"),
          apiFetch("/api/admin/questions"),
          apiFetch("/api/admin/contributions"),
          apiFetch("/api/admin/suggestions"),
          apiFetch("/api/contact"),
          apiFetch("/api/admin/pending-approvals"),
        ]);
      setUsers(allU);
      setPending(pend);
      setActivities(acts);
      setEvents(evts);
      setQuestions(qs);
      setContributions(contribs);
      setSuggestions(suggs);
      setContacts(conts);
      setPendingApprovals(pendingAppr);
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // ── Auto-clear message ────────────────────────────────────────────────────
  useEffect(() => {
    if (!actionMsg) return;
    const t = setTimeout(() => setActionMsg(""), 3500);
    return () => clearTimeout(t);
  }, [actionMsg]);

  // ── Generic action ────────────────────────────────────────────────────────
  const doAction = async (fn, msg) => {
    setError("");
    try {
      await fn();
      // Assurez-vous que msg est une string
      const msgStr = typeof msg === "string" ? msg : "✓ Action effectuée";
      setActionMsg(msgStr);
      await loadAll();
    } catch (e) {
      console.error("Action error:", e);
      setError(toErrorString(e));
    }
  };

  const handleLogout = async () => {
    try {
      await apiFetch("/logout");
    } catch {}
    navigate("/");
  };

  // ── Open modals ───────────────────────────────────────────────────────────
  const openModal = (type, data = {}) => {
    setModal({ type, data });
    setForm(data.initial || {});
    setSaving(false);
  };
  const closeModal = () => {
    setModal(null);
    setForm({});
  };

  // ── Modal submit ──────────────────────────────────────────────────────────
  const handleModalSubmit = async () => {
    setSaving(true);
    setError("");
    try {
      const { type, data } = modal;

      if (type === "createActivity") {
        await apiFetch("/api/activities", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        setActionMsg("✓ Activité créée");
      } else if (type === "createEvent") {
        await apiFetch("/api/admin/events", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        });
        setActionMsg("✓ Événement créé");
      } else if (type === "editUser") {
        await apiFetch(
          `/api/admin/users/${encodeURIComponent(data.email)}/update`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(form),
          },
        );
        setActionMsg(`✓ Utilisateur ${data.email} mis à jour`);
      } else if (type === "createUser") {
        const result = await apiFetch("/api/admin/users/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: form.name }),
        });
        setActionMsg(
          `✓ Utilisateur ${form.name} créé\n📧 Email : ${result.email}\n🔑 Mot de passe : ${result.password}`
        );
      } else if (type === "roleUser") {
        await apiFetch(
          `/api/admin/users/${encodeURIComponent(data.email)}/role`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: form.role }),
          },
        );
        setActionMsg(`✓ Rôle « ${form.role} » attribué à ${data.email}`);
      } else if (type === "inviteUser") {
        await apiFetch(
          `/api/activities/${encodeURIComponent(form.activity_id)}/invite/${encodeURIComponent(data.email)}`,
          { method: "POST" },
        );
        setActionMsg(`✓ Invitation envoyée à ${data.email}`);
      } else if (type === "answerQuestion") {
        await apiFetch(`/api/admin/questions/${data.q_id}/answer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            libelle_response: form.libelle_response,
            description_response: form.description_response,
          }),
        });
        setActionMsg("✓ Réponse publiée");
      }

      await loadAll();
      closeModal();
    } catch (e) {
      setError(toErrorString(e));
    } finally {
      setSaving(false);
    }
  };

  // ── Helpers ───────────────────────────────────────────────────────────────
  const fc = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  const validated = users.filter((u) => u.validated);
  const suspended = users.filter((u) => u.suspended);
  const unreadContacts = contacts.filter((c) => c.status === "nouveau");
  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()),
  );
  const pendingQ = questions.filter((q) => q.responses?.length === 0);

  // ══════════════════════════════════════════════════════════════════════════
  // VIEWS
  // ══════════════════════════════════════════════════════════════════════════

  // ── Dashboard ─────────────────────────────────────────────────────────────
  const renderDashboard = () => (
    <>
      <div className="stats-grid">
        {[
          {
            icon: "fa-users",
            cls: "gold",
            val: users.length,
            label: "Utilisateurs",
            view: "users",
          },
          {
            icon: "fa-user-check",
            cls: "green",
            val: validated.length,
            label: "Membres validés",
            view: "validation",
          },
          {
            icon: "fa-user-clock",
            cls: "orange",
            val: pending.length,
            label: "En attente",
            view: "validation",
          },
          {
            icon: "fa-user-slash",
            cls: "red",
            val: suspended.length,
            label: "Suspendus",
            view: "users",
          },
          {
            icon: "fa-flask",
            cls: "blue",
            val: activities.length,
            label: "Activités",
            view: "activities",
          },
          {
            icon: "fa-calendar",
            cls: "purple",
            val: events.length,
            label: "Événements",
            view: "events",
          },
          {
            icon: "fa-question",
            cls: "gold",
            val: pendingQ.length,
            label: "Questions sans réponse",
            view: "questions",
          },
          {
            icon: "fa-layer-group",
            cls: "green",
            val: contributions.length,
            label: "Contributions",
            view: "contributions",
          },
        ].map((s) => (
          <div
            className="stat-card"
            key={s.label}
            onClick={() => setView(s.view)}
          >
            <div className={`stat-icon ${s.cls}`}>
              <i className={`fas ${s.icon}`}></i>
            </div>
            <div className="stat-value">{s.val}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>
    </>
  );

  // ── Users ─────────────────────────────────────────────────────────────────
  const renderUsers = () => (
    <>
      <div className="table-container">
        <div className="table-header">
          <span className="table-title">
            Tous les utilisateurs ({filtered.length})
          </span>
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            <button
              className="btn-primary"
              title="Créer nouvel utilisateur"
              onClick={() =>
                openModal("createUser", { initial: { name: "" } })
              }
            >
              <i className="fas fa-plus"></i> Nouvel utilisateur
            </button>
            <div className="search-box">
              <i className="fas fa-search"></i>
              <input
                placeholder="Rechercher…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>
        </div>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Nom</th>
              <th>Email</th>
              <th>Occupation</th>
              <th>Institution</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((u) => (
              <tr key={u.email}>
                <td>
                  <strong>{u.name}</strong>
                </td>
                <td style={{ color: "var(--muted)", fontSize: ".82rem" }}>
                  {u.email}
                </td>
                <td>
                  <span className="badge blue">{u.occupation}</span>
                </td>
                <td>{u.institution || "—"}</td>
                <td>
                  <span className={`badge ${ROLE_BADGE[u.role] || "gray"}`}>
                    {u.role || "membre"}
                  </span>
                </td>
                <td>
                  <span
                    className={`badge ${u.suspended ? "red" : u.validated ? "green" : "orange"}`}
                  >
                    {u.suspended
                      ? "Suspendu"
                      : u.validated
                        ? "Validé"
                        : "En attente"}
                  </span>
                </td>
                <td>
                  <div className="actions">
                    {/* Modifier */}
                    <button
                      className="btn-icon edit"
                      title="Modifier"
                      onClick={() =>
                        openModal("editUser", {
                          email: u.email,
                          initial: {
                            name: u.name,
                            occupation: u.occupation,
                            institution: u.institution,
                            level: u.level,
                            domain: u.domain,
                            motivation: u.motivation,
                          },
                        })
                      }
                    >
                      <i className="fas fa-pen"></i>
                    </button>
                    {/* Rôle */}
                    <button
                      className="btn-icon invite"
                      title="Attribuer un rôle"
                      onClick={() =>
                        openModal("roleUser", {
                          email: u.email,
                          initial: { role: u.role || "membre" },
                        })
                      }
                    >
                      <i className="fas fa-user-tag"></i>
                    </button>
                    {/* Inviter */}
                    <button
                      className="btn-icon answer"
                      title="Inviter à une activité"
                      onClick={() =>
                        openModal("inviteUser", {
                          email: u.email,
                          initial: { activity_id: "" },
                        })
                      }
                    >
                      <i className="fas fa-paper-plane"></i>
                    </button>
                    {/* Valider */}
                    {!u.validated && (
                      <button
                        className="btn-icon validate"
                        title="Valider"
                        onClick={() =>
                          doAction(
                            () =>
                              apiFetch(
                                `/api/users/${encodeURIComponent(u.email)}/validate`,
                                { method: "PUT" },
                              ),
                            `✓ ${u.name} validé`,
                          )
                        }
                      >
                        <i className="fas fa-check"></i>
                      </button>
                    )}
                    {/* Suspendre / Réactiver */}
                    {u.suspended ? (
                      <button
                        className="btn-icon unsuspend"
                        title="Réactiver"
                        onClick={() =>
                          doAction(
                            () =>
                              apiFetch(
                                `/api/users/${encodeURIComponent(u.email)}/unsuspend`,
                                { method: "PUT" },
                              ),
                            `✓ ${u.name} réactivé`,
                          )
                        }
                      >
                        <i className="fas fa-rotate-left"></i>
                      </button>
                    ) : (
                      <button
                        className="btn-icon suspend"
                        title="Suspendre"
                        onClick={() =>
                          doAction(
                            () =>
                              apiFetch(
                                `/api/users/${encodeURIComponent(u.email)}/suspend`,
                                { method: "PUT" },
                              ),
                            `✓ ${u.name} suspendu`,
                          )
                        }
                      >
                        <i className="fas fa-ban"></i>
                      </button>
                    )}
                    {/* Supprimer */}
                    <button
                      className="btn-icon delete"
                      title="Supprimer"
                      onClick={() => {
                        if (
                          !confirm(
                            `Supprimer définitivement ${u.email} et toutes ses données ?`,
                          )
                        )
                          return;
                        doAction(
                          () =>
                            apiFetch(
                              `/api/users/${encodeURIComponent(u.email)}`,
                              { method: "DELETE" },
                            ),
                          `✓ ${u.email} supprimé`,
                        );
                      }}
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  style={{
                    textAlign: "center",
                    color: "var(--muted)",
                    padding: "2rem",
                  }}
                >
                  Aucun résultat
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );

  // ── Validation ────────────────────────────────────────────────────────────
  const renderValidation = () => (
    <>
      <div className="validation-tabs">
        {[
          {
            id: "pending",
            label: `En attente (${pending.length})`,
            icon: "fa-user-clock",
          },
          {
            id: "validated",
            label: `Validés (${validated.length})`,
            icon: "fa-user-check",
          },
          {
            id: "suspended",
            label: `Suspendus (${suspended.length})`,
            icon: "fa-user-slash",
          },
        ].map((t) => (
          <button
            key={t.id}
            className={`vtab${valTab === t.id ? " active" : ""}`}
            onClick={() => setValTab(t.id)}
          >
            <i className={`fas ${t.icon}`}></i> {t.label}
          </button>
        ))}
      </div>

      {valTab === "pending" &&
        (pending.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-check-circle"></i>
            <p>Aucune demande en attente</p>
          </div>
        ) : (
          <div className="val-cards">
            {pending.map((u) => (
              <div className="val-card" key={u.email}>
                <div className="vc-header">
                  <div className="vc-avatar">
                    {u.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="vc-info">
                    <h4>{u.name}</h4>
                    <p>{u.email}</p>
                  </div>
                </div>
                <div className="vc-details">
                  {[
                    ["Occupation", u.occupation],
                    ["Institution", u.institution],
                    ["Niveau", u.level],
                    ["Domaine", u.domain],
                  ].map(([l, v]) => (
                    <div className="vc-detail" key={l}>
                      <span className="vc-label">{l}</span>
                      <span className="vc-value">{v || "—"}</span>
                    </div>
                  ))}
                  {u.motivation && (
                    <div className="vc-detail full">
                      <span className="vc-label">Motivation</span>
                      <span className="vc-value">{u.motivation}</span>
                    </div>
                  )}
                </div>
                <div className="vc-actions">
                  <button
                    className="btn-validate"
                    onClick={() =>
                      doAction(
                        () =>
                          apiFetch(
                            `/api/users/${encodeURIComponent(u.email)}/validate`,
                            { method: "PUT" },
                          ),
                        `✓ ${u.name} validé`,
                      )
                    }
                  >
                    <i className="fas fa-check"></i> Valider
                  </button>
                  <button
                    className="btn-reject-card"
                    onClick={() =>
                      doAction(
                        () =>
                          apiFetch(
                            `/api/users/${encodeURIComponent(u.email)}/reject`,
                            { method: "PUT" },
                          ),
                        `✓ ${u.email} rejeté`,
                      )
                    }
                  >
                    <i className="fas fa-times"></i> Rejeter
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}

      {valTab === "validated" && (
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Occupation</th>
                <th>Institution</th>
                <th>Rôle</th>
              </tr>
            </thead>
            <tbody>
              {validated.map((u) => (
                <tr key={u.email}>
                  <td>{u.name}</td>
                  <td style={{ color: "var(--muted)" }}>{u.email}</td>
                  <td>
                    <span className="badge blue">{u.occupation}</span>
                  </td>
                  <td>{u.institution || "—"}</td>
                  <td>
                    <span className={`badge ${ROLE_BADGE[u.role] || "gray"}`}>
                      {u.role || "membre"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {valTab === "suspended" &&
        (suspended.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-user-slash"></i>
            <p>Aucun utilisateur suspendu</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Email</th>
                  <th>Occupation</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {suspended.map((u) => (
                  <tr key={u.email}>
                    <td>{u.name}</td>
                    <td style={{ color: "var(--muted)" }}>{u.email}</td>
                    <td>
                      <span className="badge blue">{u.occupation}</span>
                    </td>
                    <td>
                      <div className="actions">
                        <button
                          className="btn-icon unsuspend"
                          title="Réactiver"
                          onClick={() =>
                            doAction(
                              () =>
                                apiFetch(
                                  `/api/users/${encodeURIComponent(u.email)}/unsuspend`,
                                  { method: "PUT" },
                                ),
                              `✓ ${u.name} réactivé`,
                            )
                          }
                        >
                          <i className="fas fa-rotate-left"></i>
                        </button>
                        <button
                          className="btn-icon delete"
                          title="Supprimer"
                          onClick={() => {
                            if (!confirm(`Supprimer ${u.email} ?`)) return;
                            doAction(
                              () =>
                                apiFetch(
                                  `/api/users/${encodeURIComponent(u.email)}`,
                                  { method: "DELETE" },
                                ),
                              `✓ Supprimé`,
                            );
                          }}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
    </>
  );

  // ── Activities ────────────────────────────────────────────────────────────
  const renderActivities = () => (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: "1.2rem",
        }}
      >
        <button
          className="btn-primary"
          onClick={() =>
            openModal("createActivity", { initial: { status: "en attente" } })
          }
        >
          <i className="fas fa-plus"></i> Nouvelle activité
        </button>
      </div>
      <div className="table-container">
        <span
          className="table-title"
          style={{ display: "block", marginBottom: "1rem" }}
        >
          Toutes les activités ({activities.length})
        </span>
        <table className="custom-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nom</th>
              <th>Description</th>
              <th>Classe</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {activities.map((a) => (
              <tr key={a.id_activity}>
                <td>
                  <code style={{ fontSize: ".78rem", color: "var(--muted)" }}>
                    {a.id_activity}
                  </code>
                </td>
                <td>
                  <strong>{a.name_activity}</strong>
                </td>
                <td
                  style={{
                    fontSize: ".82rem",
                    color: "var(--muted)",
                    maxWidth: "200px",
                  }}
                >
                  {a.description || "—"}
                </td>
                <td>{a.class_activity || "—"}</td>
                <td>
                  <span
                    className={`badge ${a.status === "approuvé" ? "green" : a.status === "rejeté" ? "red" : "orange"}`}
                  >
                    {a.status || "en attente"}
                  </span>
                </td>
                <td>
                  <div className="actions">
                    {a.status !== "approuvé" && (
                      <button
                        className="btn-icon validate"
                        title="Approuver"
                        onClick={() =>
                          doAction(
                            () =>
                              apiFetch(
                                `/api/activities/${encodeURIComponent(a.id_activity)}/validate`,
                                { method: "PUT" },
                              ),
                            `✓ Activité approuvée`,
                          )
                        }
                      >
                        <i className="fas fa-check"></i>
                      </button>
                    )}
                    {a.status !== "rejeté" && (
                      <button
                        className="btn-icon reject"
                        title="Rejeter"
                        onClick={() =>
                          doAction(
                            () =>
                              apiFetch(
                                `/api/activities/${encodeURIComponent(a.id_activity)}/reject`,
                                { method: "PUT" },
                              ),
                            `✓ Activité rejetée`,
                          )
                        }
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    )}
                    <button
                      className="btn-icon invite"
                      title="Inviter un utilisateur"
                      onClick={() =>
                        openModal("inviteUser", {
                          email: "",
                          initial: { activity_id: a.id_activity },
                          forActivity: true,
                        })
                      }
                    >
                      <i className="fas fa-user-plus"></i>
                    </button>
                    <button
                      className="btn-icon delete"
                      title="Supprimer"
                      onClick={() => {
                        if (!confirm(`Supprimer l'activité ${a.id_activity} ?`))
                          return;
                        doAction(
                          () =>
                            apiFetch(
                              `/api/activities/${encodeURIComponent(a.id_activity)}`,
                              { method: "DELETE" },
                            ),
                          "✓ Activité supprimée",
                        );
                      }}
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {activities.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  style={{
                    textAlign: "center",
                    color: "var(--muted)",
                    padding: "2rem",
                  }}
                >
                  Aucune activité
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );

  // ── Events ────────────────────────────────────────────────────────────────
  const renderEvents = () => (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          marginBottom: "1.2rem",
        }}
      >
        <button
          className="btn-primary"
          onClick={() => openModal("createEvent")}
        >
          <i className="fas fa-plus"></i> Nouvel événement
        </button>
      </div>
      {events.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-calendar-days"></i>
          <p>Aucun événement planifié</p>
        </div>
      ) : (
        <div className="events-grid">
          {events.map((ev) => (
            <div className="event-card" key={ev.id}>
              <div className="event-card-header">
                <span className="event-type-badge">{ev.event_type}</span>
                <button
                  className="btn-icon delete"
                  title="Supprimer"
                  onClick={() =>
                    doAction(
                      () =>
                        apiFetch(`/api/admin/events/${ev.id}`, {
                          method: "DELETE",
                        }),
                      `✓ Événement supprimé`,
                    )
                  }
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
              <div className="event-title">{ev.title}</div>
              {ev.description && (
                <div className="event-desc">{ev.description}</div>
              )}
              <div className="event-meta">
                {ev.event_date && (
                  <span>
                    <i className="fas fa-calendar"></i>
                    {ev.event_date}
                  </span>
                )}
                {ev.location && (
                  <span>
                    <i className="fas fa-map-marker-alt"></i>
                    {ev.location}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );

  // ── Questions ─────────────────────────────────────────────────────────────
  const renderQuestions = () => (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.2rem",
        }}
      >
        <span style={{ fontSize: ".9rem", color: "var(--muted)" }}>
          {pendingQ.length} question{pendingQ.length !== 1 ? "s" : ""} sans
          réponse
        </span>
      </div>
      {questions.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-circle-question"></i>
          <p>Aucune question posée</p>
        </div>
      ) : (
        questions.map((q) => (
          <div className="question-card" key={q.id_question}>
            <div className="question-header">
              <div className="question-meta">
                <div className="q-icon">
                  <i className="fas fa-question"></i>
                </div>
                <div>
                  <div className="q-title">{q.libele_question}</div>
                  {q.id_user && <div className="q-user">Par : {q.id_user}</div>}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  className="btn-icon answer"
                  title="Répondre"
                  onClick={() =>
                    openModal("answerQuestion", {
                      q_id: q.id_question,
                      q_title: q.libele_question,
                      initial: { libelle_response: "", description_response: "" },
                    })
                  }
                >
                  <i className="fas fa-reply"></i>
                </button>
                <button
                  className="btn-icon delete"
                  title="Supprimer la question"
                  onClick={() => {
                    if (confirm(`Supprimer la question « ${q.libele_question} » ?`)) {
                      doAction(
                        () =>
                          apiFetch(`/api/admin/questions/${q.id_question}`, {
                            method: "DELETE",
                          }),
                        "✓ Question supprimée",
                      );
                    }
                  }}
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
            {q.description_question && (
              <div className="q-desc">{q.description_question}</div>
            )}
            {q.responses?.length > 0 && (
              <div className="q-answers">
                <div className="q-answers-title">
                  <i
                    className="fas fa-comments"
                    style={{ marginRight: ".35rem", color: "var(--gold)" }}
                  ></i>
                  {q.responses.length} réponse
                  {q.responses.length !== 1 ? "s" : ""}
                </div>
                {q.responses.map((r) => (
                  <div className="answer-item" key={r.id_response}>
                    <div className="a-title">{r.libelle_response}</div>
                    {r.description_response && (
                      <div className="a-desc">{r.description_response}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))
      )}
    </>
  );

  // ── Contributions ─────────────────────────────────────────────────────────
  const renderContributions = () => (
    <div className="table-container">
      <span
        className="table-title"
        style={{ display: "block", marginBottom: "1rem" }}
      >
        Toutes les participations ({contributions.length})
      </span>
      <table className="custom-table">
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Email</th>
            <th>Activité</th>
            <th>Classe</th>
            <th>Statut participation</th>
            <th>Période</th>
          </tr>
        </thead>
        <tbody>
          {contributions.map((c, i) => (
            <tr key={i}>
              <td>
                <strong>{c.user_name}</strong>
              </td>
              <td style={{ fontSize: ".8rem", color: "var(--muted)" }}>
                {c.user_email}
              </td>
              <td>{c.name_activity}</td>
              <td>{c.class_activity || "—"}</td>
              <td>
                <span
                  className={`badge ${c.participation_status === "accepted" ? "green" : c.participation_status === "refused" ? "red" : "orange"}`}
                >
                  {c.participation_status === "accepted"
                    ? "Accepté"
                    : c.participation_status === "refused"
                      ? "Refusé"
                      : "En attente"}
                </span>
              </td>
              <td style={{ fontSize: ".8rem", color: "var(--muted)" }}>
                {c.period || "—"}
              </td>
            </tr>
          ))}
          {contributions.length === 0 && (
            <tr>
              <td
                colSpan={6}
                style={{
                  textAlign: "center",
                  color: "var(--muted)",
                  padding: "2rem",
                }}
              >
                Aucune contribution
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );

  // ── Approval Actions ───────────────────────────────────────────────────────────
  const handleApproval = async (type, id, action) => {
    setError("");
    try {
      let url = "";
      switch (type) {
        case "profile":
          url = `/api/admin/profile-modification/${id}/${action}`;
          break;
        case "question":
          url = `/api/admin/questions/${id}/${action}`;
          break;
        case "suggestion":
          url = `/api/admin/suggestions/${id}/${action}`;
          break;
        case "activity":
          url = `/api/admin/activities/${id}/${action}`;
          break;
        case "activity_mod":
          url = `/api/admin/activity-modification/${id}/${action}`;
          break;
        default:
          throw new Error("Type d'approbation inconnu");
      }

      await apiFetch(url, { method: "PUT" });
      setActionMsg(
        `✅ ${action === "approve" ? "Approuvé" : "Rejeté"} avec succès`,
      );
      await loadAll();
    } catch (e) {
      setError(toErrorString(e));
    }
  };

  // ── Approvals View ────────────────────────────────────────────────────────────
  const renderApprovals = () => {
    if (!pendingApprovals) {
      return (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Chargement des approbations...</p>
        </div>
      );
    }

    const total = pendingApprovals.counts?.total || 0;

    return (
      <>
        <div className="view-header">
          <h2>File d'approbation</h2>
          <span>
            {total} demande{total !== 1 ? "s" : ""} en attente
          </span>
        </div>

        {total === 0 ? (
          <div className="empty-state">
            <i className="fas fa-clipboard-check"></i>
            <p>Aucune demande en attente d'approbation.</p>
          </div>
        ) : (
          <div className="approvals-grid">
            {/* Profile Modifications */}
            {pendingApprovals.profile_modifications?.length > 0 && (
              <div className="approval-section">
                <h3>
                  <i className="fas fa-user-edit"></i> Modifications de profil (
                  {pendingApprovals.profile_modifications.length})
                </h3>
                {pendingApprovals.profile_modifications.map((mod) => (
                  <div className="approval-card" key={mod.id}>
                    <div className="approval-card-header">
                      <div className="approval-icon">
                        <i className="fas fa-user-edit"></i>
                      </div>
                      <div className="approval-info">
                        <h4>{mod.user_email}</h4>
                        <p>Modification : {mod.field}</p>
                        <p>
                          Demandée le{" "}
                          {new Date(mod.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <div className="approval-actions">
                        <button
                          className="btn-approve"
                          onClick={() =>
                            handleApproval("profile", mod.id, "approve")
                          }
                          title="Approuver"
                        >
                          <i className="fas fa-check"></i>
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() =>
                            handleApproval("profile", mod.id, "reject")
                          }
                          title="Rejeter"
                        >
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                    <div className="approval-details">
                      <div className="approval-change">
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

            {/* Questions */}
            {pendingApprovals.pending_questions?.length > 0 && (
              <div className="approval-section">
                <h3>
                  <i className="fas fa-circle-question"></i> Questions (
                  {pendingApprovals.pending_questions.length})
                </h3>
                {pendingApprovals.pending_questions.map((q) => (
                  <div className="approval-card" key={q.id}>
                    <div className="approval-card-header">
                      <div className="approval-icon">
                        <i className="fas fa-circle-question"></i>
                      </div>
                      <div className="approval-info">
                        <h4>{q.title}</h4>
                        <p>Par : {q.user}</p>
                        <p>
                          Posée le{" "}
                          {new Date(q.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <div className="approval-actions">
                        <button
                          className="btn-approve"
                          onClick={() =>
                            handleApproval("question", q.id, "approve")
                          }
                          title="Approuver"
                        >
                          <i className="fas fa-check"></i>
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() =>
                            handleApproval("question", q.id, "reject")
                          }
                          title="Rejeter"
                        >
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                    {q.description && (
                      <div className="approval-desc">{q.description}</div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Suggestions */}
            {pendingApprovals.pending_suggestions?.length > 0 && (
              <div className="approval-section">
                <h3>
                  <i className="fas fa-lightbulb"></i> Suggestions (
                  {pendingApprovals.pending_suggestions.length})
                </h3>
                {pendingApprovals.pending_suggestions.map((s) => (
                  <div className="approval-card" key={s.id}>
                    <div className="approval-card-header">
                      <div className="approval-icon">
                        <i className="fas fa-lightbulb"></i>
                      </div>
                      <div className="approval-info">
                        <h4>{s.title}</h4>
                        <p>Par : {s.user}</p>
                        <p>
                          Proposée le{" "}
                          {new Date(s.created_at).toLocaleDateString("fr-FR")}
                        </p>
                      </div>
                      <div className="approval-actions">
                        <button
                          className="btn-approve"
                          onClick={() =>
                            handleApproval("suggestion", s.id, "approve")
                          }
                          title="Approuver"
                        >
                          <i className="fas fa-check"></i>
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() =>
                            handleApproval("suggestion", s.id, "reject")
                          }
                          title="Rejeter"
                        >
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                    {s.description && (
                      <div className="approval-desc">{s.description}</div>
                    )}
                    {s.rating > 0 && (
                      <div className="approval-rating">
                        <span className="rating-label">Importance :</span>
                        <div className="star-display">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <i
                              key={star}
                              className={`fas fa-star${star <= s.rating ? " filled" : ""}`}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Activities */}
            {pendingApprovals.pending_activities?.length > 0 && (
              <div className="approval-section">
                <h3>
                  <i className="fas fa-flask"></i> Activités (
                  {pendingApprovals.pending_activities.length})
                </h3>
                {pendingApprovals.pending_activities.map((a) => (
                  <div className="approval-card" key={a.id}>
                    <div className="approval-card-header">
                      <div className="approval-icon">
                        <i className="fas fa-flask"></i>
                      </div>
                      <div className="approval-info">
                        <h4>{a.name}</h4>
                        <p>Créé par : {a.creator}</p>
                        {a.class && <p>Classe : {a.class}</p>}
                      </div>
                      <div className="approval-actions">
                        <button
                          className="btn-approve"
                          onClick={() =>
                            handleApproval("activity", a.id, "approve")
                          }
                          title="Approuver"
                        >
                          <i className="fas fa-check"></i>
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() =>
                            handleApproval("activity", a.id, "reject")
                          }
                          title="Rejeter"
                        >
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                    {a.description && (
                      <div className="approval-desc">{a.description}</div>
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

  // ── Stats ─────────────────────────────────────────────────────────────────
  const renderStats = () => {
    const byOcc = groupCount(users, "occupation");
    const byRole = groupCount(users, "role");
    const byInst = groupCount(users, "institution");
    const total = users.length || 1;

    return (
      <>
        <div className="stats-grid">
          {[
            {
              icon: "fa-users",
              cls: "gold",
              val: users.length,
              label: "Total utilisateurs",
            },
            {
              icon: "fa-user-check",
              cls: "green",
              val: validated.length,
              label: "Validés",
            },
            {
              icon: "fa-user-clock",
              cls: "orange",
              val: pending.length,
              label: "En attente",
            },
            {
              icon: "fa-flask",
              cls: "blue",
              val: activities.length,
              label: "Activités",
            },
          ].map((s) => (
            <div className="stat-card" key={s.label}>
              <div className={`stat-icon ${s.cls}`}>
                <i className={`fas ${s.icon}`}></i>
              </div>
              <div className="stat-value">{s.val}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {[
          {
            title: "Répartition par occupation",
            data: byOcc,
            colorCls: "gold",
          },
          { title: "Répartition par rôle", data: byRole, colorCls: "purple" },
          {
            title: "Répartition par institution",
            data: byInst,
            colorCls: "green",
          },
        ].map(({ title, data, colorCls }) => (
          <div
            className="table-container"
            key={title}
            style={{ marginBottom: "1.2rem" }}
          >
            <span
              className="table-title"
              style={{ display: "block", marginBottom: "1rem" }}
            >
              {title}
            </span>
            <div className="bar-chart">
              {Object.entries(data)
                .sort((a, b) => b[1] - a[1])
                .map(([k, v]) => (
                  <div className="bar-row" key={k}>
                    <span className="bar-label">{k || "—"}</span>
                    <div className="bar-track">
                      <div
                        className={`bar-fill ${colorCls}`}
                        style={{ width: `${(v / total) * 100}%` }}
                      ></div>
                    </div>
                    <span className="bar-count">{v}</span>
                  </div>
                ))}
              {Object.keys(data).length === 0 && (
                <p style={{ color: "var(--muted)", fontSize: ".85rem" }}>
                  Aucune donnée
                </p>
              )}
            </div>
          </div>
        ))}
      </>
    );
  };

  // ── Settings ──────────────────────────────────────────────────────────────
  const renderSettings = () => (
    <div className="table-container">
      <span
        className="table-title"
        style={{ display: "block", marginBottom: "1.2rem" }}
      >
        Informations système
      </span>
      <table className="custom-table">
        <tbody>
          {[
            ["Base de données", "MySQL — db_lab"],
            ["Backend", "FastAPI — Port 8000"],
            ["Frontend", "React + Vite — Port 30000"],
            ["Authentification", "Session cookies + token"],
            ["Hachage", "pbkdf2_sha256 (passlib)"],
          ].map(([k, v]) => (
            <tr key={k}>
              <td style={{ fontWeight: 600, width: "200px" }}>{k}</td>
              <td style={{ color: "var(--muted)" }}>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  // ── Contacts ─────────────────────────────────────────────────────────────
  const renderContacts = () => (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.2rem",
        }}
      >
        <span style={{ fontSize: ".9rem", color: "var(--muted)" }}>
          {unreadContacts.length} message
          {unreadContacts.length !== 1 ? "s" : ""} \u00e0 traiter
        </span>
      </div>
      {contacts.length === 0 ? (
        <div className="empty-state">
          <i className="fas fa-envelope"></i>
          <p>Aucun message de contact</p>
        </div>
      ) : (
        contacts.map((c) => (
          <div
            className="contact-card"
            key={c.id_contact}
            style={{
              border: "1px solid var(--border)",
              borderRadius: "12px",
              padding: "1rem",
              marginBottom: ".8rem",
              background:
                c.status === "nouveau"
                  ? "rgba(255, 193, 7, 0.05)"
                  : "transparent",
            }}
          >
            <div
              className="contact-header"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "start",
                marginBottom: ".8rem",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: ".95rem",
                    fontWeight: 600,
                    color: "var(--dark)",
                  }}
                >
                  {c.name}
                </div>
                <div
                  style={{
                    fontSize: ".8rem",
                    color: "var(--muted)",
                    marginTop: ".2rem",
                  }}
                >
                  {c.email}
                </div>
              </div>
              <div style={{ display: "flex", gap: ".5rem" }}>
                <span
                  className={`badge ${c.is_join_request ? "blue" : "gray"}`}
                >
                  {c.is_join_request ? "Adhésion" : "Contact"}
                </span>
                <span
                  className={`badge ${c.status === "nouveau" ? "orange" : c.status === "lu" ? "gray" : c.status === "invité" ? "blue" : "green"}`}
                >
                  {c.status === "nouveau"
                    ? "À traiter"
                    : c.status === "lu"
                      ? "Lu"
                      : c.status === "invité"
                        ? "Invité"
                        : "Traité"}
                </span>
              </div>
            </div>
            <div style={{ marginBottom: ".8rem" }}>
              <div
                style={{
                  fontSize: ".9rem",
                  fontWeight: 500,
                  color: "var(--dark)",
                  marginBottom: ".3rem",
                }}
              >
                Sujet: {c.subject}
              </div>
              <div
                style={{
                  fontSize: ".85rem",
                  lineHeight: "1.5",
                  color: "var(--muted)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {c.message}
              </div>
            </div>
            <div
              style={{
                fontSize: ".75rem",
                color: "var(--muted)",
                marginBottom: ".8rem",
              }}
            >
              📅 {new Date(c.date_request).toLocaleString("fr-FR")}
            </div>
            <div className="contact-actions">
              {c.status === "nouveau" && (
                <button
                  className="contact-btn"
                  title="Marquer comme lu"
                  onClick={() =>
                    doAction(
                      () =>
                        apiFetch(`/api/contact/${c.id_contact}/read`, {
                          method: "PUT",
                        }),
                      "✓ Message marqué comme lu",
                    )
                  }
                >
                  <i className="fas fa-check"></i> Marquer comme lu
                </button>
              )}
              {c.is_join_request && (
                <button
                  className="contact-btn"
                  title="Envoyer une invitation"
                  onClick={() =>
                    doAction(
                      () =>
                        apiFetch(`/api/contact/${c.id_contact}/invite`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({}),
                        }),
                      "✓ Invitation envoyée à " + c.email,
                    )
                  }
                >
                  <i className="fas fa-paper-plane"></i> Envoyer invitation
                </button>
              )}
              <button
                className="contact-btn delete"
                title="Supprimer"
                onClick={() =>
                  doAction(
                    () =>
                      apiFetch(`/api/contact/${c.id_contact}`, {
                        method: "DELETE",
                      }),
                    "✓ Message supprimé",
                  )
                }
              >
                <i className="fas fa-trash"></i> Supprimer
              </button>
            </div>
          </div>
        ))
      )}
    </>
  );

  // ── Dispatch ──────────────────────────────────────────────────────────────
  const renderView = () => {
    if (loading)
      return (
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Chargement…</p>
        </div>
      );
    switch (view) {
      case "dashboard":
        return renderDashboard();
      case "users":
        return renderUsers();
      case "validation":
        return renderValidation();
      case "approvals":
        return renderApprovals();
      case "contacts":
        return renderContacts();
      case "activities":
        return renderActivities();
      case "events":
        return renderEvents();
      case "questions":
        return renderQuestions();
      case "contributions":
        return renderContributions();
      case "stats":
        return renderStats();
      case "settings":
        return renderSettings();
      default:
        return renderDashboard();
    }
  };

  // ══════════════════════════════════════════════════════════════════════════
  // MODAL CONTENT
  // ══════════════════════════════════════════════════════════════════════════
  const renderModal = () => {
    if (!modal) return null;
    const { type, data } = modal;

    const MODAL_TITLES = {
      createActivity: "Créer une activité",
      createEvent: "Créer un événement",
      createUser: "Créer un nouvel utilisateur",
      editUser: `Modifier l'utilisateur`,
      roleUser: "Attribuer un rôle",
      inviteUser: "Inviter à une activité",
      answerQuestion: "Répondre à la question",
    };

    return (
      <Modal title={MODAL_TITLES[type] || ""} onClose={closeModal}>
        {/* ── Create Activity ── */}
        {type === "createActivity" && (
          <div className="form-grid">
            {[
              { name: "id_activity", label: "ID activité *", ph: "Ex: ACT01" },
              {
                name: "name_activity",
                label: "Nom *",
                ph: "Nom de l'activité",
              },
              { name: "class_activity", label: "Classe", ph: "Ex: Recherche" },
            ].map((f) => (
              <div className="form-group" key={f.name}>
                <label>{f.label}</label>
                <input
                  name={f.name}
                  placeholder={f.ph}
                  value={form[f.name] || ""}
                  onChange={fc}
                />
              </div>
            ))}
            <div className="form-group">
              <label>Statut</label>
              <select
                name="status"
                value={form.status || "en attente"}
                onChange={fc}
              >
                <option value="en attente">En attente</option>
                <option value="approuvé">Approuvé</option>
              </select>
            </div>
            <div className="form-group full">
              <label>Description</label>
              <textarea
                name="description"
                placeholder="Description de l'activité…"
                value={form.description || ""}
                onChange={fc}
              />
            </div>
          </div>
        )}

        {/* ── Create Event ── */}
        {type === "createEvent" && (
          <div className="form-grid">
            <div className="form-group full">
              <label>Titre *</label>
              <input
                name="title"
                placeholder="Titre de l'événement"
                value={form.title || ""}
                onChange={fc}
              />
            </div>
            <div className="form-group">
              <label>Type</label>
              <select
                name="event_type"
                value={form.event_type || "événement"}
                onChange={fc}
              >
                {[
                  "conférence",
                  "hackathon",
                  "atelier",
                  "séminaire",
                  "événement",
                ].map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Date</label>
              <input
                type="date"
                name="event_date"
                value={form.event_date || ""}
                onChange={fc}
              />
            </div>
            <div className="form-group full">
              <label>Lieu</label>
              <input
                name="location"
                placeholder="Ex: Amphithéâtre A, Yaoundé"
                value={form.location || ""}
                onChange={fc}
              />
            </div>
            <div className="form-group full">
              <label>Description</label>
              <textarea
                name="description"
                placeholder="Description de l'événement…"
                value={form.description || ""}
                onChange={fc}
              />
            </div>
          </div>
        )}

        {/* ── Create User ── */}
        {type === "createUser" && (
          <div className="form-grid">
            <div className="form-group full">
              <label>Nom complet *</label>
              <input
                name="name"
                placeholder="Ex: Jean Dupont"
                value={form.name || ""}
                onChange={fc}
                autoFocus
              />
            </div>
            <p style={{ fontSize: ".85rem", color: "var(--muted)", gridColumn: "1/-1" }}>
              ℹ️ L'email et le mot de passe seront générés automatiquement. L'utilisateur pourra les modifier après connexion.
            </p>
          </div>
        )}

        {/* ── Edit User ── */}
        {type === "editUser" && (
          <div className="form-grid">
            {[
              { name: "name", label: "Nom complet", ph: "Nom" },
              { name: "institution", label: "Institution", ph: "Institution" },
              { name: "level", label: "Niveau", ph: "Ex: M2" },
              { name: "domain", label: "Domaine", ph: "Domaine" },
            ].map((f) => (
              <div className="form-group" key={f.name}>
                <label>{f.label}</label>
                <input
                  name={f.name}
                  placeholder={f.ph}
                  value={form[f.name] || ""}
                  onChange={fc}
                />
              </div>
            ))}
            <div className="form-group">
              <label>Occupation</label>
              <select
                name="occupation"
                value={form.occupation || ""}
                onChange={fc}
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
                value={form.motivation || ""}
                onChange={fc}
              />
            </div>
          </div>
        )}

        {/* ── Role ── */}
        {type === "roleUser" && (
          <div className="form-grid">
            <div className="form-group full">
              <label>Rôle à attribuer</label>
              <select name="role" value={form.role || "membre"} onChange={fc}>
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* ── Invite User ── */}
        {type === "inviteUser" && (
          <div className="form-grid">
            {!data?.forActivity && (
              <div className="form-group full">
                <label>ID de l'activité *</label>
                <select
                  name="activity_id"
                  value={form.activity_id || ""}
                  onChange={fc}
                >
                  <option value="">Sélectionner une activité…</option>
                  {activities.map((a) => (
                    <option key={a.id_activity} value={a.id_activity}>
                      {a.name_activity}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {data?.forActivity && (
              <div className="form-group full">
                <label>Email de l'utilisateur à inviter *</label>
                <select name="email" value={form.email || ""} onChange={fc}>
                  <option value="">Sélectionner un utilisateur…</option>
                  {users.map((u) => (
                    <option key={u.email} value={u.email}>
                      {u.name} ({u.email})
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div
              className="form-group full"
              style={{ fontSize: ".82rem", color: "var(--muted)" }}
            >
              {data?.forActivity ? (
                <>
                  Activité :{" "}
                  <strong>
                    {form.activity_id || data?.initial?.activity_id}
                  </strong>
                </>
              ) : (
                <>
                  Utilisateur : <strong>{data?.email}</strong>
                </>
              )}
            </div>
          </div>
        )}

        {/* ── Answer Question ── */}
        {type === "answerQuestion" && (
          <div className="form-grid">
            <div className="form-group full">
              <label>Question</label>
              <p
                style={{
                  fontSize: ".88rem",
                  color: "var(--dark)",
                  padding: ".6rem .95rem",
                  background: "var(--bg)",
                  borderRadius: "10px",
                  margin: 0,
                }}
              >
                {data?.q_title}
              </p>
            </div>
            <div className="form-group full">
              <label>Titre de la réponse *</label>
              <input
                name="libelle_response"
                placeholder="Résumé de la réponse"
                value={form.libelle_response || ""}
                onChange={fc}
              />
            </div>
            <div className="form-group full">
              <label>Détails</label>
              <textarea
                name="description_response"
                placeholder="Développez votre réponse…"
                value={form.description_response || ""}
                onChange={fc}
              />
            </div>
          </div>
        )}

        <div className="modal-actions">
          <button
            className="btn-secondary"
            onClick={closeModal}
            disabled={saving}
          >
            Annuler
          </button>
          <button
            className="btn-primary"
            onClick={handleModalSubmit}
            disabled={saving}
          >
            <i
              className={`fas ${saving ? "fa-spinner fa-spin" : "fa-check"}`}
            ></i>
            {saving ? "Enregistrement…" : "Confirmer"}
          </button>
        </div>
      </Modal>
    );
  };

  // ══════════════════════════════════════════════════════════════════════════
  // LAYOUT
  // ══════════════════════════════════════════════════════════════════════════
  const navSections = [...new Set(VIEWS.map((v) => v.section))];

  return (
    <div className="admin-layout">
      {/* ── SIDEBAR ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <img
            src="/betalabs.png"
            alt="BetaLab"
            className="sidebar-logo-img"
          />
          <span className="logo-text">BetaLab</span>
          <span className="logo-badge">ADMIN</span>
        </div>

        {navSections.map((sec) => (
          <div key={sec}>
            <div className="nav-section">{sec}</div>
            {VIEWS.filter((v) => v.section === sec).map((v) => (
              <button
                key={v.id}
                className={`nav-item${view === v.id ? " active" : ""}`}
                onClick={() => setView(v.id)}
              >
                <i className={`fas ${v.icon}`}></i>
                {v.label}
                {v.id === "validation" && pending.length > 0 && (
                  <span className="nav-badge">{pending.length}</span>
                )}
                {v.id === "contacts" && unreadContacts.length > 0 && (
                  <span className="nav-badge">{unreadContacts.length}</span>
                )}
                {v.id === "questions" && pendingQ.length > 0 && (
                  <span className="nav-badge">{pendingQ.length}</span>
                )}
              </button>
            ))}
          </div>
        ))}

        <div className="sidebar-footer">
          <div className="admin-info">
            <div className="admin-avatar">A</div>
            <div className="admin-details">
              <div className="name">Administrateur</div>
              <div className="role-label">Super Admin</div>
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
            <h1>{PAGE_META[view]?.title}</h1>
            <p>{PAGE_META[view]?.sub}</p>
          </div>
          <div className="topbar-right">
            <span className="topbar-badge">ADMIN</span>
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
          {renderView()}
        </div>
      </div>

      {/* ── MODALS ── */}
      {renderModal()}
    </div>
  );
}

// ── Util ─────────────────────────────────────────────────────────────────────
function groupCount(arr, key) {
  return arr.reduce((acc, item) => {
    const val = item[key] || "—";
    acc[val] = (acc[val] || 0) + 1;
    return acc;
  }, {});
}
