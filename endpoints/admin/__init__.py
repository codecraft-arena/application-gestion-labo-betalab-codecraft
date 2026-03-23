"""
Endpoints pour les administrateurs
"""

def get_admin_routers():
    """Retourne tous les routers admin."""
    from endpoints.admin.admin_auth import router as admin_auth_router
    from endpoints.admin.admin_users import router as admin_users_router
    from endpoints.admin.admin_activities import router as admin_activities_router
    from endpoints.admin.admin_events import router as admin_events_router
    from endpoints.admin.approvals import router as approvals_router
    
    return [
        admin_auth_router,
        admin_users_router,
        admin_activities_router,
        admin_events_router,
        approvals_router,
    ]
