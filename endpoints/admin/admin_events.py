"""
Gestion des événements (Admin) — BetaLab
Endpoints:
  GET    /api/admin/events                    → lister événements
  POST   /api/admin/events                    → créer événement
  GET    /api/admin/events/{event_id}         → détails événement
  PUT    /api/admin/events/{event_id}/update  → modifier événement
  DELETE /api/admin/events/{event_id}         → supprimer événement
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

import models
from database import get_db

router = APIRouter(prefix="/api/admin", tags=["Admin - Événements"])


def _verify_admin(request: Request, db: Session):
    """Vérifie que l'utilisateur est admin."""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    # Vérifier la session en BD
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.expires_at > datetime.utcnow()
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    # Vérifier que c'est une session admin
    if not session.user_mailer.startswith("admin_"):
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    # Vérifier le session_type si disponible
    if hasattr(session, 'session_type') and session.session_type != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    
    return token


@router.get("/events")
async def list_events(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Liste tous les événements."""
    _verify_admin(request, db)
    
    events = db.query(models.Event).order_by(
        models.Event.event_date.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(models.Event).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "event_date": str(e.event_date) if e.event_date else None,
                "location": e.location,
                "event_type": e.event_type,
            }
            for e in events
        ]
    }


import schemas

@router.post("/events")
async def create_event(
    request: Request,
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
):
    """Crée un nouvel événement."""
    _verify_admin(request, db)
    
    event = models.Event(
        title=event_data.title,
        description=event_data.description,
        event_date=event_data.event_date,
        location=event_data.location,
        event_type=event_data.event_type,
        created_by="admin",
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return {
        "message": "Événement créé avec succès",
        "event": {
            "id": event.id,
            "title": event.title,
            "event_date": str(event.event_date) if event.event_date else None,
        }
    }


@router.get("/events/{event_id}")
async def get_event_details(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les détails d'un événement."""
    _verify_admin(request, db)
    
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "event_date": str(event.event_date) if event.event_date else None,
        "location": event.location,
        "event_type": event.event_type,
        "created_by": event.created_by,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.put("/events/{event_id}/update")
async def update_event(
    event_id: int,
    request: Request,
    event_data: schemas.EventCreate, # On peut réutiliser EventCreate ou créer un EventUpdate
    db: Session = Depends(get_db),
):
    """Modifie un événement."""
    _verify_admin(request, db)
    
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    if event_data.title:
        event.title = event_data.title
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.event_date:
        event.event_date = event_data.event_date
    if event_data.location is not None:
        event.location = event_data.location
    if event_data.event_type:
        event.event_type = event_data.event_type
    
    db.commit()
    db.refresh(event)
    
    return {"message": "Événement mis à jour", "event": {"id": event.id, "title": event.title}}


@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Supprime un événement."""
    _verify_admin(request, db)
    
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    event_title = event.title
    db.delete(event)
    db.commit()
    
    return {"message": f"Événement '{event_title}' supprimé"}
