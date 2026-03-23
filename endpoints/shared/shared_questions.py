"""
Questions (Partagé) — BetaLab
Endpoints:
  POST   /api/questions                    → user: poser question
  GET    /api/questions/user/{mailer}      → user: ses questions
  GET    /api/questions                    → admin: toutes les questions
  POST   /api/questions/{id}/answer        → admin: répondre question
  GET    /api/questions/{id}/responses     → voir réponses
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional, List

import models, schemas
from database import get_db
from dependencies import sessions

router = APIRouter(tags=["Questions"])


@router.post("/api/questions", response_model=schemas.QuestionResponse)
async def create_question(
    data: schemas.QuestionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Poser une question (utilisateur connecté)."""
    token = request.cookies.get("session_token")
    
    if not token or token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    
    user_email = sessions[token]
    
    question = models.Question(
        libele_question=data.libele_question,
        description_question=data.description_question,
        id_user=user_email,
        visibility="pending",  # NEW: Set to pending for admin approval
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question


@router.get("/api/questions/user/{user_mailer}", response_model=List[schemas.QuestionResponse])
async def get_user_questions(
    user_mailer: str,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """Récupère les questions d'un utilisateur."""
    questions = db.query(models.Question).filter(
        models.Question.id_user == user_mailer
    ).order_by(models.Question.id_question.desc()).all()
    
    return questions


@router.get("/api/questions", response_model=List[schemas.QuestionResponse])
async def list_all_questions(
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: lister toutes les questions (approved + pending)."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Admin sees ALL questions (pending + approved + rejected)
    return db.query(models.Question).order_by(
        models.Question.id_question.desc()
    ).all()


@router.post("/api/questions/{question_id}/answer", response_model=schemas.AnswerResponse)
async def answer_question(
    question_id: int,
    data: schemas.AnswerCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: répondre à une question."""
    from endpoints.admin.admin_auth import admin_sessions
    from datetime import datetime
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    admin_email = admin_sessions[token]  # Get admin email from session
    
    q = db.query(models.Question).filter(
        models.Question.id_question == question_id
    ).first()
    
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    # NEW: Auto-approve question when admin responds
    q.visibility = "approved"
    q.reviewed_at = datetime.utcnow()
    q.reviewed_by = admin_email
    
    response = models.Response(
        libelle_response=data.libelle_response,
        description_response=data.description_response,
        id_question=question_id,
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    
    # Send notification email to user about approval
    try:
        from email_service import send_question_answered_notification
        user = db.query(models.User).filter(models.User.email == q.id_user).first()
        send_question_answered_notification(
            to_email=q.id_user,
            to_name=user.name if user else q.id_user,
            question_text=q.libele_question,
            answer_text=data.libelle_response
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send notification: {e}")
    
    return response


@router.get("/api/questions/{question_id}/responses")
async def get_question_responses(
    question_id: int,
    db: Session = Depends(get_db),
):
    """Récupère les réponses d'une question."""
    q = db.query(models.Question).filter(
        models.Question.id_question == question_id
    ).first()
    
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    return {
        "question_id": q.id_question,
        "question": q.libele_question,
        "description": q.description_question,
        "user": q.id_user,
        "responses": [
            {
                "id_response": r.id_response,
                "libelle": r.libelle_response,
                "description": r.description_response,
            }
            for r in q.responses
        ]
    }


@router.delete("/api/admin/questions/{question_id}")
async def delete_question(
    question_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Admin: supprimer une question."""
    from endpoints.admin.admin_auth import admin_sessions
    
    token = request.cookies.get("admin_token")
    if not token or token not in admin_sessions:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    q = db.query(models.Question).filter(
        models.Question.id_question == question_id
    ).first()
    
    if not q:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    # Supprimer les réponses si existentes
    db.query(models.Response).filter(
        models.Response.id_question == question_id
    ).delete()
    
    # Supprimer la question
    db.delete(q)
    db.commit()
    
    return {"message": "Question supprimée avec succès"}
