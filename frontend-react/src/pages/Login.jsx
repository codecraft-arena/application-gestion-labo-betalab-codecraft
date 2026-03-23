/**
 * Page de connexion utilisateur BetaLab.
 * Panneau gauche : branding, logo, fonctionnalités.
 * Panneau droit : formulaire email/mot de passe.
 * Envoie un FormData à /connexion puis redirige vers /dashuser.
 */
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  /* Soumission du formulaire — envoie les identifiants au backend */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("password", password);
      const res = await fetch("/connexion", {
        method: "POST",
        credentials: "include",
        body: formData,
        redirect: "follow",
      });
      if (res.redirected) {
        navigate("/dashuser");
        return;
      }
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Identifiants incorrects");
      }
      navigate("/dashuser");
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
        <div className="left-panel">
          <div className="brand">
            <Link to="/" className="brand-link">
              <img
                src="/betalabs.png"
                alt="BetaLab"
                style={{ height: "120px", width: "auto" }}
              />
            </Link>
          </div>
          <Link to="/" className="back-home">
            <i className="fas fa-arrow-left"></i> Retour à l'accueil
          </Link>
          <div className="hero-text">
            <h1>
              Bienvenue dans
              <br />
              votre <span>Laboratoire</span>
            </h1>
            <p>
              Connectez-vous pour accéder à votre espace, gérer vos projets et
              collaborer avec l'équipe.
            </p>
          </div>
          <div className="features">
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Accès à vos projets et contributions</span>
            </div>
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Collaboration avec l'équipe</span>
            </div>
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Ressources exclusives</span>
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="right-panel">
          <div className="login-box">
            <h2>Connexion</h2>
            <p className="login-subtitle">Accédez à votre espace BetaLab</p>

            {error && <div className="alert-error">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Email</label>
                <div className="input-wrap">
                  <i className="fas fa-envelope"></i>
                  <input
                    type="email"
                    placeholder="votre@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
              <button type="submit" className="btn-login" disabled={loading}>
                {loading ? "Connexion..." : "Se connecter"}
              </button>
            </form>

            <div className="login-footer">
              <p>
                <a
                  href="/admin"
                  onClick={(e) => {
                    e.preventDefault();
                    navigate("/admin");
                  }}
                >
                  Se connecter en tant qu'admin
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
