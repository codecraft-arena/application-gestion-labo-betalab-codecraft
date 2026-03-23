/**
 * Page de connexion administrateur BetaLab.
 * Similaire à Login mais avec style admin (fond plus sombre, bouton or).
 * Envoie un FormData à /admin-login et redirige selon la réponse JSON.
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  /* Soumission du formulaire admin — envoie les identifiants et récupère l'URL de redirection */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const res = await fetch("/admin-login", {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Identifiants admin incorrects");
      }

      const data = await res.json();
      if (data.redirect) {
        navigate(data.redirect);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-wrapper">
        {/* Left Panel */}
        <div
          className="left-panel"
          style={{ background: "linear-gradient(135deg, #14213d, #0a1628)" }}
        >
          <div className="brand">
            <img
              src="/betalabs.png"
              alt="BetaLab"
              style={{ height: "120px", width: "auto" }}
            />
            <span>BetaLab Admin</span>
          </div>
          <div className="hero-text">
            <h1>
              Panneau
              <br />
              <span
                style={{
                  background: "linear-gradient(135deg, #e9b000, #c89800)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Administrateur
              </span>
            </h1>
            <p>
              Accédez au tableau de bord d'administration pour gérer les
              utilisateurs, les activités et les statistiques du laboratoire.
            </p>
          </div>
          <div className="features">
            <div className="feature-item">
              <div
                className="feature-dot"
                style={{
                  background: "linear-gradient(135deg, #e9b000, #c89800)",
                }}
              ></div>
              <span>Gestion des utilisateurs</span>
            </div>
            <div className="feature-item">
              <div
                className="feature-dot"
                style={{
                  background: "linear-gradient(135deg, #e9b000, #c89800)",
                }}
              ></div>
              <span>Suivi des activités</span>
            </div>
            <div className="feature-item">
              <div
                className="feature-dot"
                style={{
                  background: "linear-gradient(135deg, #e9b000, #c89800)",
                }}
              ></div>
              <span>Statistiques avancées</span>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <div className="login-box">
            <h2>Admin</h2>
            <p className="login-subtitle">Connexion administrateur</p>

            {error && <div className="alert-error">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nom d'utilisateur</label>
                <div className="input-wrap">
                  <i className="fas fa-user-shield"></i>
                  <input
                    type="text"
                    placeholder="admin"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Mot de passe</label>
                <div className="input-wrap">
                  <i className="fas fa-lock"></i>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                className="btn-login"
                style={{
                  background: "linear-gradient(135deg, #e9b000, #c89800)",
                }}
                disabled={loading}
              >
                {loading ? "Connexion..." : "Accéder au dashboard"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
