"""
Dépendances partagées entre tous les routeurs.
- sessions : DEPRECATED (remplacé par SessionManager)
- pwd_context : configuration du hachage des mots de passe
- get_current_user : dépendance FastAPI pour protéger les routes
"""

from fastapi import HTTPException, Request, Depends, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models
from database import get_db
from session_manager import SessionManager

# ── Stockage des sessions actives (déclaré mais inutilisé — utiliser SessionManager) ──────────────────────────────
sessions: dict[str, str] = {}  # DEPRECATED: Utilisé uniquement pour rétrocompatibilité

# ── Contexte de hachage des mots de passe ────────────────────────────────────
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ── Dépendance : utilisateur authentifié ─────────────────────────────────────
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> models.User:
    """
    Récupère l'utilisateur authentifié à partir du token de session.
    Utilise SessionManager pour les sessions persistantes en BD.
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    # Utiliser le SessionManager pour récupérer l'utilisateur
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de session invalide ou expiré",
        )
    
    return user
