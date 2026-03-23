"""
Sécurité — CSRF Protection & Rate Limiting.
"""

import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
from fastapi import HTTPException, status, Request
from functools import lru_cache
from collections import defaultdict
from time import time

# ═══════════════════════════════════════════════════════════════════════════════
# CSRF PROTECTION
# ═══════════════════════════════════════════════════════════════════════════════

class CSRFManager:
    """Gère les tokens CSRF pour protection contre les attaques."""
    
    @staticmethod
    def generate_token(db: Session, session_id: int | None = None) -> str:
        """Génère un nouveau token CSRF."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        csrf = models.CSRFToken(
            token=token,
            session_id=session_id,
            expires_at=expires_at
        )
        db.add(csrf)
        db.commit()
        return token
    
    @staticmethod
    def verify_token(db: Session, token: str) -> bool:
        """Vérifie qu'un token CSRF est valide et non expiré."""
        # Nettoyer les tokens expirés
        db.query(models.CSRFToken).filter(
            models.CSRFToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        csrf = db.query(models.CSRFToken).filter(
            models.CSRFToken.token == token,
            models.CSRFToken.expires_at > datetime.utcnow()
        ).first()
        
        if csrf:
            # Optionnel: Invalider après utilisation (une seule utilisation par token)
            db.delete(csrf)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired(db: Session) -> int:
        """Nettoie les tokens CSRF expirés."""
        count = db.query(models.CSRFToken).filter(
            models.CSRFToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return count

# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Rate limiting en mémoire pour les endpoints sensibles."""
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # IP → [timestamp1, timestamp2, ...]
    
    def _get_key(self, request: Request) -> str:
        """Récupère la clé d'identification (IP)."""
        # Gérer proxies (X-Forwarded-For)
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def is_allowed(self, request: Request) -> bool:
        """Vérifie si la requête est autorisée."""
        key = self._get_key(request)
        now = time()
        
        # Nettoyer les vieilles entrées (outside window)
        self.requests[key] = [
            ts for ts in self.requests[key]
            if now - ts < self.window_seconds
        ]
        
        # Vérifier limite
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Ajouter requête actuelle
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, request: Request) -> int:
        """Retourne le nombre de requêtes restantes."""
        key = self._get_key(request)
        return max(0, self.max_requests - len(self.requests[key]))

# Instances de rate limiting
limiter_login = RateLimiter(max_requests=5, window_seconds=300)  # 5 tentatives / 5 min
limiter_contact = RateLimiter(max_requests=3, window_seconds=3600)  # 3 par heure
limiter_suggestion = RateLimiter(max_requests=10, window_seconds=86400)  # 10 par jour

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def check_rate_limit(limiter: RateLimiter, request: Request):
    """Middleware pour vérifier le rate limit."""
    if not limiter.is_allowed(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de requêtes. Veuillez réessayer plus tard.",
            headers={"Retry-After": str(limiter.window_seconds)}
        )
