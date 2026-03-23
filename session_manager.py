"""
Gestion des Sessions Persistantes en Base de Données.
Remplace le stockage en-mémoire par une persistance BD.
"""

import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models

class SessionManager:
    """Gère les sessions persistantes."""
    
    @staticmethod
    def create_session(
        db: Session,
        user_mailer: str,
        user_agent: str = "",
        ip_address: str = "",
        duration_hours: int = 24
    ) -> str:
        """
        Crée une nouvelle session pour un utilisateur.
        Retourne le token de session.
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        session = models.Session(
            token=token,
            user_mailer=user_mailer,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        return token
    
    @staticmethod
    def get_user_from_token(db: Session, token: str) -> models.User | None:
        """
        Récupère l'utilisateur à partir d'un token de session.
        Retourne None si token invalide ou expiré.
        """
        # Nettoyer d'abord les sessions expirées
        db.query(models.Session).filter(
            models.Session.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        session = db.query(models.Session).filter(
            models.Session.token == token,
            models.Session.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Vérifier que c'est une session utilisateur (pas admin)
        if hasattr(session, 'session_type') and session.session_type == "admin":
            return None
            
        return session.user
    
    @staticmethod
    def revoke_session(db: Session, token: str) -> bool:
        """Invalide une session (logout)."""
        session = db.query(models.Session).filter(
            models.Session.token == token
        ).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_sessions(db: Session, user_mailer: str) -> int:
        """Invalide TOUTES les sessions d'un utilisateur."""
        count = db.query(models.Session).filter(
            models.Session.user_mailer == user_mailer
        ).delete()
        db.commit()
        return count
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Nettoie les sessions expirées de la BD."""
        count = db.query(models.Session).filter(
            models.Session.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return count
    
    @staticmethod
    def extend_session(db: Session, token: str, hours: int = 24) -> bool:
        """Prolonge une session existante."""
        session = db.query(models.Session).filter(
            models.Session.token == token
        ).first()
        
        if session:
            session.expires_at = datetime.utcnow() + timedelta(hours=hours)
            db.commit()
            return True
        return False
