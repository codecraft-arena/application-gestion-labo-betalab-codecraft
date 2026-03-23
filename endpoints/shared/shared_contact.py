"""
Contact et adhésion (Partagé) — BetaLab
Endpoints:
  POST   /api/contact                     → soumettre formulaire contact
  GET    /api/contact                     → admin: lister demandes
  PUT    /api/contact/{id}/read           → admin: marquer comme lu
  POST   /api/contact/{id}/invite         → admin: envoyer invitation
  GET    /api/adhesion/{token}            → vérifier token
  POST   /api/adhesion/{token}            → soumettre formulaire adhésion
"""

import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import EmailStr

import models, schemas
from database import get_db
from dependencies import get_password_hash
from email_service import (
    send_contact_acknowledgment,
    send_invitation_email,
    send_credentials_email,
)

router = APIRouter(tags=["Contact & Adhésion"])

_JOIN_KEYWORDS = {"rejoindre", "adhésion", "adherer", "adhérer", "membre", "intégrer", "integrer", "candidature"}


@router.post("/api/contact", response_model=schemas.ContactRequestResponse)
async def submit_contact(
    data: schemas.ContactRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Soumet une demande de contact (public)."""
    subject_lower = (data.subject or "").lower()
    message_lower = (data.message or "").lower()
    is_join = any(kw in subject_lower or kw in message_lower for kw in _JOIN_KEYWORDS)

    contact = models.ContactRequest(
        name=data.name,
        email=str(data.email),
        subject=data.subject,
        message=data.message,
        is_join_request=is_join,
        status="nouveau",
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    background_tasks.add_task(
        send_contact_acknowledgment, str(data.email), data.name
    )

    return contact


@router.get("/api/contact", response_model=List[schemas.ContactRequestResponse])
async def list_contacts(
    request: Request,
    join_only: bool = False,
    db: Session = Depends(get_db),
):
    """Admin: récupère les demandes de contact."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    q = db.query(models.ContactRequest)
    if join_only:
        q = q.filter(models.ContactRequest.is_join_request == True)
    return q.order_by(models.ContactRequest.created_at.desc()).all()


@router.put("/api/contact/{contact_id}/read")
async def mark_contact_read(
    contact_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: marque une demande comme lue."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    c = db.query(models.ContactRequest).filter(models.ContactRequest.id == contact_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    c.status = "lu"
    db.commit()
    return {"message": "Demande marquée comme lue"}


@router.delete("/api/contact/{contact_id}")
async def delete_contact(
    contact_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: supprime une demande de contact."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    c = db.query(models.ContactRequest).filter(models.ContactRequest.id == contact_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    db.delete(c)
    db.commit()
    return {"message": "Demande supprimée"}


@router.post("/api/contact/{contact_id}/invite")
async def send_adhesion_invitation(
    contact_id: int,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: envoie une invitation d'adhésion."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    contact = db.query(models.ContactRequest).filter(
        models.ContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Supprimer les anciens tokens
    db.query(models.InvitationToken).filter(
        models.InvitationToken.contact_id == contact_id,
        models.InvitationToken.used == False,
    ).delete()

    token_value = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(hours=72)

    inv = models.InvitationToken(
        token=token_value,
        email=contact.email,
        name=contact.name,
        used=False,
        expires_at=expires,
        contact_id=contact.id,
    )
    db.add(inv)

    contact.status = "invité"
    db.commit()
    db.refresh(inv)

    background_tasks.add_task(
        send_invitation_email, contact.email, contact.name, token_value
    )

    return {
        "message": f"Invitation envoyée à {contact.email}",
        "token": token_value,
        "expires_at": expires.isoformat(),
    }


@router.get("/api/adhesion/{token}")
async def verify_token(token: str, db: Session = Depends(get_db)):
    """Vérifie la validité du token d'invitation."""
    inv = db.query(models.InvitationToken).filter(
        models.InvitationToken.token == token
    ).first()
    
    if not inv:
        raise HTTPException(status_code=404, detail="Lien invalide")
    if inv.used:
        raise HTTPException(status_code=400, detail="Lien déjà utilisé")
    if datetime.utcnow() > inv.expires_at:
        raise HTTPException(status_code=400, detail="Lien expiré")
    
    return {
        "valid": True,
        "mailer": inv.email,
        "name": inv.name,
    }


@router.post("/api/adhesion/{token}", response_model=schemas.AdhesionResponse)
async def submit_adhesion(
    token: str,
    data: schemas.AdhesionForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Soumet le formulaire d'adhésion."""
    inv = db.query(models.InvitationToken).filter(
        models.InvitationToken.token == token
    ).first()
    
    if not inv:
        raise HTTPException(status_code=404, detail="Lien invalide")
    if inv.used:
        raise HTTPException(status_code=400, detail="Lien déjà utilisé")
    if datetime.utcnow() > inv.expires_at:
        raise HTTPException(status_code=400, detail="Lien expiré")
    
    # Vérifier que l'email n'existe pas
    if db.query(models.User).filter(models.User.email == inv.email).first():
        raise HTTPException(status_code=400, detail="Compte existe déjà")

    try:
        birthdate_obj = datetime.strptime(data.birthdate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide")

    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court")

    user = models.User(
        mailer=inv.email,
        name=data.name,
        birthdate=birthdate_obj,
        occupation=data.occupation,
        institution=data.institution,
        level=data.level or "",
        domain=data.domain or "",
        motivation=data.motivation or "",
        password=get_password_hash(data.password),
        validated=False,
        suspended=False,
        role="membre",
    )
    db.add(user)

    inv.used = True

    if inv.contact_id:
        contact = db.query(models.ContactRequest).filter(
            models.ContactRequest.id == inv.contact_id
        ).first()
        if contact:
            contact.status = "traité"

    db.commit()
    db.refresh(user)

    background_tasks.add_task(
        send_credentials_email, inv.email, data.name, data.password
    )

    return schemas.AdhesionResponse(
        mailer=user.email,
        name=user.name,
        message="Compte créé! Validation par admin requise.",
    )
