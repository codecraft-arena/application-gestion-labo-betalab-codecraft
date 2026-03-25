"""
Couche de compatibilité — BetaLab
Mappe les anciens endpoints utilisés par le frontend vers les nouveaux endpoints.
Permet une transition en douceur sans refonte complète du frontend.

Endpoints mappés:
  POST /connexion → POST /api/user/login (FormData conversion)
  POST /admin-login → POST /api/admin/login (FormData conversion)
  GET /logout → GET /api/user/logout
  GET /api/me → GET /api/user/profile
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

import models
from database import get_db
from dependencies import get_password_hash, verify_password
from session_manager import SessionManager

router = APIRouter(tags=["Compatibility"])

# ═════════════════════════════════════════════════════════════════════════════
# USER LOGIN & LOGOUT (Compatibility with old frontend)
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/connexion")
async def user_login_compat(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Login utilisateur — MapS to /api/user/login
    Frontend sends FormData, backward compatible.
    On success: redirect to /dashuser
    """
    # Vérifier utilisateur existe et active
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()
    
    if not user or not verify_password(password, user.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Email ou mot de passe incorrect"}
        )
    
    if user.suspended:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Compte suspendu. Contactez l'administrateur."}
        )
    
    if not user.validated:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Compte non validé par l'administrateur"}
        )
    
    # Créer session en BD
    session_token = SessionManager.create_session(
        db=db, 
        user_mailer=user.email,
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
        duration_hours=24
    )
    
    # Mettre à jour le session_type pour utilisateur
    session = db.query(models.Session).filter(models.Session.token == session_token).first()
    if session:
        session.session_type = "user"
        db.commit()
    
    # Réponse avec cookie httpOnly + redirection
    response = RedirectResponse(url="/dashuser", status_code=302)
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=False,  # À mettre à True en production
        samesite="lax",
        max_age=86400 * 7  # 7 jours
    )
    return response


@router.post("/admin-login")
async def admin_login_compat(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Login admin — Maps to /api/admin/login
    Frontend sends FormData, returns JSON with redirect URL.
    """
    # Vérifier admin existe et actif
    admin = db.query(models.AdminUser).filter(
        models.AdminUser.username == username
    ).first()
    
    if not admin or not verify_password(password, admin.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Nom d'utilisateur ou mot de passe incorrect"}
        )
    
    if not admin.is_active:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Compte admin désactivé"}
        )
    
    # Créer session admin en BD avec SessionManager
    session_token = SessionManager.create_session(
        db=db,
        user_mailer=f"admin_{username}",
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
        duration_hours=24
    )
    
    # Ajouter le type de session admin manuellement
    session = db.query(models.Session).filter(models.Session.token == session_token).first()
    if session:
        session.session_type = "admin"
        db.commit()
    
    # Mettre à jour last_login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Réponse JSON avec URL redirection ET cookie
    response = JSONResponse(
        content={
            "message": "Connexion admin réussie",
            "token": session_token,
            "redirect": "/dashadmin"
        }
    )
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=False,  # À mettre à True en production
        samesite="lax",
        max_age=86400 * 7  # 7 jours
    )
    return response


@router.get("/logout")
async def logout_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Logout utilsateur — Maps to exit session. Redirect to home."""
    token = request.cookies.get("session_token")
    if token:
        # Supprimer session de BD
        db.query(models.Session).filter(
            models.Session.token == token
        ).delete()
        db.commit()
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_token")
    return response


# ═════════════════════════════════════════════════════════════════════════════
# USER PROFILE & DATA (Compatibility with frontend paths)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/me")
async def get_current_user_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get current user profile — Maps to /api/user/profile
    Frontend calls GET /api/me
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré ou invalide"
        )
    
    return {
        "email": user.email,
        "name": user.name,
        "occupation": user.occupation,
        "institution": user.institution,
        "level": user.level,
        "domain": user.domain,
        "motivation": user.motivation,
        "suspended": user.suspended,
        "role": user.role,
    }


