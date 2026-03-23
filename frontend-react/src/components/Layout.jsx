/**
 * Layout partagé : Navbar + contenu (Outlet) + Footer.
 * Utilisé uniquement pour la page d'accueil (Home).
 * Les autres pages gèrent leur propre Navbar/Footer directement.
 */
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";

export default function Layout() {
  return (
    <>
      <Navbar />
      <Outlet />
      <Footer />
    </>
  );
}
