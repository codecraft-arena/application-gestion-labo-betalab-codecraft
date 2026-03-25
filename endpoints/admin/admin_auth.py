"""
Authentification administrateur — BetaLab
Endpoints:
  POST   /api/admin/login        → connexion admin
  POST   /api/admin/logout       → déconnexion admin
  POST   /api/admin/register     → créer nouvel admin (admin seulement)
  GET    /api/admin/me           → profil admin connecté
"""

import secrets
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import EmailStr

import models
from database import get_db
from session_manager import SessionManager
from admin_auth import AdminAuthManager
from dependencies import get_password_hash, verify_password

router = APIRouter(prefix="/api/admin", tags=["Admin - Auth"])

# ── Stockage des sessions admin (dépôt temporaire) ────────
admin_sessions: dict[str, str] = {}


@router.post("/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Connexion administrateur."""
    
    # Vérifier admin en base de données
    admin = AdminAuthManager.verify_admin(db, username, password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )
    
    # Créer session admin avec SessionManager
    token = SessionManager.create_session(
        db=db,
        user_mailer=f"admin_{username}",  # Préfixe pour différencier
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
        duration_hours=8
    )
    
    # Mettre à jour last_login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Retourner le token
    return JSONResponse(
        content={
            "message": "Connexion admin réussie",
            "token": token,
            "redirect": "/dashadmin"
        },
        status_code=200
    )
    return response


@router.get("/me")
async def get_admin_profile(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère le profil de l'admin connecté."""
    token = request.cookies.get("session_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    # Vérifier la session en BD
    session = SessionManager.get_session(db, token)
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    # Vérifier que c'est une session admin
    if not session.user_mailer.startswith("admin_"):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    # Extraire le username admin
    admin_username = session.user_mailer.replace("admin_", "")
    
    admin = db.query(models.AdminUser).filter(
        models.AdminUser.username == admin_username
    ).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin non trouvé")
    
    return {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
        "role": admin.role,
        "is_active": admin.is_active,
        "created_at": admin.created_at.isoformat(),
        "last_login": admin.last_login.isoformat() if admin.last_login else None,
    }


@router.post("/logout")
async def admin_logout(request: Request, db: Session = Depends(get_db)):
    """Déconnexion administrateur."""
    token = request.cookies.get("session_token")
    
    if token:
        SessionManager.revoke_session(db, token)
    
    response = JSONResponse(content={"message": "Déconnexion admin réussie"})
    response.delete_cookie("session_token")
    return response


@router.post("/register")
async def create_admin(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    role: str = Form(default="admin"),
    db: Session = Depends(get_db),
):
    """Crée un nouvel administrateur (admin seulement)."""
    token = request.cookies.get("admin_token")
    
    if not token or token not in admin_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    # Vérifier que c'est un super-admin
    requester_username = admin_sessions[token]
    requester = db.query(models.AdminUser).filter(
        models.AdminUser.username == requester_username
    ).first()
    
    if not requester or requester.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un super-admin peut créer des administrateurs",
        )
    
    # Vérifications
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (8 caractères min)")
    
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")
    
    if db.query(models.AdminUser).filter(models.AdminUser.username == username).first():
        raise HTTPException(status_code=400, detail="Cet identifiant admin existe déjà")
    
    if db.query(models.AdminUser).filter(models.AdminUser.email == email).first():
        raise HTTPException(status_code=400, detail="Cet email admin existe déjà")
    
    # Créer admin
    new_admin = models.AdminUser(
        username=username,
        email=email,
        password=get_password_hash(password),
        role=role,
        is_active=True,
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return {
        "message": "Administrateur créé avec succès",
        "username": new_admin.username,
        "email": new_admin.email,
        "role": new_admin.role,
    }