@router.put("/api/users/{email}/profile")
async def update_user_profile_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Update user profile — Maps to /api/user/profile
    Frontend sends PUT with JSON body via apiFetch
    """
    # Vérifier authentification
    token = request.cookies.get("session_token")
    current_user = SessionManager.get_user_from_token(db, token)
    if not current_user or current_user.email != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé"
        )
    
    # Récupérer body JSON
    body = await request.json()
    
    # Mettre à jour champs autorisés
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    updatable = ["name", "occupation", "institution", "level", "domain", "motivation"]
    for field in updatable:
        if field in body:
            setattr(user, field, body[field])
    
    db.commit()
    
    return {
        "email": user.email,
        "name": user.name,
        "occupation": user.occupation,
        "institution": user.institution,
        "level": user.level,
        "domain": user.domain,
        "motivation": user.motivation,
    }


# ═════════════════════════════════════════════════════════════════════════
# ROUTES API MANQUANTES (pour le dashboard admin)
# ═════════════════════════════════════════════════════════════════════════

@router.get("/api/users")
async def list_all_users_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all users for admin dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    users = db.query(models.User).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
            "role": u.role,
            "validated": u.validated,
            "suspended": u.suspended,
        }
        for u in users
    ]


@router.get("/api/activities")
async def list_all_activities_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all activities for admin dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    activities = db.query(models.Activity).all()
    return [
        {
            "id_activity": a.id_activity,
            "name_activity": a.name_activity,
            "description": a.description,
            "status": a.status,
            "class_activity": a.class_activity,
            "created_by": a.created_by,
            "user_approval_status": a.user_approval_status,
        }
        for a in activities
    ]


@router.get("/api/contact")
async def list_contact_requests_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List contact requests for admin dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    contacts = db.query(models.ContactRequest).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "subject": c.subject,
            "message": c.message,
            "status": c.status,
            "created_at": c.created_at,
        }
        for c in contacts
    ]


@router.get("/api/users/pending")
async def list_pending_users_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending users for admin dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    pending_users = db.query(models.User).filter(models.User.validated == False).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
            "role": u.role,
            "validated": u.validated,
            "suspended": u.suspended,
            "level": u.level,
            "domain": u.domain,
            "motivation": u.motivation,
        }
        for u in pending_users
    ]


@router.get("/api/admin/contributions")
async def list_admin_contributions_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all contributions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    contributions = db.query(models.Contribute, models.User, models.Activity).join(
        models.User, models.Contribute.id_user == models.User.email
    ).join(
        models.Activity, models.Contribute.id_activity == models.Activity.id_activity
    ).all()
    
    return [
        {
            "user_email": u.email,
            "user_name": u.name,
            "id_activity": a.id_activity,
            "name_activity": a.name_activity,
            "class_activity": a.class_activity,
            "participation_status": c.participation_status,
            "participation_date": c.period.isoformat() if hasattr(c, "period") and c.period else None,
        }
        for c, u, a in contributions
    ]


@router.get("/api/admin/pending-approvals")
async def list_pending_approvals_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending approvals for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    # Pour l'instant, retourner une liste vide
    return []


# ═════════════════════════════════════════════════════════════════════════
# ROUTES UTILISATEUR MANQUANTES (pour le dashboard utilisateur)
# ═════════════════════════════════════════════════════════════════════════

@router.get("/api/contributions/{email}")
async def list_user_contributions_api_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List user contributions for dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Activités
    act_contribs = db.query(models.Contribute, models.Activity).join(
        models.Activity, models.Contribute.id_activity == models.Activity.id_activity
    ).filter(
        models.Contribute.id_user == email,
        models.Contribute.participation_status == "accepted"
    ).all()
    
    # Événements
    evt_contribs = db.query(models.EventParticipate, models.Event).join(
        models.Event, models.EventParticipate.id_event == models.Event.id
    ).filter(
        models.EventParticipate.id_user == email,
        models.EventParticipate.status == "accepted"
    ).all()

    return [
        {
            "id_user": c.id_user,
            "id_activity": c.id_activity,
            "name_activity": a.name_activity,
            "description": a.description,
            "class_activity": a.class_activity,
            "participation_status": c.participation_status,
            "participation_date": c.period.isoformat() if hasattr(c, "period") and c.period else None,
        }
        for c, a in act_contribs
    ] + [
        {
            "id_user": p.id_user,
            "id_activity": e.id,
            "name_activity": e.title,
            "description": e.description,
            "class_activity": e.event_type,
            "participation_status": p.status,
            "participation_date": e.event_date.isoformat() if e.event_date else None,
        }
        for p, e in evt_contribs
    ]


@router.get("/api/invitations/{email}")
async def list_user_invitations_api_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List user invitations for dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Activités
    act_invs = db.query(models.Contribute, models.Activity).join(
        models.Activity, models.Contribute.id_activity == models.Activity.id_activity
    ).filter(
        models.Contribute.id_user == email,
        models.Contribute.participation_status == "pending"
    ).all()
    
    # Événements
    evt_invs = db.query(models.EventParticipate, models.Event).join(
        models.Event, models.EventParticipate.id_event == models.Event.id
    ).filter(
        models.EventParticipate.id_user == email,
        models.EventParticipate.status == "pending"
    ).all()

    return [
        {
            "type": "activity",
            "id_activity": a.id_activity,
            "name_activity": a.name_activity,
            "description": a.description,
            "class_activity": a.class_activity,
            "participation_status": c.participation_status,
        }
        for c, a in act_invs
    ] + [
        {
            "type": "event",
            "id_event": e.id,
            "name_activity": e.title, # Mapper sur name_activity pour compatibilité UI
            "description": e.description,
            "class_activity": e.event_type, # Mapper sur class_activity
            "participation_status": p.status,
        }
        for p, e in evt_invs
    ]


@router.get("/api/questions/user/{email}")
async def list_user_questions_api_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List user questions for dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    questions = db.query(models.Question).filter(
        models.Question.id_user == email
    ).all()
    return [
        {
            "id_question": q.id_question,
            "libele_question": q.libele_question,
            "description_question": q.description_question,
            "date_question": q.created_at,
            "visibility": q.visibility,
            "responses": [
                {
                    "id_response": r.id_response,
                    "libelle_response": r.libelle_response,
                    "description_response": r.description_response,
                }
                for r in q.responses
            ] if q.responses else [],
        }
        for q in questions
    ]


@router.get("/api/suggestions/user/{email}")
async def list_user_suggestions_api_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List user suggestions for dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.id_user == email
    ).all()
    return [
        {
            "id_suggest": s.id_suggest,
            "libele": s.libele,
            "description_suggest": s.description_suggest,
            "note": s.note,
            "date_suggest": s.created_at,
        }
        for s in suggestions
    ]


@router.get("/api/users/{email}/pending-modifications")
async def list_user_pending_modifications_api_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """List user pending modifications for dashboard."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Pour l'instant, retourner une liste vide
    return []


