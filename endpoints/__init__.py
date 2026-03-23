"""
Endpoints package — Architecture modulaire BetaLab
"""

from fastapi import APIRouter

def get_routers():
    """Retourne tous les routers des endpoints."""
    from endpoints.admin import get_admin_routers
    from endpoints.user import get_user_routers
    from endpoints.shared import get_shared_routers
    
    return {
        "admin": get_admin_routers(),
        "user": get_user_routers(),
        "shared": get_shared_routers(),
    }
