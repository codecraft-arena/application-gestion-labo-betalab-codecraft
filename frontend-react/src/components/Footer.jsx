/**
 * Pied de page du site BetaLab.
 * Affiche 4 colonnes : description, navigation, compte, contact.
 * Intègre un NeuralCanvas animé en arrière-plan.
 */
import { Link } from "react-router-dom";
import NeuralCanvas from "./NeuralCanvas";

export default function Footer() {
  return (
    <footer
      className="footer"
      style={{ position: "relative", overflow: "hidden" }}
    >
      {/* Animation de fond — réseau neuronal décoratif */}
      <NeuralCanvas
        nodeCount={40}
        connectionDist={120}
        mouseRadius={150}
        opacity={0.65}
      />
      <div className="container" style={{ position: "relative", zIndex: 1 }}>
        <div className="footer-grid">
          {/* Colonne 1 : Description et réseaux sociaux */}
          <div>
            <p
              style={{ color: "#86868b", lineHeight: 1.7, fontSize: "0.95rem" }}
            >
              Laboratoire d'excellence en informatique, dédié à l'innovation et
              la recherche.
            </p>
            <div className="social-links" style={{ marginTop: "1rem" }}>
              <a href="#">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="#">
                <i className="fab fa-linkedin"></i>
              </a>
              <a href="#">
                <i className="fab fa-github"></i>
              </a>
            </div>
          </div>
          <div>
            <h4 className="footer-title">Navigation</h4>
            <ul className="footer-links">
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
            <Link to="/faq">FAQ</Link>
          </li>
          <li>
            <Link to="/contact">Contact</Link>
          </li>
            </ul>
          </div>
          <div>
            <h4 className="footer-title">Contact</h4>
            <ul className="footer-links">
              <li>
                <a href="#">contact@beta-lab.fr</a>
              </li>
              <li>
                <a href="#">+237 675 75 99 00 / +33 7 49 55 61 71</a>
              </li>
              <li>
                <a href="#">Paris, France</a>
              </li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 BetaLab. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  );
}
