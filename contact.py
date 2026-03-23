"""
Routeur contact & adhésion — BetaLab v2.0

Avec sécurité:
  - Rate limiting (3 demandes/heure)
  - CSRF protection optional
  - Validation stricte des emails

Flux complet :
  1. POST /api/contact          → utilisateur soumet le formulaire de contact
                                   → accusé de réception par email
                                   → si sujet contient "rejoindre/adhésion/membre" → is_join_request=True
  2. POST /api/contact/{id}/invite → admin envoie l'invitation (token 72h)
                                      → email avec lien /adhesion/{token}
  3. GET  /api/adhesion/{token} → valide le token et retourne nom+email pré-remplis
  4. POST /api/adhesion/{token} → utilisateur soumet le formulaire d'adhésion
                                   → compte créé en DB + email identifiants
  5. GET  /api/contact          → admin liste toutes les demandes
"""

import secrets
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from dependencies import get_password_hash
from email_service import (
    send_contact_acknowledgment,
    send_invitation_email,
    send_credentials_email,
)
from security import limiter_contact, check_rate_limit, CSRFManager

router = APIRouter(tags=["Contact & Adhésion"])

# Mots-clés déclenchant is_join_request
_JOIN_KEYWORDS = {"rejoindre", "adhésion", "adherer", "adhérer", "membre", "intégrer", "integrer", "candidature"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Formulaire de contact (public) - Avec rate limiting
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/api/contact", response_model=schemas.ContactRequestResponse)
async def submit_contact(
    request: Request,
    data: schemas.ContactRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Soumet une demande de contact.
    ⚠️ Rate limited: 3 demandes par heure.
    Détecte automatiquement si c'est une demande d'adhésion selon l'objet.
    Envoie un accusé de réception par email (tâche de fond).
    """
    
    # Rate limiting (3 par heure)
    check_rate_limit(limiter_contact, request)
    
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

    # Accusé de réception en arrière-plan
    background_tasks.add_task(
        send_contact_acknowledgment, str(data.email), data.name
    )

    return contact


# ─────────────────────────────────────────────────────────────────────────────
# 2. Admin : liste des demandes de contact
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/contact", response_model=List[schemas.ContactRequestResponse])
async def list_contacts(
    join_only: bool = False,
    db: Session = Depends(get_db),
):
    """Retourne toutes les demandes de contact (filtrable aux demandes d'adhésion)."""
    q = db.query(models.ContactRequest)
    if join_only:
        q = q.filter(models.ContactRequest.is_join_request == True)
    return q.order_by(models.ContactRequest.created_at.desc()).all()


@router.put("/api/contact/{contact_id}/read")
async def mark_contact_read(contact_id: int, db: Session = Depends(get_db)):
    """Marque une demande comme lue."""
    c = _get_contact_or_404(db, contact_id)
    c.status = "lu"
    db.commit()
    return {"message": "Demande marquée comme lue"}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Admin : envoyer une invitation d'adhésion
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/api/contact/{contact_id}/invite")
async def send_adhesion_invitation(
    contact_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    L'admin envoie une invitation par mailer à l'auteur de la demande.
    Génère un token unique (72 h) et met à jour le statut.
    """
    contact = _get_contact_or_404(db, contact_id)

    # Supprimer les anciens tokens non-utilisés pour ce contact
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

    # Envoi mailer en arrière-plan
    background_tasks.add_task(
        send_invitation_email, contact.email, contact.name, token_value
    )

    return {
        "message": f"Invitation envoyée à {contact.email}",
        "token": token_value,
        "expires_at": expires.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Vérifier le token (frontend pré-remplit le formulaire)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/api/adhesion/{token}")
async def verify_token(token: str, db: Session = Depends(get_db)):
    """
    Vérifie la validité du token et retourne les infos pré-remplies
    (nom, mailer) pour le formulaire d'adhésion.
    """
    inv = _get_valid_token(db, token)
    return {
        "valid": True,
        "mailer": inv.email,
        "name":  inv.name,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Soumettre le formulaire d'adhésion
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/api/adhesion/{token}", response_model=schemas.AdhesionResponse)
async def submit_adhesion(
    token: str,
    data: schemas.AdhesionForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Traite le formulaire d'adhésion :
      1. Valide le token
      2. Crée le compte utilisateur en DB
      3. Invalide le token
      4. Met à jour le statut de la demande de contact
      5. Envoie les identifiants par mailer
    """
    inv = _get_valid_token(db, token)

    # Vérifier que l'mailer n'existe pas déjà
    if db.query(models.User).filter(models.User.mailer == inv.email).first():
        raise HTTPException(
            status_code=400,
            detail="Un compte avec cet mailer existe déjà. Connectez-vous directement."
        )

    # Validation de la date
    try:
        birthdate_obj = datetime.strptime(data.birthdate, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")

    # Validation mot de passe
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (8 caractères min)")

    # Création du compte
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
        validated=False,  # doit être validé par l'admin
        suspended=False,
        role="membre",
    )
    db.add(user)

    # Invalider le token
    inv.used = True

    # Mettre à jour la demande de contact si liée
    if inv.contact_id:
        contact = db.query(models.ContactRequest).filter(
            models.ContactRequest.id == inv.contact_id
        ).first()
        if contact:
            contact.status = "traité"

    db.commit()
    db.refresh(user)

    # Envoyer les identifiants par mailer (arrière-plan)
    background_tasks.add_task(
        send_credentials_email, inv.email, data.name, data.password
    )

    return schemas.AdhesionResponse(
        mailer=user.mailer,
        name=user.name,
        message=(
            "Votre compte a été créé avec succès ! "
            "Vos identifiants vous ont été envoyés par mailer. "
            "Votre accès sera activé après validation par un administrateur."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS PRIVÉS
# ─────────────────────────────────────────────────────────────────────────────

def _get_contact_or_404(db: Session, contact_id: int) -> models.ContactRequest:
    c = db.query(models.ContactRequest).filter(models.ContactRequest.id == contact_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Demande de contact non trouvée")
    return c


def _get_valid_token(db: Session, token: str) -> models.InvitationToken:
    inv = db.query(models.InvitationToken).filter(
        models.InvitationToken.token == token
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Lien d'invitation invalide ou inexistant")
    if inv.used:
        raise HTTPException(status_code=400, detail="Ce lien d'invitation a déjà été utilisé")
    if datetime.utcnow() > inv.expires_at:
        raise HTTPException(status_code=400, detail="Ce lien d'invitation a expiré (72h)")
    return inv