@router.post("/api/questions")
async def create_question_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new question."""
    token = request.cookies.get("session_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Utiliser la même logique que get_current_user_compat
    user = SessionManager.get_user_from_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    try:
        data = await request.json()
        question = models.Question(
            libele_question=data.get("libele_question", ""),
            description_question=data.get("description_question", ""),
            id_user=user.email,
            visibility="pending",  # en attente de validation
            created_at=datetime.utcnow()
        )
        db.add(question)
        db.commit()
        return {"message": "Question créée avec succès", "id": question.id_question}
    except Exception as e:
        print(f"DEBUG: Erreur: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/suggestions")
async def create_suggestion_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new suggestion."""
    token = request.cookies.get("session_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Utiliser la même logique que get_current_user_compat
    user = SessionManager.get_user_from_token(db, token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    try:
        data = await request.json()
        suggestion = models.Sugestion(
            libele=data.get("libele", ""),
            description_suggest=data.get("description_suggest", ""),
            note=int(data.get("note", 0)),  # Convertir en entier
            id_user=user.email,
            created_at=datetime.utcnow()  # Utiliser created_at au lieu de date_suggest
        )
        db.add(suggestion)
        db.commit()
        return {"message": "Suggestion créée avec succès", "id": suggestion.id_suggest}
    except Exception as e:
        print(f"DEBUG SUGGESTION: Erreur: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN API ENDPOINTS (Compatibility with /api/admin/* routes)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/admin/users")
async def list_users_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all users for admin — Maps to existing endpoint."""
    # Vérifier que l'utilisateur est admin
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    users = db.query(models.User).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
            "role": u.role,
            "suspended": u.suspended,
        }
        for u in users
    ]


@router.get("/api/admin/users/pending")
async def list_pending_users_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending users for validation."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    pending = db.query(models.User).filter(
        models.User.validated == False
    ).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
        }
        for u in pending
    ]


@router.get("/api/admin/activities")
async def list_activities_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all activities for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    activities = db.query(models.Activity).all()
    return [
        {
            "id_activity": a.id_activity,
            "libele": a.name_activity,  # Utiliser name_activity au lieu de libele
            "description": a.description,
            "status": a.status,
            "class_activity": a.class_activity,
            "created_by": a.created_by,
            "user_approval_status": a.user_approval_status,
        }
        for a in activities
    ]


@router.get("/api/admin/events")
async def list_events_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List events for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    events = db.query(models.Event).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "event_date": e.event_date,
            "location": e.location,
            "event_type": e.event_type,
        }
        for e in events
    ]


@router.get("/api/admin/questions")
async def list_questions_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all questions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    questions = db.query(models.Question).all()
    return [
        {
            "id_question": q.id_question,
            "id_user": q.id_user,
            "libele_question": q.libele_question,
            "description_question": q.description_question,
            "date_question": q.created_at,
            "visibility": q.visibility,
            "responses": [
                {
                    "id_response": r.id_response,
                    "libelle_response": r.libelle_response,
                    "description_response": r.description_response,
                }
                for r in q.responses
            ] if q.responses else [],
        }
        for q in questions
    ]


@router.get("/api/admin/contributions")
async def list_contributions_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all contributions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    contributions = db.query(models.Contribute).all()
    return [
        {
            "id_user": c.id_user,
            "id_activity": c.id_activity,
            "participation_status": c.participation_status,
            "participation_date": c.period.isoformat() if hasattr(c, "period") and c.period else None,
        }
        for c in contributions
    ]


@router.get("/api/admin/suggestions")
async def list_suggestions_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all suggestions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    suggestions = db.query(models.Sugestion).all()
    return [
        {
            "id": s.id_suggest,
            "user": s.id_user,
            "title": s.libele,
            "description": s.description_suggest,
            "rating": s.note,
            "created_at": s.created_at,
        }
        for s in suggestions
    ]


@router.get("/api/admin/pending-approvals")
async def list_pending_approvals_api_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending approvals for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    # Profile modifications
    profile_mods = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.request_status == "pending"
    ).all()
    
    # Questions pending
    questions = db.query(models.Question).filter(
        models.Question.visibility == "pending"
    ).all()
    
    # Suggestions pending
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.visibility == "pending"
    ).all()
    
    # Activities pending
    activities = db.query(models.Activity).filter(
        models.Activity.user_approval_status == "pending_submission"
    ).all()

    # Contributions pending (participation requests)
    contributions = db.query(models.Contribute, models.Activity).join(
        models.Activity, models.Contribute.id_activity == models.Activity.id_activity
    ).filter(
        models.Contribute.participation_status == "pending"
    ).all()

    # Event participations pending
    event_parts = db.query(models.EventParticipate, models.Event).join(
        models.Event, models.EventParticipate.id_event == models.Event.id
    ).filter(
        models.EventParticipate.status == "pending"
    ).all()
    
    return {
        "profile_modifications": [
            {
                "id": m.id,
                "user_email": m.user_email,
                "field": m.field_name,
                "old_value": m.old_value,
                "new_value": m.new_value,
                "created_at": m.created_at,
            } for m in profile_mods
        ],
        "pending_questions": [
            {
                "id": q.id_question,
                "user": q.id_user,
                "title": q.libele_question,
                "description": q.description_question,
                "created_at": q.created_at,
            } for q in questions
        ],
        "pending_suggestions": [
            {
                "id": s.id_suggest,
                "user": s.id_user,
                "title": s.libele,
                "description": s.description_suggest,
                "rating": s.note,
                "created_at": s.created_at,
            } for s in suggestions
        ],
        "pending_activities": [
            {
                "id": a.id_activity,
                "name": a.name_activity,
                "creator": a.created_by,
                "description": a.description,
                "class": a.class_activity,
            } for a in activities
        ],
        "pending_contributions": [
            {
                "id": f"contrib/{c.id_activity}/{c.id_user}",
                "user": c.id_user,
                "title": f"Demande Participation: {a.name_activity}",
                "description": f"Détails: {a.description[:100]}...",
                "created_at": datetime.utcnow(),
            } for c, a in contributions
        ],
        "pending_event_participations": [
            {
                "id": f"event/{p.id_event}/{p.id_user}",
                "user": p.id_user,
                "title": f"Demande Participation Event: {e.title}",
                "description": f"Lieu: {e.location}",
                "created_at": p.created_at,
            } for p, e in event_parts
        ],
        "counts": {
            "profile_modifications": len(profile_mods),
            "questions": len(questions),
            "suggestions": len(suggestions),
            "activities": len(activities),
            "contributions": len(contributions),
            "events": len(event_parts),
            "total": len(profile_mods) + len(questions) + len(suggestions) + len(activities) + len(contributions) + len(event_parts),
        }
    }


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (Compatibility with frontend paths)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/users")
async def list_all_users_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all users for admin — Maps to existing endpoint."""
    # Vérifier que l'utilisateur est admin
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    users = db.query(models.User).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
            "level": u.level,
            "domain": u.domain,
            "motivation": u.motivation,
            "role": u.role,
            "suspended": u.suspended,
            "validated": u.validated,
        }
        for u in users
    ]


