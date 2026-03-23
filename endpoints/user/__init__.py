"""
Endpoints pour les utilisateurs
"""

def get_user_routers():
    """Retourne tous les routers utilisateur."""
    from endpoints.user.user_profile import router as user_profile_router
    from endpoints.user.user_contributions import router as user_contributions_router
    from endpoints.user.user_auth import router as user_auth_router
    from endpoints.user.profile_modifications import router as profile_modifications_router
    
    return [
        user_auth_router,
        user_profile_router,
        user_contributions_router,
        profile_modifications_router,
    ]
