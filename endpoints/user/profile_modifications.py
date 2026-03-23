"""
Endpoints for user profile modification requests.
Users request changes to their profile, which are then reviewed and approved by admins.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from session_manager import SessionManager
import models
import schemas

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Verify User Authentication
# ══════════════════════════════════════════════════════════════════════════════

def verify_user(request: Request, db: Session):
    """Verify user token and return user email."""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Vérifier la session en BD
    session = SessionManager.get_session(db, token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Vérifier que ce n'est pas une session admin
    if session.user_mailer.startswith("admin_"):
        raise HTTPException(status_code=403, detail="User access required")
    
    return session.user_mailer


# ══════════════════════════════════════════════════════════════════════════════
# USER: Request Profile Modification
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/api/user/profile/request-modification", response_model=schemas.ProfileModificationRequestResponse)
async def request_profile_modification(
    data: schemas.ProfileModificationRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    User requests to modify a profile field.
    Modification is saved as pending and must be approved by admin before taking effect.
    """
    user_email = verify_user(request, db)
    
    # Validez field name
    allowed_fields = ["name", "occupation", "institution", "level", "domain", "motivation"]
    if data.field not in allowed_fields:
        raise HTTPException(status_code=400, detail=f"Cannot modify field: {data.field}")
    
    # Get current user
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get current value
    old_value = getattr(user, data.field, None)
    if str(old_value) == str(data.value):
        raise HTTPException(status_code=400, detail="No change detected")
    
    # Create modification request
    mod_request = models.ProfileModificationRequest(
        user_email=user_email,
        field_name=data.field,
        old_value=str(old_value) if old_value else None,
        new_value=data.value,
        request_status="pending",
        created_at=datetime.utcnow(),
    )
    
    db.add(mod_request)
    db.commit()
    
    # Send email to admin about new modification request
    try:
        from email_service import send_profile_modification_request_notification
        # Get admin email from database
        admin = db.query(models.AdminUser).filter(models.AdminUser.is_active == True).first()
        if admin:
            send_profile_modification_request_notification(
                to_admin_email=admin.email,
                user_name=user.name or user_email,
                user_email=user_email,
                field_name=data.field,
                old_value=str(old_value) if old_value else "—",
                new_value=data.value
            )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send notification: {e}")
    
    return mod_request


# ══════════════════════════════════════════════════════════════════════════════
# USER: Get Pending Profile Modification Requests
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/api/user/profile/pending-requests")
async def get_pending_profile_requests(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get all pending profile modification requests for the current user.
    User can see status of their requests (pending, approved, rejected).
    """
    user_email = verify_user(request, db)
    
    requests_list = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.user_email == user_email
    ).order_by(models.ProfileModificationRequest.created_at.desc()).all()
    
    return requests_list


# ══════════════════════════════════════════════════════════════════════════════
# USER: Get Submissions Status (Dashboard Widget)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/api/user/submissions-status", response_model=schemas.UserSubmissionsStatusResponse)
async def get_submissions_status(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get count of all pending submissions/requests for the current user.
    Used to show badges on dashboard tabs.
    """
    user_email = verify_user(request, db)
    
    # Count pending profile modifications
    profile_count = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.user_email == user_email,
        models.ProfileModificationRequest.request_status == "pending"
    ).count()
    
    # Count pending questions (visibility=pending means draft)
    questions_count = db.query(models.Question).filter(
        models.Question.id_user == user_email,
        models.Question.visibility == "pending"
    ).count()
    
    # Count pending suggestions (visibility=pending means draft)
    suggestions_count = db.query(models.Sugestion).filter(
        models.Sugestion.id_user == user_email,
        models.Sugestion.visibility == "pending"
    ).count()
    
    # Count pending activities created by user (user_approval_status=pending_submission)
    activities_count = db.query(models.Activity).filter(
        models.Activity.created_by == user_email,
        models.Activity.user_approval_status == "pending_submission"
    ).count()
    
    # Count pending activity modifications
    activity_mods_count = db.query(models.ActivityModificationRequest).filter(
        models.ActivityModificationRequest.user_email == user_email,
        models.ActivityModificationRequest.request_status == "pending"
    ).count()
    
    total = profile_count + questions_count + suggestions_count + activities_count + activity_mods_count
    
    return schemas.UserSubmissionsStatusResponse(
        profile_changes=profile_count,
        questions_pending=questions_count,
        suggestions_pending=suggestions_count,
        activities_pending=activities_count + activity_mods_count,
        participations_pending=0,  # Auto-approved when user accepts admin invitation
        total=total,
    )
