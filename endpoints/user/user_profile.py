"""
Profil utilisateur — BetaLab
Endpoints:
  GET    /api/user/profile                    → profil connecté
  PUT    /api/user/profile/update             → modifier profil
  GET    /api/user/dashboard                  → données dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

import models
from database import get_db
from dependencies import sessions, get_password_hash, verify_password

router = APIRouter(prefix="/api/user", tags=["Utilisateur - Profil"])


@router.get("/profile")
async def get_user_profile(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère le profil complet de l'utilisateur connecté."""
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
    
    # Compter contributions
    contributions_count = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "accepted"
    ).count()
    
    # Compter invitations en attente
    pending_count = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "pending"
    ).count()
    
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
        "contributions_count": contributions_count,
        "pending_invitations": pending_count,
    }


@router.put("/profile/update")
async def update_user_profile(
    request: Request,
    name: Optional[str] = None,
    occupation: Optional[str] = None,
    institution: Optional[str] = None,
    level: Optional[str] = None,
    domain: Optional[str] = None,
    motivation: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Modifie le profil de l'utilisateur connecté."""
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
    
    # Mettre à jour uniquement les champs fournis
    if name is not None:
        user.name = name
    if occupation is not None:
        user.occupation = occupation
    if institution is not None:
        user.institution = institution
    if level is not None:
        user.level = level
    if domain is not None:
        user.domain = domain
    if motivation is not None:
        user.motivation = motivation
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Profil mis à jour avec succès",
        "user": {
            "mailer": user.email,
            "name": user.name,
            "occupation": user.occupation,
            "institution": user.institution,
            "level": user.level,
            "domain": user.domain,
            "motivation": user.motivation,
        }
    }


@router.put("/profile/change-password")
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """Change le mot de passe de l'utilisateur."""
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
    
    # Vérifier ancien mot de passe
    from dependencies import verify_password
    if not verify_password(current_password, user.password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Valider nouveau mot de passe
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Nouveau mot de passe trop court (8 caractères min)")
    
    # Mettre à jour
    user.password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Mot de passe changé avec succès"}


@router.get("/dashboard")
async def get_dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Récupère les données du dashboard utilisateur.
    Inclut: contributions, invitations, profil, statistiques.
    """
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
    
    # Récupérer contributions acceptées
    contributions = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "accepted"
    ).all()
    
    # Récupérer invitations en attente
    invitations = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "pending"
    ).all()
    
    # Récupérer questions de l'utilisateur
    questions = db.query(models.Question).filter(
        models.Question.id_user == user_email
    ).all()
    
    # Récupérer suggestions de l'utilisateur
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.id_user == user_email
    ).all()
    
    return {
        "user": {
            "mailer": user.email,
            "name": user.name,
            "role": user.role,
            "validated": user.validated,
        },
        "statistics": {
            "contributions_count": len(contributions),
            "pending_invitations": len(invitations),
            "questions_count": len(questions),
            "suggestions_count": len(suggestions),
        },
        "contributions": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "status": c.activity.status,
                "period": str(c.period) if c.period else None,
            }
            for c in contributions
        ],
        "pending_invitations": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "class_activity": c.activity.class_activity,
                "description": c.activity.description,
            }
            for c in invitations
        ],
        "recent_questions": [
            {
                "id_question": q.id_question,
                "libele_question": q.libele_question,
                "description": q.description_question,
            }
            for q in questions[-5:]  # 5 dernières
        ],
        "recent_suggestions": [
            {
                "id_suggest": s.id_suggest,
                "libele": s.libele,
                "note": s.note,
            }
            for s in suggestions[-5:]  # 5 dernières
        ],
    }
