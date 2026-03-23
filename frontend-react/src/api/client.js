/**
 * Client API pour communiquer avec le backend FastAPI.
 * API_BASE est vide car Vite proxy les requêtes vers localhost:8000.
 * Toutes les requêtes incluent les cookies de session (credentials: "include").
 */
const API_BASE = "";

/**
 * Requête GET/générique avec gestion d'erreurs JSON.
 * @param {string} path  — chemin relatif (ex: "/api/me")
 * @param {object} options — options fetch supplémentaires
 */
export async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur serveur");
  }
  return res.json();
}

/** Requête POST avec body JSON. */
export async function apiPost(path, body, options = {}) {
  return apiFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...options.headers },
    body: JSON.stringify(body),
    ...options,
  });
}

/** Requête POST avec FormData (formulaires de connexion). Gère les redirections serveur. */
export async function apiPostForm(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });
  if (res.redirected) {
    window.location.href = res.url;
    return null;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erreur serveur");
  }
  return res.json();
}
