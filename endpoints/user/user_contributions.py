"""
Contributions et participations utilisateur — BetaLab
Endpoints:
  GET    /api/user/contributions                    → contributions acceptées
  GET    /api/user/invitations                      → invitations en attente
  PUT    /api/user/invitations/{activity_id}/accept → accepter invitation
  PUT    /api/user/invitations/{activity_id}/refuse → refuser invitation
  POST   /api/user/contributions                    → proposer contribution
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

import models
from database import get_db
from dependencies import sessions

router = APIRouter(prefix="/api/user", tags=["Utilisateur - Contributions"])


@router.get("/contributions")
async def get_user_contributions(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les contributions acceptées de l'utilisateur."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    contributions = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "accepted"
    ).all()
    
    return {
        "user_email": user_email,
        "contributions_count": len(contributions),
        "contributions": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "description": c.activity.description,
                "status": c.activity.status,
                "class_activity": c.activity.class_activity,
                "period": str(c.period) if c.period else None,
            }
            for c in contributions
        ]
    }


@router.get("/invitations")
async def get_user_invitations(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les invitations en attente de l'utilisateur."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    invitations = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "pending"
    ).all()
    
    return {
        "user_email": user_email,
        "pending_count": len(invitations),
        "invitations": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "description": c.activity.description,
                "class_activity": c.activity.class_activity,
                "status": c.activity.status,
            }
            for c in invitations
        ]
    }


@router.put("/invitations/{activity_id}/accept")
async def accept_invitation(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """L'utilisateur accepte une invitation à participer à une activité."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    # Vérifier que l'activité existe
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Récupérer la contribution
    contrib = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.id_activity == activity_id,
        models.Contribute.participation_status == "pending"
    ).first()
    
    if not contrib:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    
    # Accepter
    contrib.participation_status = "accepted"
    db.commit()
    
    return {
        "message": f"Vous avez accepté l'invitation pour '{activity.name_activity}'",
        "activity_id": activity_id,
        "activity_name": activity.name_activity,
        "participation_status": "accepted",
    }


@router.put("/invitations/{activity_id}/refuse")
async def refuse_invitation(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """L'utilisateur refuse une invitation à participer à une activité."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    # Vérifier que l'activité existe
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Récupérer la contribution
    contrib = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.id_activity == activity_id,
        models.Contribute.participation_status == "pending"
    ).first()
    
    if not contrib:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")
    
    # Refuser
    contrib.participation_status = "refused"
    db.commit()
    
    return {
        "message": f"Vous avez refusé l'invitation pour '{activity.name_activity}'",
        "activity_id": activity_id,
        "activity_name": activity.name_activity,
        "participation_status": "refused",
    }


@router.post("/contributions")
async def propose_contribution(
    activity_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    description: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """
    L'utilisateur propose une contribution à une activité.
    Crée une participation en attente d'approbation admin.
    """
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    # Vérifier que l'activité existe
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Vérifier qu'il n'y a pas déjà une contribution
    existing = db.query(models.Contribute).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.id_activity == activity_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Vous participez déjà à cette activité"
        )
    
    # Créer la contribution (en attente d'approbation)
    period = None
    if period_start:
        try:
            period = datetime.strptime(period_start, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")
    
    contrib = models.Contribute(
        id_user=user_email,
        id_activity=activity_id,
        period=period,
        participation_status="pending"
    )
    
    db.add(contrib)
    db.commit()
    db.refresh(contrib)
    
    return {
        "message": f"Proposition de contribution envoyée pour '{activity.name_activity}'",
        "activity_id": activity_id,
        "activity_name": activity.name_activity,
        "status": "pending",
        "description": "En attente d'approbation de l'administrateur",
    }


@router.get("/contributions/active")
async def get_active_contributions(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les activités auxquelles l'utilisateur participe actuellement."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    active_contributions = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email,
        models.Contribute.participation_status == "accepted",
        models.Activity.status != "rejeté"
    ).all()
    
    return {
        "user_email": user_email,
        "active_count": len(active_contributions),
        "activities": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "status": c.activity.status,
                "started_at": str(c.period) if c.period else None,
                "class_activity": c.activity.class_activity,
            }
            for c in active_contributions
        ]
    }


@router.get("/contributions/history")
async def get_contribution_history(
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère l'historique complet des contributions de l'utilisateur."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    all_contributions = db.query(models.Contribute).join(
        models.Activity
    ).filter(
        models.Contribute.id_user == user_email
    ).all()
    
    # Grouper par statut
    accepted = [c for c in all_contributions if c.participation_status == "accepted"]
    refused = [c for c in all_contributions if c.participation_status == "refused"]
    pending = [c for c in all_contributions if c.participation_status == "pending"]
    
    return {
        "user_email": user_email,
        "summary": {
            "accepted": len(accepted),
            "refused": len(refused),
            "pending": len(pending),
            "total": len(all_contributions),
        },
        "accepted_contributions": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
                "period": str(c.period) if c.period else None,
            }
            for c in accepted
        ],
        "refused_contributions": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
            }
            for c in refused
        ],
        "pending_contributions": [
            {
                "id_activity": c.activity.id_activity,
                "name_activity": c.activity.name_activity,
            }
            for c in pending
        ],
    }