@router.get("/api/users/pending")
async def list_pending_users_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List pending users for validation."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token
    ).first()
    if not session or session.session_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    pending = db.query(models.User).filter(
        models.User.validated == False,
        models.User.suspended == False
    ).all()
    return [
        {
            "email": u.email,
            "name": u.name,
            "occupation": u.occupation,
            "institution": u.institution,
            "level": u.level,
            "domain": u.domain,
            "motivation": u.motivation,
            "role": u.role,
            "validated": False,
            "suspended": False,
        }
        for u in pending
    ]


# ═════════════════════════════════════════════════════════════════════════════
# ACTIVITIES & EVENTS (Compatibility)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/activities")
async def list_activities_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all activities — public endpoint."""
    activities = db.query(models.Activity).all()
    return [
        {
            "id_activity": a.id_activity,
            "name_activity": a.name_activity,
            "description": a.description,
            "status": a.status,
            "class_activity": a.class_activity,
            "user_approval_status": a.user_approval_status,
        }
        for a in activities
    ]


@router.get("/api/admin/events")
async def list_admin_events_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List events for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    events = db.query(models.Event).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "event_date": e.event_date,
            "location": e.location,
            "event_type": e.event_type,
        }
        for e in events
    ]


# ═════════════════════════════════════════════════════════════════════════════
# CONTRIBUTIONS & QUESTIONS (Compatibility)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/contributions/{email}")
async def get_user_contributions_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get contributions for a user."""
    contributions = db.query(models.Contribute).filter(
        models.Contribute.id_user == email
    ).all()
    return [
        {
            "id_activity": c.id_activity,
            "participation_status": c.participation_status,
            "participation_date": c.period.isoformat() if hasattr(c, "period") and c.period else None,
        }
        for c in contributions
    ]


@router.get("/api/invitations/{email}")
async def get_user_invitations_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get invitations for a user — activities they're invited to."""
    # Récupérer les activités où l'utilisateur a une invitation (participation_status = 'pending')
    invitations = db.query(models.Contribute).filter(
        models.Contribute.id_user == email,
        models.Contribute.participation_status == "pending"
    ).all()
    
    result = []
    for inv in invitations:
        activity = db.query(models.Activity).filter(
            models.Activity.id_activity == inv.id_activity
        ).first()
        if activity:
            result.append({
                "id_activity": activity.id_activity,
                "name_activity": activity.name_activity,
                "description": activity.description,
                "participation_status": inv.participation_status,
            })
    return result


