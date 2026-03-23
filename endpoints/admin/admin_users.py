"""
Gestion des utilisateurs (Admin) — BetaLab
Endpoints:
  GET    /api/admin/users                        → lister utilisateurs
  GET    /api/admin/users/{mailer}               → détails utilisateur
  PUT    /api/admin/users/{mailer}/update        → modifier utilisateur
  PUT    /api/admin/users/{mailer}/validate      → valider utilisateur
  PUT    /api/admin/users/{mailer}/reject        → rejeter utilisateur
  PUT    /api/admin/users/{mailer}/suspend       → suspendre utilisateur
  PUT    /api/admin/users/{mailer}/unsuspend     → réactiver utilisateur
  PUT    /api/admin/users/{mailer}/role          → assigner rôle
  DELETE /api/admin/users/{mailer}               → supprimer utilisateur
  GET    /api/admin/users/pending                → utilisateurs en attente
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

import models
from database import get_db
from session_manager import SessionManager
from admin_auth import AdminAuthManager

router = APIRouter(prefix="/api/admin", tags=["Admin - Utilisateurs"])


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


@router.get("/users")
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Liste tous les utilisateurs."""
    _verify_admin(request, db)
    
    users = db.query(models.User).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(models.User).count(),
        "skip": skip,
        "limit": limit,
        "users": [
            {
                "mailer": u.email,
                "name": u.name,
                "occupation": u.occupation,
                "institution": u.institution,
                "role": u.role,
                "validated": u.validated,
                "suspended": u.suspended,
            }
            for u in users
        ]
    }


@router.get("/users/pending")
async def list_pending_users(
    request: Request,
    db: Session = Depends(get_db),
):
    """Liste les utilisateurs en attente de validation."""
    _verify_admin(request, db)
    
    pending_users = db.query(models.User).filter(
        models.User.validated == False
    ).all()
    
    return {
        "count": len(pending_users),
        "users": [
            {
                "mailer": u.email,
                "name": u.name,
                "occupation": u.occupation,
                "institution": u.institution,
                "role": u.role,
            }
            for u in pending_users
        ]
    }


@router.get("/users/{mailer}")
async def get_user_details(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Récupère les détails d'un utilisateur."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Compter contributions
    contributions = db.query(models.Contribute).filter(
        models.Contribute.id_user == mailer
    ).count()
    
    # Voir questions
    questions = db.query(models.Question).filter(
        models.Question.id_user == mailer
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
        "contributions_count": contributions,
        "questions_count": questions,
    }


@router.put("/users/{mailer}/update")
async def update_user(
    mailer: str,
    request: Request,
    name: Optional[str] = None,
    occupation: Optional[str] = None,
    institution: Optional[str] = None,
    level: Optional[str] = None,
    domain: Optional[str] = None,
    motivation: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Modifie les infos d'un utilisateur."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
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
    
    return {"message": "Utilisateur mis à jour", "user": {"mailer": user.email, "name": user.name}}


@router.put("/users/{mailer}/validate")
async def validate_user(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Valide un utilisateur (lui permet de se connecter)."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.validated = True
    db.commit()
    
    return {"message": f"Utilisateur {user.name} validé avec succès"}


@router.put("/users/{mailer}/reject")
async def reject_user(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Rejette un utilisateur en attente."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"Utilisateur {user.name} rejeté et supprimé"}


@router.put("/users/{mailer}/suspend")
async def suspend_user(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Suspend un utilisateur (lui interdit l'accès)."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.suspended = True
    db.commit()
    
    return {"message": f"Utilisateur {user.name} suspendu"}


@router.put("/users/{mailer}/unsuspend")
async def unsuspend_user(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Réactive un utilisateur suspendu."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.suspended = False
    db.commit()
    
    return {"message": f"Utilisateur {user.name} réactivé"}


@router.put("/users/{mailer}/role")
async def assign_role(
    mailer: str,
    role: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Assigne un rôle à un utilisateur."""
    _verify_admin(request, db)
    
    valid_roles = {"membre", "chercheur", "responsable", "admin"}
    
    if role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Rôle invalide. Acceptés: {', '.join(valid_roles)}"
        )
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.role = role
    db.commit()
    
    return {"message": f"Rôle '{role}' assigné à {user.name}"}


@router.delete("/users/{mailer}")
async def delete_user(
    mailer: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Supprime un utilisateur et toutes ses données."""
    _verify_admin(request, db)
    
    user = db.query(models.User).filter(models.User.email == mailer).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db.delete(user)  # Cascade delete sur contributes, questions, suggestions
    db.commit()
    
    return {"message": f"Utilisateur {user.name} et ses données supprimés"}


@router.post("/users/create")
async def create_user_admin(
    request: Request,
    data: dict,
    db: Session = Depends(get_db),
):
    """Admin: crée un nouvel utilisateur avec un mot de passe par défaut."""
    _verify_admin(request, db)
    
    import string
    import secrets
    from dependencies import get_password_hash
    from datetime import date
    
    # Récupérer le nom depuis les données
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Le nom est requis")
    
    # Générer un email basé sur le nom (enlever espaces, minuscules)
    base_email = name.lower().replace(" ", ".")
    email = f"{base_email}@betalab.local"
    counter = 1
    original_email = email
    
    # Éviter les doublons en ajoutant un numéro si nécessaire
    while db.query(models.User).filter(models.User.email == email).first():
        email = f"{base_email}{counter}@betalab.local"
        counter += 1
    
    # Générer un mot de passe par défaut (10 caractères aléatoires)
    default_password = "".join(
        secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
        for _ in range(10)
    )
    
    # Créer l'utilisateur avec les valeurs par défaut
    user = models.User(
        email=email,
        name=name,
        birthdate=date.today(),  # Valeur par défaut
        occupation="Non spécifié",
        institution="Non spécifié",
        level="",
        domain="",
        password=get_password_hash(default_password),
        motivation="",
        validated=False,  # Doit être validé par l'admin
        suspended=False,
        role="membre",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Utilisateur {name} créé avec succès",
        "email": email,
        "username": email,  # L'email servira de username
        "password": default_password,
        "user": {
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "validated": user.validated,
        }
    }
