"""
Routeur activités — BetaLab.

Endpoints :
  GET  /api/activities                         → liste
  POST /api/activities                         → créer (admin)
  PUT  /api/activities/{id}/validate           → approuver
  PUT  /api/activities/{id}/reject             → rejeter
  DELETE /api/activities/{id}                  → supprimer (admin)
  POST /api/activities/{id}/invite/{mailer}     → inviter un user (admin)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(tags=["Activités"])


@router.get("/api/activities", response_model=List[schemas.ActivityResponse])
async def list_activities(db: Session = Depends(get_db)):
    return db.query(models.Activity).all()


@router.post("/api/activities", response_model=schemas.ActivityResponse)
async def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    """L'admin crée une nouvelle activité / projet."""
    if db.query(models.Activity).filter(models.Activity.id_activity == data.id_activity).first():
        raise HTTPException(status_code=400, detail="Une activité avec cet ID existe déjà")
    activity = models.Activity(
        id_activity=data.id_activity,
        name_activity=data.name_activity,
        description=data.description,
        class_activity=data.class_activity,
        status=data.status or "en attente",
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.put("/api/activities/{activity_id}/validate")
async def validate_activity(activity_id: str, db: Session = Depends(get_db)):
    a = _get_or_404(db, activity_id)
    a.status = "approuvé"; db.commit()
    return {"message": f"Activité {a.name_activity} approuvée"}


@router.put("/api/activities/{activity_id}/reject")
async def reject_activity(activity_id: str, db: Session = Depends(get_db)):
    a = _get_or_404(db, activity_id)
    a.status = "rejeté"; db.commit()
    return {"message": f"Activité {a.name_activity} rejetée"}


@router.delete("/api/activities/{activity_id}")
async def delete_activity(activity_id: str, db: Session = Depends(get_db)):
    """Supprime une activité et toutes ses contributions (cascade)."""
    a = _get_or_404(db, activity_id)
    db.delete(a); db.commit()
    return {"message": f"Activité {activity_id} supprimée"}


@router.post("/api/activities/{activity_id}/invite/{user_mailer}")
async def invite_user(activity_id: str, user_mailer: str, db: Session = Depends(get_db)):
    """Invite un utilisateur à participer à une activité (status = pending)."""
    if not db.query(models.Activity).filter(models.Activity.id_activity == activity_id).first():
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    if not db.query(models.User).filter(models.User.mailer == user_mailer).first():
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if db.query(models.Contribute).filter(
        models.Contribute.id_user == user_mailer,
        models.Contribute.id_activity == activity_id,
    ).first():
        raise HTTPException(status_code=400, detail="Invitation déjà existante")

    db.add(models.Contribute(
        id_user=user_mailer,
        id_activity=activity_id,
        participation_status="pending",
    ))
    db.commit()
    return {"message": f"Invitation envoyée à {user_mailer} pour {activity_id}"}


def _get_or_404(db: Session, activity_id: str) -> models.Activity:
    a = db.query(models.Activity).filter(models.Activity.id_activity == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    return a
