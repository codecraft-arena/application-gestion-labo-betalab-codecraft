"""
Endpoints partagés entre utilisateurs et administrateurs
"""

def get_shared_routers():
    """Retourne tous les routers partagés."""
    from endpoints.shared.shared_contact import router as contact_router
    from endpoints.shared.shared_questions import router as questions_router
    from endpoints.shared.shared_suggestions import router as suggestions_router
    
    return [
        contact_router,
        questions_router,
        suggestions_router,
    ]
