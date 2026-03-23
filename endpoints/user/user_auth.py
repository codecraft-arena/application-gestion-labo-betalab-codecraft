"""
Authentification utilisateur — BetaLab
Endpoints:
  POST   /api/user/login        → connexion
  POST   /api/user/register     → inscription
  GET    /api/user/logout       → déconnexion
  GET    /api/user/me           → profil connecté
"""

import secrets
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

import models
from database import get_db
from session_manager import SessionManager
from dependencies import get_password_hash, verify_password

router = APIRouter(prefix="/api/user", tags=["Utilisateur - Auth"])


@router.post("/login")
async def user_login(
    request: Request,
    email: EmailStr = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Connexion utilisateur — crée un cookie de session httpOnly."""
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )
    
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
        )
    
    if not user.validated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte non validé par l'administrateur",
        )
    
    if user.suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte suspendu",
        )
    
    # Créer session avec SessionManager
    token = SessionManager.create_session(
        db=db,
        user_mailer=user.email,  # Utiliser email directement
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
        duration_hours=24
    )
    
    response = JSONResponse(
        content={
            "message": "Connexion réussie",
            "user_email": user.email,
            "name": user.name,
        },
        status_code=200,
    )
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return response


@router.post("/register")
async def user_register(
    mailer: EmailStr = Form(...),
    name: str = Form(...),
    birthdate: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    occupation: str = Form(...),
    institution: str = Form(...),
    level: str = Form(default=""),
    domain: str = Form(default=""),
    motivation: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Inscription utilisateur (auto-inscription désactivée ou via invitation)."""
    
    # Vérifications
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (8 caractères min)")
    
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")
    
    if db.query(models.User).filter(models.User.email == mailer).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    try:
        birthdate_obj = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")
    
    # Créer utilisateur (non validé par défaut)
    user = models.User(
        mailer=mailer,
        name=name,
        birthdate=birthdate_obj,
        password=get_password_hash(password),
        occupation=occupation,
        institution=institution,
        level=level,
        domain=domain,
        motivation=motivation,
        validated=False,  # Doit être validé par admin
        suspended=False,
        role="membre",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Inscription réussie! Votre compte sera activé après validation par l'administrateur.",
        "user_email": user.email,
        "name": user.name,
    }


@router.get("/logout")
async def user_logout(request: Request, db: Session = Depends(get_db)):
    """Déconnexion utilisateur."""
    token = request.cookies.get("session_token")
    
    if token:
        # Supprimer de la mémoire
        if token in sessions:
            del sessions[token]
        
        # Supprimer de la BD
        db.query(models.Session).filter(models.Session.token == token).delete()
        db.commit()
    
    response = JSONResponse(content={"message": "Déconnexion réussie"})
    response.delete_cookie("session_token")
    return response


@router.get("/me")
async def get_current_user_profile(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère le profil de l'utilisateur connecté."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    user = db.query(models.User).filter(models.User.email == user_email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {
        "mailer": user.email,
        "name": user.name,
        "birthdate": str(user.birthdate) if user.birthdate else None,
        "occupation": user.occupation,
        "institution": user.institution,
        "level": user.level,
        "domain": user.domain,
        "motivation": user.motivation,
        "role": user.role,
        "validated": user.validated,
        "suspended": user.suspended,
    }
