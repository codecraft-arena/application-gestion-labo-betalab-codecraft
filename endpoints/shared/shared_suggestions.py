"""
Suggestions (Partagé) — BetaLab
Endpoints:
  POST   /api/suggestions                 → user: soumettre suggestion
  GET    /api/suggestions/user/{mailer}   → user: ses suggestions
  GET    /api/suggestions                 → admin: toutes suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional, List

import models, schemas
from database import get_db
from dependencies import sessions

router = APIRouter(tags=["Suggestions"])


@router.post("/api/suggestions", response_model=schemas.SuggestionResponse)
async def create_suggestion(
    data: schemas.SuggestionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Soumettre une suggestion (utilisateur connecté)."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    suggestion = models.Sugestion(
        libele=data.libele,
        description_suggest=data.description_suggest,
        note=data.note,
        id_user=user_email,
        visibility="pending",  # NEW: Set to pending for admin approval
    )
    
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    
    return suggestion


@router.get("/api/suggestions/user/{user_mailer}", response_model=List[schemas.SuggestionResponse])
async def get_user_suggestions(
    user_mailer: str,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """Récupère les suggestions d'un utilisateur."""
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.id_user == user_mailer
    ).order_by(models.Sugestion.id_suggest.desc()).all()
    
    return suggestions


@router.get("/api/suggestions", response_model=List[schemas.SuggestionResponse])
async def list_all_suggestions(
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: lister toutes les suggestions (approved + pending)."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Admin sees ALL suggestions (pending + approved + rejected)
    return db.query(models.Sugestion).order_by(
        models.Sugestion.id_suggest.desc()
    ).all()
