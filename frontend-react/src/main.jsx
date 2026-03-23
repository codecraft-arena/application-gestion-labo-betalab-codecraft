/**
 * Point d'entrée de l'application React BetaLab.
 * - StrictMode active les vérifications supplémentaires en développement
 * - BrowserRouter permet la navigation côté client (React Router v6)
 * - Le CSS global est importé ici pour être disponible dans toute l'app
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/global.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