@router.put("/api/invitations/{email}/{activity_id}/{action}")
async def handle_invitation_compat(
    email: str,
    activity_id: str,
    action: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Handle invitation (accept/reject) — Maps to contribution update."""
    if action not in ["accept", "reject", "refuse"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action invalide. Utilisez 'accept' ou 'reject'/'refuse'"
        )
    
    # Vérifier utilisateur
    token = request.cookies.get("session_token")
    user = SessionManager.get_user_from_token(db, token)
    if not user or user.email != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé"
        )
    
    # Trouver contribution (Activité ou Événement)
    contribution = db.query(models.Contribute).filter(
        models.Contribute.id_user == email,
        models.Contribute.id_activity == activity_id
    ).first()
    
    event_part = None
    if not contribution:
        # Essayer comme un événement
        try:
            evt_id = int(activity_id)
            event_part = db.query(models.EventParticipate).filter(
                models.EventParticipate.id_user == email,
                models.EventParticipate.id_event == evt_id
            ).first()
        except (ValueError, TypeError):
            pass

    if not contribution and not event_part:
        raise HTTPException(
            status_code=404,
            detail="Invitation non trouvée"
        )
    
    is_accept = (action == "accept")
    status_str = "accepted" if is_accept else "rejected"

    if contribution:
        contribution.participation_status = status_str
        contribution.period = datetime.utcnow().date() if is_accept else None
    else:
        event_part.status = status_str

    db.commit()
    
    return {
        "detail": f"Invitation {action}ée",
        "participation_status": status_str
    }


@router.get("/api/questions/user/{email}")
async def get_user_questions_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get questions asked by a user."""
    questions = db.query(models.Question).filter(
        models.Question.id_user == email
    ).all()
    return [
        {
            "id_question": q.id_question,
            "libele_question": q.libele_question,
            "description_question": q.description_question,
            "date_question": q.created_at,
            "visibility": q.visibility,
            "responses": [
                {
                    "id_response": r.id_response,
                    "libelle_response": r.libelle_response,
                    "description_response": r.description_response,
                }
                for r in q.responses
            ] if q.responses else [],
        }
        for q in questions
    ]


@router.post("/api/questions")
async def post_question_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Post a question — Frontend sends JSON."""
    # Vérifier authentification
    token = request.cookies.get("session_token")
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    body = await request.json()
    
    question = models.Question(
        id_user=user.email,
        libele_question=body.get("libele_question", ""),
        description_question=body.get("description_question", ""),
        created_at=datetime.utcnow(),
    )
    db.add(question)
    db.commit()
    
    return {
        "id_question": question.id_question,
        "detail": "Question envoyée avec succès"
    }


@router.get("/api/admin/questions")
async def list_admin_questions_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all questions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    questions = db.query(models.Question).all()
    return [
        {
            "id_question": q.id_question,
            "id_user": q.id_user,
            "libele_question": q.libele_question,
            "description_question": q.description_question,
            "date_question": q.created_at,
            "visibility": q.visibility,
            "responses": [
                {
                    "id_response": r.id_response,
                    "libelle_response": r.libelle_response,
                    "description_response": r.description_response,
                }
                for r in q.responses
            ] if q.responses else [],
        }
        for q in questions
    ]


# ═════════════════════════════════════════════════════════════════════════════
# SUGGESTIONS & ADMIN DATA (Compatibility)
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/api/suggestions")
async def post_suggestion_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Post a suggestion — Frontend sends JSON."""
    token = request.cookies.get("session_token")
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    body = await request.json()
    
    suggestion = models.Sugestion(
        id_user=user.email,
        libele=body.get("libele", ""),
        description_suggest=body.get("description_suggest", ""),
        note=body.get("note", 0),
        created_at=datetime.utcnow(),
    )
    db.add(suggestion)
    db.commit()
    
    return {
        "id_suggest": suggestion.id_suggest,
        "detail": "Suggestion envoyée avec succès"
    }


@router.get("/api/suggestions/user/{email}")
async def get_user_suggestions_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Get suggestions submitted by a user."""
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.id_user == email
    ).all()
    return [
        {
            "id_suggest": s.id_suggest,
            "libele": s.libele,
            "description_suggest": s.description_suggest,
            "note": s.note,
            "date_suggest": s.created_at,
        }
        for s in suggestions
    ]


@router.get("/api/admin/contributions")
async def list_admin_contributions_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all contributions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    contributions = db.query(models.Contribute).all()
    return [
        {
            "id_user": c.id_user,
            "id_activity": c.id_activity,
            "participation_status": c.participation_status,
            "participation_date": c.period.isoformat() if hasattr(c, "period") and c.period else None,
        }
        for c in contributions
    ]


@router.get("/api/admin/suggestions")
async def list_admin_suggestions_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """List all suggestions for admin."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès admin requis"
        )
    
    suggestions = db.query(models.Sugestion).all()
    return [
        {
            "id_suggest": s.id_suggest,
            "id_user": s.id_user,
            "libele": s.libele,
            "note": s.note,
            "date_suggest": s.created_at,
        }
        for s in suggestions
    ]


