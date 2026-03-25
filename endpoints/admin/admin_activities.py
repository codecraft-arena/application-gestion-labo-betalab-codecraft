"""
Gestion des activités (Admin) — BetaLab
Endpoints:
  GET    /api/admin/activities                          → lister activités
  POST   /api/admin/activities                          → créer activité
  GET    /api/admin/activities/{activity_id}           → détails activité
  PUT    /api/admin/activities/{activity_id}/update     → modifier activité
  PUT    /api/admin/activities/{activity_id}/validate   → valider activité
  PUT    /api/admin/activities/{activity_id}/reject     → rejeter activité
  DELETE /api/admin/activities/{activity_id}           → supprimer activité
  POST   /api/admin/activities/{activity_id}/invite/{mailer}  → inviter utilisateur
  GET    /api/admin/activities/{activity_id}/contributions → voir contributions
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

import models, schemas
from database import get_db
from session_manager import SessionManager
from admin_auth import AdminAuthManager

router = APIRouter(prefix="/api/admin", tags=["Admin - Activités"])


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


@router.get("/activities")
async def list_activities(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Liste toutes les activités."""
    token = _verify_admin(request, db)
    
    # NEW: Filter out pending_submission activities (only show approved/implemented)
    activities = db.query(models.Activity).filter(
        models.Activity.user_approval_status != "pending_submission"
    ).offset(skip).limit(limit).all()
    total = db.query(models.Activity).filter(
        models.Activity.user_approval_status != "pending_submission"
    ).count()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "activities": [
            {
                "id_activity": a.id_activity,
                "name_activity": a.name_activity,
                "description": a.description,
                "status": a.status,
                "class_activity": a.class_activity,
                "created_by": a.created_by,
                "user_approval_status": a.user_approval_status,
            }
            for a in activities
        ]
    }


@router.post("/activities")
async def create_activity(
    request: Request,
    activity_data: schemas.ActivityCreate,
    db: Session = Depends(get_db),
):
    """Crée une nouvelle activité."""
    token = _verify_admin(request, db)
    
    # Extraire le username admin depuis le token de session
    session = SessionManager.get_session(db, token)
    admin_username = session.user_mailer.replace("admin_", "")
    admin = AdminAuthManager.get_admin_by_username(db, admin_username)
    admin_email = admin.email if admin else admin_username
    
    # Vérifier qu'elle n'existe pas
    if db.query(models.Activity).filter(models.Activity.id_activity == activity_data.id_activity).first():
        raise HTTPException(status_code=400, detail="Une activité avec cet ID existe déjà")
    
    activity = models.Activity(
        id_activity=activity_data.id_activity,
        name_activity=activity_data.name_activity,
        description=activity_data.description,
        class_activity=activity_data.class_activity,
        status=activity_data.status,
        created_by=admin_email,  # NEW: Track who created this activity
        user_approval_status="approved",  # NEW: Admin-created activities are auto-approved
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return {
        "message": "Activité créée avec succès",
        "activity": {
            "id_activity": activity.id_activity,
            "name_activity": activity.name_activity,
            "status": activity.status,
            "created_by": activity.created_by,
            "user_approval_status": activity.user_approval_status,
        }
    }


@router.get("/activities/{activity_id}")
async def get_activity_details(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les détails d'une activité."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Compter contributions
    contributions = db.query(models.Contribute).filter(
        models.Contribute.id_activity == activity_id
    ).count()
    
    return {
        "id_activity": activity.id_activity,
        "name_activity": activity.name_activity,
        "description": activity.description,
        "status": activity.status,
        "class_activity": activity.class_activity,
        "contributions_count": contributions,
    }


@router.put("/activities/{activity_id}/update")
async def update_activity(
    activity_id: str,
    request: Request,
    name_activity: Optional[str] = None,
    description: Optional[str] = None,
    class_activity: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Modifie une activité."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    if name_activity is not None:
        activity.name_activity = name_activity
    if description is not None:
        activity.description = description
    if class_activity is not None:
        activity.class_activity = class_activity
    
    db.commit()
    db.refresh(activity)
    
    return {"message": "Activité mise à jour", "activity": {"id_activity": activity.id_activity}}


@router.put("/activities/{activity_id}/validate")
async def validate_activity(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Valide une activité."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    activity.status = "approuvé"
    db.commit()
    
    return {"message": f"Activité '{activity.name_activity}' validée"}


@router.put("/activities/{activity_id}/reject")
async def reject_activity(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Rejette une activité."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    activity.status = "rejeté"
    db.commit()
    
    return {"message": f"Activité '{activity.name_activity}' rejetée"}


@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Supprime une activité et toutes ses contributions."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    db.delete(activity)  # Cascade delete
    db.commit()
    
    return {"message": f"Activité '{activity_id}' supprimée"}


@router.post("/activities/{activity_id}/invite/{user_mailer}")
async def invite_user_to_activity(
    activity_id: str,
    user_mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Invite un utilisateur à participer à une activité."""
    _verify_admin(request, db)
    
    # Vérifier que l'activité existe
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Vérifier que l'utilisateur existe
    user = db.query(models.User).filter(
        models.User.email == user_mailer
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier qu'il n'invite pas déjà
    existing = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_mailer,
        models.Contribute.id_activity == activity_id,
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Cet utilisateur a déjà une participation pour cette activité")
    
    # Créer contribution en attente
    contrib = models.Contribute(
        id_user=user_mailer,
        id_activity=activity_id,
        participation_status="pending",
    )
    
    db.add(contrib)
    db.commit()
    
    return {
        "message": f"Invitation envoyée à {user.name} pour participer à '{activity.name_activity}'",
        "user": user.name,
        "activity": activity.name_activity,
        "status": "pending",
    }


@router.get("/activities/{activity_id}/contributions")
async def get_activity_contributions(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère toutes les contributions pour une activité."""
    _verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    contributions = db.query(models.Contribute).join(
        models.User
    ).filter(
        models.Contribute.id_activity == activity_id
    ).all()
    
    return {
        "activity_id": activity_id,
        "activity_name": activity.name_activity,
        "contributions_count": len(contributions),
        "contributions": [
            {
                "user_name": c.user.name,
                "user_mailer": c.user.email,
                "status": c.participation_status,
                "period": str(c.period) if c.period else None,
            }
            for c in contributions
        ]
    }


@router.put("/activities/{activity_id}/contributions/{user_mailer}/approve")
async def approve_contribution(
    activity_id: str,
    user_mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Approuve une proposition de contribution."""
    _verify_admin(request, db)
    
    contrib = db.query(models.Contribute).filter(
        models.Contribute.id_activity == activity_id,
        models.Contribute.id_user == user_mailer,
    ).first()
    
    if not contrib:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    contrib.participation_status = "accepted"
    db.commit()
    
    return {"message": "Contribution approuvée"}


@router.put("/activities/{activity_id}/contributions/{user_mailer}/reject")
async def reject_contribution(
    activity_id: str,
    user_mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Rejette une proposition de contribution."""
    _verify_admin(request, db)
    
    contrib = db.query(models.Contribute).filter(
        models.Contribute.id_activity == activity_id,
        models.Contribute.id_user == user_mailer,
    ).first()
    
    if not contrib:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    contrib.participation_status = "refused"
    db.commit()
    
    return {"message": "Contribution rejetée"}
