"""
Routeur utilisateurs — toutes les fonctionnalités liées au profil et aux actions utilisateur.

Endpoints :
  POST   /submit                                  → inscription HTML
  GET    /api/users                               → liste utilisateurs
  POST   /api/users                               → créer utilisateur (JSON)
  GET    /api/users/pending                       → en attente de validation
  GET    /api/users/validated                     → validés
  GET    /api/me                                  → profil connecté
  PUT    /api/users/{mailer}/profile               → modifier son profil
  GET    /api/contributions/{mailer}               → contributions acceptées
  GET    /api/invitations/{mailer}                 → invitations en attente
  PUT    /api/invitations/{mailer}/{act_id}/accept → accepter une invitation
  PUT    /api/invitations/{mailer}/{act_id}/refuse → refuser une invitation
  POST   /api/questions                           → poser une question
  GET    /api/questions/user/{mailer}              → questions d'un utilisateur
  POST   /api/suggestions                         → apporter une suggestion
  GET    /api/suggestions/user/{mailer}            → suggestions d'un utilisateur
  GET    /api/users/{mailer}                       → récupérer un utilisateur
  PUT    /api/users/{mailer}/validate              → valider (admin)
  PUT    /api/users/{mailer}/reject                → rejeter (admin)
  PUT    /api/users/{mailer}/suspend               → suspendre (admin)
  PUT    /api/users/{mailer}/unsuspend             → réactiver (admin)
  DELETE /api/users/{mailer}                       → supprimer (admin)
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from dependencies import get_password_hash, sessions

router = APIRouter(tags=["Utilisateurs"])


# ─────────────────────────────────────────────────────────────────────────────
# INSCRIPTION HTML
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/submit")
async def soumettre_formulaire(
    mailer:       EmailStr = Form(...),
    name:        str      = Form(...),
    birthdate:   str      = Form(...),
    password:    str      = Form(...),
    occupation:  str      = Form(...),
    institution: str      = Form(...),
    level:       str      = Form(default=""),
    domain:      str      = Form(default=""),
    motivation:  str      = Form(default=""),
    db: Session = Depends(get_db),
):
    try:
        birthdate_obj = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (8 caractères min)")
    if len(password) > 255:
        raise HTTPException(status_code=400, detail="Mot de passe trop long (255 caractères max)")
    if db.query(models.User).filter(models.User.mailer == mailer).first():
        raise HTTPException(status_code=400, detail="Cet mailer est déjà utilisé")

    user = models.User(
        name=name, mailer=mailer, birthdate=birthdate_obj,
        password=get_password_hash(password), occupation=occupation,
        institution=institution, level=level, domain=domain, motivation=motivation,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription")

    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────────────────────────────────────
# LISTE & CRÉATION (admin / API)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/users", response_model=List[schemas.UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


@router.post("/api/users", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new = models.User(**user.dict())
    db.add(new); db.commit(); db.refresh(new)
    return new


# ⚠️  Routes spécifiques AVANT /api/users/{mailer}
@router.get("/api/users/pending", response_model=List[schemas.UserResponse])
async def list_pending(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.validated == False).all()


@router.get("/api/users/validated", response_model=List[schemas.UserResponse])
async def list_validated(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.validated == True).all()


# ─────────────────────────────────────────────────────────────────────────────
# PROFIL CONNECTÉ
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/me", response_model=schemas.UserResponse)
async def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    user = db.query(models.User).filter(models.User.mailer == sessions[token]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


# ─────────────────────────────────────────────────────────────────────────────
# MODIFIER SON PROFIL
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/api/users/{user_mailer}/profile", response_model=schemas.UserResponse)
async def update_profile(
    user_mailer: str,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
):
    """Permet à l'utilisateur de mettre à jour ses informations personnelles."""
    user = _get_or_404(db, user_mailer)
    for field, value in data.dict(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────────────────────────────────────
# CONTRIBUTIONS (participations acceptées)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/contributions/{user_mailer}")
async def get_contributions(user_mailer: EmailStr, db: Session = Depends(get_db)):
    """Retourne les contributions dont la participation est acceptée."""
    rows = (
        db.query(models.Contribute)
        .join(models.Activity)
        .filter(
            models.Contribute.id_user == user_mailer,
            models.Contribute.participation_status == "accepted",
        )
        .all()
    )
    return [
        {
            "id_activity":    c.activity.id_activity,
            "name_activity":  c.activity.name_activity,
            "description":    c.activity.description,
            "status":         c.activity.status,
            "class_activity": c.activity.class_activity,
            "period":         str(c.period) if c.period else None,
        }
        for c in rows
    ]


# ─────────────────────────────────────────────────────────────────────────────
# INVITATIONS (contributions en statut pending)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/invitations/{user_mailer}")
async def get_invitations(user_mailer: str, db: Session = Depends(get_db)):
    """Retourne les invitations en attente de réponse pour un utilisateur."""
    rows = (
        db.query(models.Contribute)
        .join(models.Activity)
        .filter(
            models.Contribute.id_user == user_mailer,
            models.Contribute.participation_status == "pending",
        )
        .all()
    )
    return [
        {
            "id_activity":          c.activity.id_activity,
            "name_activity":        c.activity.name_activity,
            "description":          c.activity.description,
            "class_activity":       c.activity.class_activity,
            "participation_status": c.participation_status,
            "period":               str(c.period) if c.period else None,
        }
        for c in rows
    ]


@router.put("/api/invitations/{user_mailer}/{activity_id}/accept")
async def accept_invitation(
    user_mailer: str, activity_id: str, db: Session = Depends(get_db)
):
    """L'utilisateur accepte une invitation à participer à une activité."""
    contrib = _get_contribute_or_404(db, user_mailer, activity_id)
    contrib.participation_status = "accepted"
    db.commit()
    return {"message": f"Invitation à « {activity_id} » acceptée"}


@router.put("/api/invitations/{user_mailer}/{activity_id}/refuse")
async def refuse_invitation(
    user_mailer: str, activity_id: str, db: Session = Depends(get_db)
):
    """L'utilisateur refuse une invitation."""
    contrib = _get_contribute_or_404(db, user_mailer, activity_id)
    contrib.participation_status = "refused"
    db.commit()
    return {"message": f"Invitation à « {activity_id} » refusée"}


# ─────────────────────────────────────────────────────────────────────────────
# QUESTIONS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/api/questions", response_model=schemas.QuestionResponse)
async def create_question(
    data: schemas.QuestionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Poser une nouvelle question."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")

    question = models.Question(
        libele_question=data.libele_question,
        description_question=data.description_question,
        id_user=sessions[token],
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


# ⚠️  Route spécifique AVANT /api/questions/{id}
@router.get("/api/questions/user/{user_mailer}", response_model=List[schemas.QuestionResponse])
async def get_user_questions(user_mailer: str, db: Session = Depends(get_db)):
    """Retourne toutes les questions posées par un utilisateur."""
    return (
        db.query(models.Question)
        .filter(models.Question.id_user == user_mailer)
        .order_by(models.Question.id_question.desc())
        .all()
    )


@router.get("/api/questions", response_model=List[schemas.QuestionResponse])
async def get_all_questions(db: Session = Depends(get_db)):
    """Retourne toutes les questions (usage admin)."""
    return db.query(models.Question).order_by(models.Question.id_question.desc()).all()


# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTIONS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/api/suggestions", response_model=schemas.SuggestionResponse)
async def create_suggestion(
    data: schemas.SuggestionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Apporter une suggestion."""
    token = request.cookies.get("session_token")
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")

    suggestion = models.Sugestion(
        libele=data.libele,
        description_suggest=data.description_suggest,
        note=data.note,
        id_user=sessions[token],
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


# ⚠️  Route spécifique AVANT /api/suggestions/{id}
@router.get("/api/suggestions/user/{user_mailer}", response_model=List[schemas.SuggestionResponse])
async def get_user_suggestions(user_mailer: str, db: Session = Depends(get_db)):
    """Retourne toutes les suggestions d'un utilisateur."""
    return (
        db.query(models.Sugestion)
        .filter(models.Sugestion.id_user == user_mailer)
        .order_by(models.Sugestion.id_suggest.desc())
        .all()
    )


@router.get("/api/suggestions", response_model=List[schemas.SuggestionResponse])
async def get_all_suggestions(db: Session = Depends(get_db)):
    """Retourne toutes les suggestions (usage admin)."""
    return db.query(models.Sugestion).order_by(models.Sugestion.id_suggest.desc()).all()


# ─────────────────────────────────────────────────────────────────────────────
# CRUD ADMIN sur utilisateurs
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/users/{user_mailer}", response_model=schemas.UserResponse)
async def get_user(user_mailer: str, db: Session = Depends(get_db)):
    return _get_or_404(db, user_mailer)


@router.put("/api/users/{user_mailer}/validate")
async def validate_user(user_mailer: str, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_mailer)
    user.validated = True
    db.commit()
    return {"message": f"Utilisateur {user.name} validé"}


@router.put("/api/users/{user_mailer}/reject")
async def reject_user(user_mailer: str, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_mailer)
    db.delete(user); db.commit()
    return {"message": f"Utilisateur {user_mailer} rejeté et supprimé"}


@router.put("/api/users/{user_mailer}/suspend")
async def suspend_user(user_mailer: str, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_mailer)
    user.suspended = True; db.commit()
    return {"message": f"Utilisateur {user.name} suspendu"}


@router.put("/api/users/{user_mailer}/unsuspend")
async def unsuspend_user(user_mailer: str, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_mailer)
    user.suspended = False; db.commit()
    return {"message": f"Utilisateur {user.name} réactivé"}


@router.delete("/api/users/{user_mailer}")
async def delete_user(user_mailer: str, db: Session = Depends(get_db)):
    user = _get_or_404(db, user_mailer)
    db.delete(user); db.commit()
    return {"message": f"Utilisateur {user_mailer} supprimé"}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS PRIVÉS
# ─────────────────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, mailer: str) -> models.User:
    user = db.query(models.User).filter(models.User.mailer == mailer).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


def _get_contribute_or_404(db: Session, user_mailer: str, activity_id: str) -> models.Contribute:
    contrib = (
        db.query(models.Contribute)
        .filter(
            models.Contribute.id_user == user_mailer,
            models.Contribute.id_activity == activity_id,
        )
        .first()
    )
    if not contrib:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    return contrib
