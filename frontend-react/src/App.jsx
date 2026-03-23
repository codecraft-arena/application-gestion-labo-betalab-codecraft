/**
 * App.jsx — Routes de l'application BetaLab.
 * Ajout : /adhesion/:token → formulaire d'adhésion via invitation
 */
import { Routes, Route } from "react-router-dom";
import Layout      from "./components/Layout";
import Home        from "./pages/Home";
import Login       from "./pages/Login";
import AdminLogin  from "./pages/AdminLogin";
import Activites   from "./pages/Activites";
import DashUser    from "./pages/DashUser";
import DashAdmin   from "./pages/DashAdmin";
import APropos     from "./pages/APropos";
import FAQ         from "./pages/FAQ";
import Blog        from "./pages/Blog";
import NousRejoindre from "./pages/NousRejoindre";
import Contact     from "./pages/Contact";
import Fondateurs  from "./pages/Fondateurs";
import AdhesionForm from "./pages/AdhesionForm";  // ← NOUVEAU

function App() {
  return (
    <Routes>
      {/* Pages avec Navbar + Footer */}
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
      </Route>

      {/* Pages sans layout partagé */}
      <Route path="/login"          element={<Login />} />
      <Route path="/admin"          element={<AdminLogin />} />
      <Route path="/activites"      element={<Activites />} />
      <Route path="/a-propos"       element={<APropos />} />
      <Route path="/faq"            element={<FAQ />} />
      <Route path="/blog"           element={<Blog />} />
      <Route path="/nous-rejoindre" element={<NousRejoindre />} />
      <Route path="/contact"        element={<Contact />} />
      <Route path="/fondateurs"     element={<Fondateurs />} />

      {/* Formulaire d'adhésion via lien d'invitation */}
      <Route path="/adhesion/:token" element={<AdhesionForm />} />   {/* ← NOUVEAU */}

      {/* Dashboards */}
      <Route path="/dashuser"  element={<DashUser />} />
      <Route path="/dashadmin" element={<DashAdmin />} />
    </Routes>
  );
}

export default App;
