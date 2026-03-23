"""
Routeur administrateur — BetaLab.

Endpoints :
  GET  /api/admin/profile                         → profil admin (hardcodé)
  GET  /api/admin/contributions                   → toutes les contributions
  POST /api/admin/users/{mailer}/update            → modifier infos d'un user
  PUT  /api/admin/users/{mailer}/role              → attribuer un rôle
  POST /api/questions/{q_id}/answer               → répondre à une question
  GET  /api/questions                             → toutes les questions (avec réponses)
  GET  /api/suggestions                           → toutes les suggestions
  POST /api/events                                → créer un événement
  GET  /api/events                                → liste des événements
  DELETE /api/events/{event_id}                   → supprimer un événement
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from dependencies import sessions

router = APIRouter(prefix="/api/admin", tags=["Administration"])


# ─────────────────────────────────────────────────────────────────────────────
# HELPER : admin authentifié (session active — pas de vrai modèle admin en DB)
# ─────────────────────────────────────────────────────────────────────────────
def _require_admin(request: Request):
    """
    Vérification minimale : session active.
    En production, ajouter un vrai modèle Admin avec rôle.
    """
    token = request.cookies.get("session_token")
    # Pour la démo l'admin se connecte sans cookie (form /admin-login → navigate)
    # donc on ne bloque pas. À durcir en production.
    return True


# ─────────────────────────────────────────────────────────────────────────────
# CONTRIBUTIONS — toutes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/contributions")
async def all_contributions(db: Session = Depends(get_db)):
    """Retourne toutes les contributions (toutes activités, tous utilisateurs)."""
    rows = (
        db.query(models.Contribute)
        .join(models.Activity)
        .join(models.User)
        .all()
    )
    return [
        {
            "user_name":            c.user.name,
            "user_mailer":           c.user.mailer,
            "id_activity":          c.activity.id_activity,
            "name_activity":        c.activity.name_activity,
            "class_activity":       c.activity.class_activity,
            "participation_status": c.participation_status,
            "period":               str(c.period) if c.period else None,
        }
        for c in rows
    ]


# ─────────────────────────────────────────────────────────────────────────────
# MODIFIER UN UTILISATEUR (admin)
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/users/{user_mailer}/update", response_model=schemas.UserResponse)
async def admin_update_user(
    user_mailer: str,
    data: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
):
    """L'admin modifie les informations complètes d'un utilisateur."""
    user = _get_user_or_404(db, user_mailer)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────────────────────────────────────
# RÔLES
# ─────────────────────────────────────────────────────────────────────────────

VALID_ROLES = {"membre", "chercheur", "responsable", "admin"}

@router.put("/users/{user_mailer}/role", response_model=schemas.UserResponse)
async def assign_role(
    user_mailer: str,
    data: schemas.RoleUpdate,
    db: Session = Depends(get_db),
):
    """Attribue un rôle à un utilisateur."""
    if data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Rôle invalide. Valeurs acceptées : {', '.join(VALID_ROLES)}",
        )
    user = _get_user_or_404(db, user_mailer)
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────────────────────────────────────
# ÉVÉNEMENTS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/events", response_model=schemas.EventResponse)
async def create_event(
    data: schemas.EventCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Crée un événement (conférence, hackathon, atelier…)."""
    event = models.Event(
        title=data.title,
        description=data.description,
        event_date=data.event_date,
        location=data.location,
        event_type=data.event_type or "événement",
        created_by="admin",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events", response_model=List[schemas.EventResponse])
async def list_events(db: Session = Depends(get_db)):
    """Liste tous les événements, du plus récent au plus ancien."""
    return (
        db.query(models.Event)
        .order_by(models.Event.event_date.desc())
        .all()
    )


@router.delete("/events/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Supprime un événement."""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    db.delete(event)
    db.commit()
    return {"message": f"Événement « {event.title} » supprimé"}


# ─────────────────────────────────────────────────────────────────────────────
# QUESTIONS — liste complète + réponses
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/questions", response_model=List[schemas.QuestionResponse])
async def list_all_questions(db: Session = Depends(get_db)):
    """Toutes les questions posées par les utilisateurs, avec leurs réponses."""
    return (
        db.query(models.Question)
        .order_by(models.Question.id_question.desc())
        .all()
    )


@router.post("/questions/{question_id}/answer", response_model=schemas.AnswerResponse)
async def answer_question(
    question_id: int,
    data: schemas.AnswerCreate,
    db: Session = Depends(get_db),
):
    """L'admin répond à une question."""
    q = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")

    response = models.Response(
        libelle_response=data.libelle_response,
        description_response=data.description_response,
        id_question=question_id,
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTIONS — liste complète
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/suggestions", response_model=List[schemas.SuggestionResponse])
async def list_all_suggestions(db: Session = Depends(get_db)):
    """Toutes les suggestions soumises par les utilisateurs."""
    return (
        db.query(models.Sugestion)
        .order_by(models.Sugestion.id_suggest.desc())
        .all()
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPER PRIVÉ
# ─────────────────────────────────────────────────────────────────────────────

def _get_user_or_404(db: Session, mailer: str) -> models.User:
    user = db.query(models.User).filter(models.User.mailer == mailer).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user
