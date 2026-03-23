"""
Authentification Admin — Système amélioré en BD au lieu de hardcoding.
Gère création, validation et permissions des utilisateurs admin.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
from database import get_db
from dependencies import pwd_context

class AdminAuthManager:
    """Gère l'authentification et les permissions admin."""
    
    @staticmethod
    def create_admin_user(
        db: Session,
        username: str,
        password: str,
        email: str,
        role: str = "admin"
    ) -> models.AdminUser:
        """Crée un nouvel utilisateur admin."""
        
        # Vérifier doublons
        if db.query(models.AdminUser).filter(models.AdminUser.username == username).first():
            raise HTTPException(
                status_code=400,
                detail="Cet utilisateur admin existe déjà"
            )
        
        if db.query(models.AdminUser).filter(models.AdminUser.email == email).first():
            raise HTTPException(
                status_code=400,
                detail="Cet email est déjà utilisé"
            )
        
        # Valider mot de passe
        if len(password) < 12:
            raise HTTPException(
                status_code=400,
                detail="Mot de passe admin doit être ≥ 12 caractères"
            )
        
        # Créer l'admin
        password_hashed = pwd_context.hash(password)
        admin = models.AdminUser(
            username=username,
            password=password_hashed,
            email=email,
            role=role,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    @staticmethod
    def verify_admin(db: Session, username: str, password: str) -> models.AdminUser | None:
        """Vérifie les identifiants admin et retourne l'utilisateur."""
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.username == username,
            models.AdminUser.is_active == True
        ).first()
        
        if not admin:
            return None
        
        if not pwd_context.verify(password, admin.password):
            return None
        
        return admin
    
    @staticmethod
    def get_admin_by_username(db: Session, username: str) -> models.AdminUser | None:
        """Récupère un admin par son username."""
        return db.query(models.AdminUser).filter(
            models.AdminUser.username == username
        ).first()
    
    @staticmethod
    def deactivate_admin(db: Session, admin_id: int) -> bool:
        """Désactive un compte admin."""
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.id == admin_id
        ).first()
        
        if admin:
            admin.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def list_admins(db: Session):
        """Liste tous les utilisateurs admin."""
        return db.query(models.AdminUser).all()

# ──────────────────────────────────────────────────────────────────────────────
# Initialisation des Admin par Défaut
# ──────────────────────────────────────────────────────────────────────────────

def init_default_admin(db: Session):
    """Crée un admin par défaut s'il n'existe pas."""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    # Récupérer du .env ou utiliser défaut
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "AdminPassword123@Secure")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@betalab.local")
    
    # Vérifier si existe
    if db.query(models.AdminUser).filter(
        models.AdminUser.username == admin_user
    ).first():
        return False
    
    # Créer
    try:
        AdminAuthManager.create_admin_user(
            db=db,
            username=admin_user,
            password=admin_pass,
            email=admin_email,
            role="admin"
        )
        print(f"✅ Admin par défaut créé: {admin_user}")
        return True
    except Exception as e:
        print(f"⚠️  Impossible de créer admin par défaut: {e}")
        return False