# ═════════════════════════════════════════════════════════════════════════════
# CONTACT FORM (Public endpoint)
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/api/contact")
async def submit_contact_form_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Submit a contact form — Public endpoint.
    If subject mentions 'Rejoindre', mark as join request.
    Frontend sends JSON with: name, email, subject, message
    """
    body = await request.json()
    
    is_join_request = "rejoindre" in body.get("subject", "").lower()
    
    contact = models.ContactRequest(
        name=body.get("name", ""),
        email=body.get("email", ""),
        subject=body.get("subject", ""),
        message=body.get("message", ""),
        is_join_request=is_join_request,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(contact)
    db.commit()
    
    return {
        "detail": "Formulaire de contact reçu",
        "contact_id": contact.id,
        "is_join_request": is_join_request,
    }


# ═════════════════════════════════════════════════════════════════════════════
# ADHESION / INVITATION FLOW
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/adhesion/{token}")
async def verify_adhesion_token_compat(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Verify adhesion token — Frontend calls before filling form.
    Returns prefilled data (email, name) if token is valid.
    """
    inv_token = db.query(models.InvitationToken).filter(
        models.InvitationToken.token == token
    ).first()
    
    if not inv_token:
        raise HTTPException(
            status_code=404,
            detail="Token d'invitation invalide"
        )
    
    if inv_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=410,
            detail="Token d'invitation expiré"
        )
    
    if inv_token.used:
        raise HTTPException(
            status_code=409,
            detail="Token d'invitation déjà utilisé"
        )
    
    # Récupérer le contact original pour le nom
    contact = db.query(models.ContactRequest).filter(
        models.ContactRequest.id == inv_token.contact_id
    ).first()
    
    return {
        "email": inv_token.email,
        "name": contact.name if contact else "",
        "token": token,
    }


