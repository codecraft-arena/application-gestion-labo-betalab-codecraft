/**
 * Barre de navigation principale du site BetaLab.
 * Affichée en haut de chaque page (sauf dashboards).
 * Contient le logo et 8 liens de navigation (React Router).
 */
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container">
        {/* Logo BetaLab — lien vers l'accueil */}
        <Link className="navbar-brand" to="/">
          <img src="/betalabs.png" alt="BetaLab" className="navbar-logo" />
        </Link>
        {/* Liens de navigation */}
        <ul className="nav-links">
          <li>
            <Link to="/">Accueil</Link>
          </li>
          <li>
            <Link to="/activites">Activités</Link>
          </li>
          <li>
            <Link to="/fondateurs">Fondateurs</Link>
          </li>
          <li>
            <Link to="/blog">Blog</Link>
          </li>
          <li>
            <Link to="/a-propos">A propos</Link>
          </li>
          <li>
            <Link to="/nous-rejoindre">Nous rejoindre</Link>
          </li>
          <li>
            <Link to="/faq">FAQ</Link>
          </li>
          <li>
            <Link to="/contact">Contact</Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}
