"""
Admin endpoints for reviewing and approving/rejecting user requests.
Central approval queue for all user actions requiring admin validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from session_manager import SessionManager
from admin_auth import AdminAuthManager
import models
import schemas

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Verify Admin Authentication
# ══════════════════════════════════════════════════════════════════════════════

def verify_admin(request: Request, db: Session):
    """Verify admin token and return admin email."""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Admin not authenticated")
    
    # Vérifier la session en BD
    session = SessionManager.get_session(db, token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Vérifier que c'est une session admin (préfixe admin_)
    if not session.user_mailer.startswith("admin_"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Extraire le username admin
    admin_username = session.user_mailer.replace("admin_", "")
    
    # Vérifier que l'admin existe et est actif
    admin = AdminAuthManager.get_admin_by_username(db, admin_username)
    if not admin or not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account not found or inactive")
    
    return admin.email


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Get All Pending Approvals
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/api/admin/pending-approvals", response_model=schemas.PendingApprovalsResponse)
async def get_all_pending_approvals(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get all pending items requiring admin approval.
    This is the main admin dashboard widget showing approval queue.
    """
    admin_email = verify_admin(request, db)
    
    # Profile modifications
    profile_mods = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.request_status == "pending"
    ).order_by(models.ProfileModificationRequest.created_at.desc()).all()
    
    # Questions pending approval
    questions = db.query(models.Question).filter(
        models.Question.visibility == "pending"
    ).order_by(models.Question.created_at.desc()).all()
    
    # Suggestions pending approval
    suggestions = db.query(models.Sugestion).filter(
        models.Sugestion.visibility == "pending"
    ).order_by(models.Sugestion.created_at.desc()).all()
    
    # Activities created by users (not yet approved)
    activities = db.query(models.Activity).filter(
        models.Activity.user_approval_status == "pending_submission"
    ).order_by(models.Activity.id_activity).all()
    
    # Activity modifications pending approval
    activity_mods = db.query(models.ActivityModificationRequest).filter(
        models.ActivityModificationRequest.request_status == "pending"
    ).order_by(models.ActivityModificationRequest.created_at.desc()).all()
    
    # Contributions pending admin approval (user accepted invitation)
    contributions = db.query(models.Contribute).filter(
        models.Contribute.approval_status == "pending_admin_approval"
    ).all()
    
    return schemas.PendingApprovalsResponse(
        profile_modifications=[
            {
                "id": m.id,
                "user_email": m.user_email,
                "field": m.field_name,
                "old_value": m.old_value,
                "new_value": m.new_value,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            } for m in profile_mods
        ],
        pending_questions=[
            {
                "id": q.id_question,
                "user": q.id_user,
                "title": q.libele_question,
                "description": q.description_question,
                "created_at": q.created_at.isoformat() if q.created_at else None,
            } for q in questions
        ],
        pending_suggestions=[
            {
                "id": s.id_suggest,
                "user": s.id_user,
                "title": s.libele,
                "description": s.description_suggest,
                "rating": s.note,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            } for s in suggestions
        ],
        pending_activities=[
            {
                "id": a.id_activity,
                "creator": a.created_by,
                "name": a.name_activity,
                "description": a.description,
                "class": a.class_activity,
            } for a in activities
        ],
        pending_contributions=[
            {
                "id": f"{c.id_user}_{c.id_activity}",
                "user": c.id_user,
                "activity": c.id_activity,
            } for c in contributions
        ],
        counts={
            "profile_modifications": len(profile_mods),
            "questions": len(questions),
            "suggestions": len(suggestions),
            "activities": len(activities) + len(activity_mods),
            "contributions": len(contributions),
            "total": len(profile_mods) + len(questions) + len(suggestions) + len(activities) + len(activity_mods) + len(contributions),
        }
    )


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Approve Profile Modification
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/profile-modification/{mod_id}/approve")
async def approve_profile_modification(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin approves a profile modification request.
    Modification is applied to user's profile and saved to database.
    """
    admin_email = verify_admin(request, db)
    
    mod = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.id == mod_id
    ).first()
    
    if not mod:
        raise HTTPException(status_code=404, detail="Modification request not found")
    
    if mod.request_status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")
    
    # Get user
    user = db.query(models.User).filter(models.User.email == mod.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Apply modification
    setattr(user, mod.field_name, mod.new_value)
    
    # Mark request as approved
    mod.request_status = "approved"
    mod.reviewed_at = datetime.utcnow()
    mod.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_profile_modification_approved_email
        send_profile_modification_approved_email(
            to_email=mod.user_email,
            to_name=user.name or mod.user_email,
            field_name=mod.field_name
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send approval email: {e}")
    
    return {
        "message": "Modification approved and applied",
        "user_email": mod.user_email,
        "field": mod.field_name,
        "new_value": mod.new_value,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Reject Profile Modification
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/profile-modification/{mod_id}/reject")
async def reject_profile_modification(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin rejects a profile modification request.
    User's profile is not modified.
    """
    admin_email = verify_admin(request, db)
    
    mod = db.query(models.ProfileModificationRequest).filter(
        models.ProfileModificationRequest.id == mod_id
    ).first()
    
    if not mod:
        raise HTTPException(status_code=404, detail="Modification request not found")
    
    mod.request_status = "rejected"
    mod.reviewed_at = datetime.utcnow()
    mod.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_profile_modification_rejected_email
        user = db.query(models.User).filter(models.User.email == mod.user_email).first()
        send_profile_modification_rejected_email(
            to_email=mod.user_email,
            to_name=user.name if user else mod.user_email,
            field_name=mod.field_name,
            admin_notes=mod.admin_notes
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
    
    return {"message": "Modification rejected"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Approve Question
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/questions/{question_id}/approve")
async def approve_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin approves a question.
    Question becomes visible to all users.
    """
    admin_email = verify_admin(request, db)
    
    question = db.query(models.Question).filter(
        models.Question.id_question == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question.visibility = "approved"
    question.reviewed_at = datetime.utcnow()
    question.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_question_approved_email
        user = db.query(models.User).filter(models.User.email == question.id_user).first()
        send_question_approved_email(
            to_email=question.id_user,
            to_name=user.name if user else question.id_user,
            question_text=question.libele_question
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send approval email: {e}")
    
    return {"message": "Question approved"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Reject Question
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/questions/{question_id}/reject")
async def reject_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin rejects a question.
    Question remains hidden.
    """
    admin_email = verify_admin(request, db)
    
    question = db.query(models.Question).filter(
        models.Question.id_question == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question.visibility = "rejected"
    question.reviewed_at = datetime.utcnow()
    question.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_question_rejected_email
        user = db.query(models.User).filter(models.User.email == question.id_user).first()
        send_question_rejected_email(
            to_email=question.id_user,
            to_name=user.name if user else question.id_user,
            question_text=question.libele_question
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
    
    return {"message": "Question rejected"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Approve Suggestion
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/suggestions/{suggestion_id}/approve")
async def approve_suggestion(
    suggestion_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin approves a suggestion.
    Suggestion becomes visible to all users.
    """
    admin_email = verify_admin(request, db)
    
    suggestion = db.query(models.Sugestion).filter(
        models.Sugestion.id_suggest == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.visibility = "approved"
    suggestion.reviewed_at = datetime.utcnow()
    suggestion.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_question_approved_email
        user = db.query(models.User).filter(models.User.email == suggestion.id_user).first()
        send_question_approved_email(
            to_email=suggestion.id_user,
            to_name=user.name if user else suggestion.id_user,
            question_text=suggestion.libele
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send approval email: {e}")
    
    return {"message": "Suggestion approved"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Reject Suggestion
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin rejects a suggestion.
    Suggestion remains hidden.
    """
    admin_email = verify_admin(request, db)
    
    suggestion = db.query(models.Sugestion).filter(
        models.Sugestion.id_suggest == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.visibility = "rejected"
    suggestion.reviewed_at = datetime.utcnow()
    suggestion.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_question_rejected_email
        user = db.query(models.User).filter(models.User.email == suggestion.id_user).first()
        send_question_rejected_email(
            to_email=suggestion.id_user,
            to_name=user.name if user else suggestion.id_user,
            question_text=suggestion.libele
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
    
    return {"message": "Suggestion rejected"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Approve User-Created Activity
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/activities/{activity_id}/approve")
async def approve_activity(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin approves a user-created activity.
    Activity becomes public and visible to all users.
    """
    admin_email = verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity.user_approval_status = "approved"
    activity.status = "approuvé"
    activity.reviewed_at = datetime.utcnow()
    activity.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to creator
    try:
        from email_service import send_activity_approved_email
        if activity.created_by:
            user = db.query(models.User).filter(models.User.email == activity.created_by).first()
            send_activity_approved_email(
                to_email=activity.created_by,
                to_name=user.name if user else activity.created_by,
                activity_name=activity.name_activity
            )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send approval email: {e}")
    
    return {"message": "Activity approved"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Reject User-Created Activity
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/activities/{activity_id}/reject")
async def reject_activity(
    activity_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin rejects a user-created activity.
    Activity remains hidden.
    """
    admin_email = verify_admin(request, db)
    
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity.user_approval_status = "rejected"
    activity.status = "rejeté"
    activity.reviewed_at = datetime.utcnow()
    activity.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to creator
    try:
        from email_service import send_activity_rejected_email
        if activity.created_by:
            user = db.query(models.User).filter(models.User.email == activity.created_by).first()
            send_activity_rejected_email(
                to_email=activity.created_by,
                to_name=user.name if user else activity.created_by,
                activity_name=activity.name_activity
            )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
    
    return {"message": "Activity rejected"}


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Approve Activity Modification
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/activity-modification/{mod_id}/approve")
async def approve_activity_modification(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin approves an activity modification request.
    Modification is applied to activity.
    """
    admin_email = verify_admin(request, db)
    
    mod = db.query(models.ActivityModificationRequest).filter(
        models.ActivityModificationRequest.id == mod_id
    ).first()
    
    if not mod:
        raise HTTPException(status_code=404, detail="Modification request not found")
    
    if mod.request_status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")
    
    # Get activity
    activity = db.query(models.Activity).filter(
        models.Activity.id_activity == mod.activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Apply modification
    setattr(activity, mod.field_name, mod.new_value)
    
    # Mark request as approved
    mod.request_status = "approved"
    mod.reviewed_at = datetime.utcnow()
    mod.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_activity_approved_email
        send_activity_approved_email(
            to_email=mod.user_email,
            to_name="User",
            activity_name=activity.name_activity
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send approval email: {e}")
    
    return {
        "message": "Modification approved and applied",
        "activity_id": mod.activity_id,
        "field": mod.field_name,
        "new_value": mod.new_value,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN: Reject Activity Modification
# ══════════════════════════════════════════════════════════════════════════════

@router.put("/api/admin/activity-modification/{mod_id}/reject")
async def reject_activity_modification(
    mod_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Admin rejects an activity modification request.
    Activity is not modified.
    """
    admin_email = verify_admin(request, db)
    
    mod = db.query(models.ActivityModificationRequest).filter(
        models.ActivityModificationRequest.id == mod_id
    ).first()
    
    if not mod:
        raise HTTPException(status_code=404, detail="Modification request not found")
    
    mod.request_status = "rejected"
    mod.reviewed_at = datetime.utcnow()
    mod.reviewed_by = admin_email
    
    db.commit()
    
    # Send email to user
    try:
        from email_service import send_activity_rejected_email
        activity = db.query(models.Activity).filter(
            models.Activity.id_activity == mod.activity_id
        ).first()
        send_activity_rejected_email(
            to_email=mod.user_email,
            to_name="User",
            activity_name=activity.name_activity if activity else "Activity",
            admin_notes=mod.admin_notes
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send rejection email: {e}")
    
    return {"message": "Modification rejected"}