@router.post("/api/adhesion/{token}")
async def complete_adhesion_compat(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Complete adhesion — User fills form and creates account.
    Frontend sends JSON with: name, birthdate, occupation, institution, level, domain, motivation, password
    Creates user in DB and marks token as used.
    """
    inv_token = db.query(models.InvitationToken).filter(
        models.InvitationToken.token == token
    ).first()
    
    if not inv_token:
        raise HTTPException(
            status_code=404,
            detail="Token d'invitation invalide"
        )
    
    if inv_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=410,
            detail="Token d'invitation expiré"
        )
    
    if inv_token.used:
        raise HTTPException(
            status_code=409,
            detail="Compte déjà créé avec ce token"
        )
    
    body = await request.json()
    
    # Vérifier email pas déjà utilisé
    existing = db.query(models.User).filter(
        models.User.email == inv_token.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email déjà utilisé"
        )
    
    # Créer utilisateur
    user = models.User(
        email=inv_token.email,
        name=body.get("name", ""),
        password=get_password_hash(body.get("password", "")),
        occupation=body.get("occupation", "etudiant"),
        institution=body.get("institution", ""),
        level=body.get("level", ""),
        domain=body.get("domain", ""),
        motivation=body.get("motivation", ""),
        role="membre",
        suspended=False,
    )
    db.add(user)
    
    # Marquer token comme utilisé
    inv_token.used = True
    inv_token.used_at = datetime.utcnow()
    
    db.commit()
    
    # TODO: Send welcome email to user
    
    return {
        "detail": "Compte créé avec succès",
        "email": inv_token.email,
        "message": "Vous pouvez maintenant vous connecter avec vos identifiants"
    }


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN USERS COMPATIBILITY (Missing endpoints)
# ═════════════════════════════════════════════════════════════════════════════

@router.put("/api/users/{email}/validate")
async def validate_user_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Validate user — Maps to /api/admin/users/{mailer}/validate"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.validated = True
    db.commit()
    return {"message": f"Utilisateur {user.name} validé", "validated": True}


@router.put("/api/users/{email}/reject")
async def reject_user_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject (delete) pending user — supprime un utilisateur en attente"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user_name = user.name
    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user_name} rejeté et supprimé"}


@router.put("/api/users/{email}/suspend")
async def suspend_user_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Suspend user — Maps to /api/admin/users/{mailer}/suspend"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.suspended = True
    db.commit()
    return {"message": f"Utilisateur {user.name} suspendu", "suspended": True}


@router.put("/api/users/{email}/unsuspend")
async def unsuspend_user_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Unsuspend user — Maps to /api/admin/users/{mailer}/unsuspend"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    user.suspended = False
    db.commit()
    return {"message": f"Utilisateur {user.name} réactivé", "suspended": False}


@router.delete("/api/users/{email}")
async def delete_user_compat(
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete user — Maps to /api/admin/users/{mailer}"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Supprimer les sessions de l'utilisateur d'abord
    db.query(models.Session).filter(models.Session.user_mailer == email).delete()
    user_name = user.name
    db.delete(user)
    db.commit()
    return {"message": f"Utilisateur {user_name} supprimé"}


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN ACTIVITIES COMPATIBILITY (Missing endpoints)
# ═════════════════════════════════════════════════════════════════════════════

@router.put("/api/activities/{activity_id}/validate")
async def validate_activity_compat(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Validate activity — Maps to /api/admin/activities/{id}/validate"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    activity.status = "approuvé"
    db.commit()
    return {"message": f"Activité '{activity.name_activity}' validée", "status": "approuvé"}


@router.put("/api/activities/{activity_id}/reject")
async def reject_activity_compat(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject activity — Maps to /api/admin/activities/{id}/reject"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    activity.status = "rejeté"
    db.commit()
    return {"message": f"Activité '{activity.name_activity}' rejetée", "status": "rejeté"}


@router.delete("/api/activities/{activity_id}")
async def delete_activity_compat(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete activity — Maps to /api/admin/activities/{id}"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    activity_id_str = activity.id_activity
    db.delete(activity)
    db.commit()
    return {"message": f"Activité '{activity_id_str}' supprimée"}


@router.post("/api/activities/{activity_id}/invite/{email}")
async def invite_to_activity_compat(
    activity_id: str,
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Invite user to activity — Maps to /api/admin/activities/{id}/invite/{mailer}"""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Vérifier activité existe
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    # Vérifier utilisateur existe
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier pas déjà invité
    existing = db.query(models.Contribute).filter(
        models.Contribute.id_user == email,
        models.Contribute.id_activity == activity_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Utilisateur déjà invité à cette activité")
    
    # Créer contribution (invitation)
    contrib = models.Contribute(
        id_user=email,
        id_activity=activity_id,
        participation_status="pending",
        period=None,
    )
    db.add(contrib)
    db.commit()
    
    return {
        "message": f"Invitation envoyée à {user.name}",
        "user_email": email,
        "activity_id": activity_id,
        "participation_status": "pending"
    }


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN APPROVALS & DELETIONS (Compatibility)
# ═════════════════════════════════════════════════════════════════════════════

# Profile Modification Approval & Rejection
@router.put("/api/admin/profile-modification/{mod_id}/approve")
async def approve_profile_mod(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve profile modification."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    mod = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.id == mod_id
    ).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    user = db.query(models.User).filter(models.User.email == mod.user_email).first()
    if user:
        setattr(user, mod.field_name, mod.new_value)
    
    mod.request_status = "approved"
    db.commit()
    return {"message": "Modification approuvée"}


@router.put("/api/admin/profile-modification/{mod_id}/reject")
async def reject_profile_mod(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject profile modification."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    mod = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.id == mod_id
    ).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    mod.request_status = "rejected"
    db.commit()
    return {"message": "Modification rejetée"}


# Question Approval & Rejection & Deletion
@router.put("/api/admin/questions/{question_id}/approve")
async def approve_question_compat(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve question."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    q = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    q.visibility = "approved"
    db.commit()
    return {"message": "Question approuvée"}


@router.put("/api/admin/questions/{question_id}/reject")
async def reject_question_compat(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject question."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    q = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    q.visibility = "rejected"
    db.commit()
    return {"message": "Question rejetée"}


@router.delete("/api/admin/questions/{question_id}")
async def delete_question_compat(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete question."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    q = db.query(models.Question).filter(models.Question.id_question == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    # Supprimer les réponses
    db.query(models.Response).filter(models.Response.id_question == question_id).delete()
    db.delete(q)
    db.commit()
    return {"message": "Question supprimée"}


# Suggestion Approval & Rejection & Deletion
@router.put("/api/admin/suggestions/{suggestion_id}/approve")
async def approve_suggestion_compat(
    suggestion_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve suggestion."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    s = db.query(models.Sugestion).filter(models.Sugestion.id_suggest == suggestion_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    s.visibility = "approved"
    db.commit()
    return {"message": "Suggestion approuvée"}


@router.put("/api/admin/suggestions/{suggestion_id}/reject")
async def reject_suggestion_compat(
    suggestion_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject suggestion."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    s = db.query(models.Sugestion).filter(models.Sugestion.id_suggest == suggestion_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    s.visibility = "rejected"
    db.commit()
    return {"message": "Suggestion rejetée"}


@router.delete("/api/admin/suggestions/{suggestion_id}")
async def delete_suggestion_compat(
    suggestion_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete suggestion."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    s = db.query(models.Sugestion).filter(models.Sugestion.id_suggest == suggestion_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    db.delete(s)
    db.commit()
    return {"message": "Suggestion supprimée"}


# Activity Approval & Rejection & Deletion
@router.put("/api/admin/activities/{activity_id}/approve")
async def approve_activity_compat(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve activity."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    a = db.query(models.Activity).filter(models.Activity.id_activity == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    a.user_approval_status = "approved"
    db.commit()
    return {"message": "Activité approuvée"}


@router.put("/api/admin/activities/{activity_id}/reject")
async def reject_activity_compat(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Reject activity."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    a = db.query(models.Activity).filter(models.Activity.id_activity == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activité non trouvée")
    
    a.user_approval_status = "rejected"
    db.commit()
    return {"message": "Activité rejetée"}


# Event Deletion
@router.delete("/api/admin/events/{event_id}")
async def delete_event_compat(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete event."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    e = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    db.delete(e)
    db.commit()
    return {"message": "Événement supprimé"}


# Contact Deletion
@router.delete("/api/contact/{contact_id}")
async def delete_contact_compat(
    contact_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Delete contact request."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    c = db.query(models.ContactRequest).filter(models.ContactRequest.id == contact_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    db.delete(c)
    db.commit()
    return {"message": "Message de contact supprimé"}


# ═════════════════════════════════════════════════════════════════════════════
# ADMIN USER CREATION
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/api/admin/users/create")
async def create_admin_user_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Create a new user with auto-generated credentials."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token, models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    body = await request.json()
    
    import string
    import secrets
    
    # Get name from body
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Le nom est requis")
    
    # Generate email from name
    base_email = name.lower().replace(" ", ".")
    email = f"{base_email}@betalab.local"
    counter = 1
    
    # Avoid duplicate emails
    while db.query(models.User).filter(models.User.email == email).first():
        email = f"{base_email}{counter}@betalab.local"
        counter += 1
    
    # Generate temporary password
    default_password = "".join(
        secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
        for _ in range(10)
    )
    
    # Create user
    user = models.User(
        email=email,
        name=name,
        birthdate=datetime.utcnow().date(),
        occupation="Non spécifié",
        institution="Non spécifié",
        level="",
        domain="",
        password=get_password_hash(default_password),
        motivation="",
        validated=False,
        suspended=False,
        role="membre",
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Utilisateur {name} créé avec succès",
        "email": email,
        "password": default_password,
        "username": email,
        "user": {
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "validated": user.validated,
        }
    }


# ═════════════════════════════════════════════════════════════════════════════
# DISCOVERY & PARTICIPATION (ALL)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/api/activities/all")
async def list_all_activities_discovery(db: Session = Depends(get_db)):
    """List all approved activities for user discovery."""
    return db.query(models.Activity).filter(
        models.Activity.status == "approved"
    ).all()


@router.get("/api/events/all")
async def list_all_events_discovery(db: Session = Depends(get_db)):
    """List all events for user discovery."""
    return db.query(models.Event).all()


@router.post("/api/activities/{activity_id}/request")
async def request_activity_participation(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """User: Request to join an activity."""
    token = request.cookies.get("session_token")
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Check if already participating or pending
    existing = db.query(models.Contribute).filter(
        models.Contribute.id_user == user.email,
        models.Contribute.id_activity == activity_id
    ).first()
    if existing:
        return {"message": "Demande déjà envoyée ou participation active", "status": existing.participation_status}
    
    contrib = models.Contribute(
        id_user=user.email,
        id_activity=activity_id,
        participation_status="pending",
    )
    db.add(contrib)
    db.commit()
    return {"message": "Demande de participation envoyée", "status": "pending"}


@router.post("/api/events/{event_id}/request")
async def request_event_participation(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """User: Request to join an event."""
    token = request.cookies.get("session_token")
    user = SessionManager.get_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    existing = db.query(models.EventParticipate).filter(
        models.EventParticipate.id_user == user.email,
        models.EventParticipate.id_event == event_id
    ).first()
    if existing:
        return {"message": "Demande déjà envoyée ou participation active", "status": existing.status}
    
    part = models.EventParticipate(
        id_user=user.email,
        id_event=event_id,
        status="pending",
    )
    db.add(part)
    db.commit()
    return {"message": "Demande de participation envoyée", "status": "pending"}


@router.put("/api/admin/profile/update")
async def update_admin_profile_compat(
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Update own profile."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Accès admin requis")
    
    try:
        data = await request.json()
        
        # Get current admin user (assuming admin email is stored in session or hardcoded)
        admin_email = "admin"  # This should be dynamic based on your admin system
        
        # Update admin user in database
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        
        # Update fields if provided
        if "name" in data and data["name"]:
            admin_user.name = data["name"]
        if "firstname" in data and data["firstname"]:
            admin_user.firstname = data["firstname"]
        if "email" in data and data["email"] and data["email"] != admin_email:
            # Check if new email already exists
            existing = db.query(models.User).filter(models.User.email == data["email"]).first()
            if existing:
                raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
            admin_user.email = data["email"]
        if "phone" in data and data["phone"]:
            admin_user.phone = data["phone"]
        
        # Update password if provided
        if "password" in data and data["password"] and data["password"].strip():
            if "confirmPassword" not in data or data["password"] != data["confirmPassword"]:
                raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas")
            
            # Hash new password
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
            admin_user.password = pwd_context.hash(data["password"])
        
        db.commit()
        
        return {"message": "Profil mis à jour avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/events/{event_id}/invite/{email}")
async def invite_to_event_compat(
    event_id: int,
    email: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Invite user to event."""
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Accès admin requis")
    
    existing = db.query(models.EventParticipate).filter(
        models.EventParticipate.id_user == email,
        models.EventParticipate.id_event == event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Utilisateur déjà invité")
    
    part = models.EventParticipate(
        id_user=email,
        id_event=event_id,
        status="pending",
    )
    db.add(part)
    db.commit()
    return {"message": f"Invitation envoyée à {email}"}


@router.put("/api/admin/contributions/{activity_id}/{email}/{action}")
async def approve_contribution_compat(
    activity_id: str,
    email: str,
    action: str, # approve | reject
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve or reject participation request."""
    # Auth check
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Accès admin requis")
    
    contrib = db.query(models.Contribute).filter(
        models.Contribute.id_user == email,
        models.Contribute.id_activity == activity_id
    ).first()
    
    if not contrib:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    
    if action == "approve":
        contrib.participation_status = "accepted"
        contrib.period = datetime.utcnow().date()
    else:
        contrib.participation_status = "refused"
    
    db.commit()
    return {"message": f"Participation {action}ée"}


@router.put("/api/admin/events/participations/{event_id}/{email}/{action}")
async def approve_event_participation_compat(
    event_id: int,
    email: str,
    action: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: Approve or reject event participation request."""
    # Auth check
    token = request.cookies.get("session_token")
    session = db.query(models.Session).filter(
        models.Session.token == token,
        models.Session.session_type == "admin"
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Accès admin requis")
    
    part = db.query(models.EventParticipate).filter(
        models.EventParticipate.id_user == email,
        models.EventParticipate.id_event == event_id
    ).first()
    
    if not part:
        raise HTTPException(status_code=404, detail="Demande introuvable")
    
    if action == "approve":
        part.status = "accepted"
    else:
        part.status = "rejected"
    
    db.commit()
    return {"message": f"Participation {action}ée"}

