"""
Routeur d'authentification — Système amélioré avec:
  - Sessions persistantes en BD
  - Admin users en BD (au lieu de hardcoding)
  - Rate limiting
  - CSRF protection

Endpoints :
  POST /connexion     → connexion utilisateur (cookie de session)
  POST /admin-login   → connexion administrateur améliorée
  GET  /logout        → déconnexion (suppression du cookie et BD)
  GET  /csrf-token    → récupérer token CSRF
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session

import models
from database import get_db
from dependencies import verify_password
from session_manager import SessionManager
from admin_auth import AdminAuthManager
from security import CSRFManager, check_rate_limit, limiter_login

router = APIRouter(tags=["Authentification"])


@router.post("/connexion")
async def connexion(
    request: Request,
    mailer: EmailStr = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Connexion utilisateur — crée une session persistante en BD."""
    
    # Rate limiting
    check_rate_limit(limiter_login, request)
    
    # Vérifier utilisateur
    user = db.query(models.User).filter(models.User.mailer == mailer).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )
    
    # Vérifier mot de passe
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect",
        )
    
    # Vérifier validations
    if not user.validated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte n'a pas encore été validé par un administrateur",
        )
    
    if user.suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte a été suspendu",
        )
    
    # Créer session persistante en BD
    user_agent = request.headers.get("user-agent", "")
    ip_address = request.client.host if request.client else ""
    
    token = SessionManager.create_session(
        db=db,
        user_mailer=mailer,
        user_agent=user_agent,
        ip_address=ip_address,
        duration_hours=24
    )
    
    # Générer token CSRF
    csrf_token = CSRFManager.generate_token(db)
    
    # Retourner avec cookies
    response = RedirectResponse(url="/dashuser/", status_code=303)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
        secure=True  # À décommenter en production (HTTPS)
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return response


@router.post("/admin-login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Connexion administrateur — authentification en BD au lieu de hardcoding."""
    
    # Rate limiting (strict pour admin)
    check_rate_limit(limiter_login, request)
    
    # Vérifier admin en BD
    admin = AdminAuthManager.verify_admin(db, username, password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants administrateur incorrects",
        )
    
    # Créer session persistante pour admin
    token = SessionManager.create_session(
        db=db,
        user_mailer=f"admin_{admin.username}",  # Préfixe pour différencier
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
        duration_hours=8  # Sessions admin plus courtes
    )
    
    # Mettre à jour last_login
    admin.last_login = __import__('datetime').datetime.utcnow()
    db.commit()
    
    return JSONResponse(
        content={
            "message": "Connexion admin réussie",
            "redirect": "/dashadmin",
            "token": token
        },
        status_code=200,
    )


@router.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Déconnexion — invalide la session en BD et supprime le cookie."""
    
    token = request.cookies.get("session_token")
    if token:
        SessionManager.revoke_session(db, token)
    
    response = JSONResponse(content={"message": "Déconnexion réussie"})
    response.delete_cookie(key="session_token")
    response.delete_cookie(key="csrf_token")
    return response


@router.get("/csrf-token")
async def get_csrf_token(request: Request, db: Session = Depends(get_db)):
    """Récupère un token CSRF pour les formulaires."""
    
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Optionnel: lier le token CSRF à la session
    csrf_token = CSRFManager.generate_token(db)
    
    return {"csrf_token": csrf_token}
