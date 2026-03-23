"""Schémas Pydantic — BetaLab."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ══════════════════════════════════════════════════════════════════════════════
# USER
# ══════════════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    mailer: EmailStr; name: str; birthdate: str; password: str
    occupation: str; institution: str; level: str; domain: str; motivation: str

class UserUpdate(BaseModel):
    """Champs modifiables par l'utilisateur lui-même."""
    name:        Optional[str] = None
    occupation:  Optional[str] = None
    institution: Optional[str] = None
    level:       Optional[str] = None
    domain:      Optional[str] = None
    motivation:  Optional[str] = None

class AdminUserUpdate(BaseModel):
    """Champs modifiables par l'admin (inclut validated, suspended, role)."""
    name:        Optional[str]  = None
    occupation:  Optional[str]  = None
    institution: Optional[str]  = None
    level:       Optional[str]  = None
    domain:      Optional[str]  = None
    motivation:  Optional[str]  = None
    validated:   Optional[bool] = None
    suspended:   Optional[bool] = None
    role:        Optional[str]  = None

class RoleUpdate(BaseModel):
    role: str  # membre | chercheur | responsable | admin

class UserLogin(BaseModel):
    mailer: EmailStr; password: str

class UserResponse(BaseModel):
    mailer:       EmailStr
    name:        str
    birthdate:   Optional[date] = None
    occupation:  str
    institution: Optional[str]  = None
    level:       Optional[str]  = None
    domain:      Optional[str]  = None
    motivation:  Optional[str]  = None
    validated:   Optional[bool] = False
    suspended:   Optional[bool] = False
    role:        Optional[str]  = "membre"

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# ACTIVITY
# ══════════════════════════════════════════════════════════════════════════════

class ActivityCreate(BaseModel):
    id_activity:    str
    name_activity:  str
    description:    Optional[str] = None
    class_activity: Optional[str] = None
    status:         Optional[str] = "en attente"

class ActivityResponse(BaseModel):
    id_activity:         str
    name_activity:       str
    description:         Optional[str] = None
    status:              Optional[str] = None
    class_activity:      Optional[str] = None
    created_by:          Optional[str] = None
    user_approval_status: Optional[str] = "approved"
    reviewed_at:         Optional[datetime] = None
    reviewed_by:         Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# EVENT
# ══════════════════════════════════════════════════════════════════════════════

class EventCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    event_date:  Optional[date] = None
    location:    Optional[str] = None
    event_type:  Optional[str] = "événement"

class EventResponse(BaseModel):
    id:          int
    title:       str
    description: Optional[str] = None
    event_date:  Optional[date] = None
    location:    Optional[str] = None
    event_type:  Optional[str] = None
    created_by:  Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# QUESTION & RESPONSE
# ══════════════════════════════════════════════════════════════════════════════

class QuestionCreate(BaseModel):
    libele_question:      str
    description_question: Optional[str] = None

class QuestionResponse(BaseModel):
    id_question:          int
    libele_question:      str
    description_question: Optional[str] = None
    id_user:              Optional[str] = None
    visibility:           Optional[str] = "pending"
    created_at:           Optional[datetime] = None
    reviewed_at:          Optional[datetime] = None
    reviewed_by:          Optional[str] = None
    responses:            List["AnswerResponse"] = []

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    libelle_response:     str
    description_response: Optional[str] = None

class AnswerResponse(BaseModel):
    id_response:          int
    libelle_response:     str
    description_response: Optional[str] = None
    id_question:          Optional[int] = None

    class Config:
        from_attributes = True

# Résolution forward-ref
QuestionResponse.model_rebuild()


# ══════════════════════════════════════════════════════════════════════════════
# SUGGESTION
# ══════════════════════════════════════════════════════════════════════════════

class SuggestionCreate(BaseModel):
    libele:              str
    description_suggest: Optional[str] = None
    note:                Optional[int] = None

class SuggestionResponse(BaseModel):
    id_suggest:          int
    libele:              str
    description_suggest: Optional[str] = None
    note:                Optional[int] = None
    id_user:             Optional[str] = None
    visibility:          Optional[str] = "pending"
    created_at:          Optional[datetime] = None
    reviewed_at:         Optional[datetime] = None
    reviewed_by:         Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# CONTRIBUTION
# ══════════════════════════════════════════════════════════════════════════════

class ContributionResponse(BaseModel):
    user_name:            Optional[str] = None
    user_mailer:           Optional[str] = None
    id_activity:          str
    name_activity:        str
    class_activity:       Optional[str] = None
    participation_status: str
    approval_status:      Optional[str] = "auto_approved"
    period:               Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

class ContactRequestCreate(BaseModel):
    """Données soumises par l'utilisateur via le formulaire de contact."""
    name: str
    email: EmailStr
    subject: str
    message: str

class ContactRequestResponse(BaseModel):
    """Réponse après soumission d'une demande de contact."""
    id: int
    name: str
    email: str
    subject: str
    message: str
    is_join_request: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdhesionForm(BaseModel):
    """Formulaire d'adhésion soumis après invitation."""
    name: str
    email: EmailStr
    birthdate: str  # format YYYY-MM-DD
    occupation: str
    institution: str
    level: Optional[str] = None
    domain: Optional[str] = None
    motivation: Optional[str] = None
    password: str

class AdhesionResponse(BaseModel):
    """Réponse après soumission du formulaire d'adhésion."""
    mailer: str
    name: str
    message: str

class InvitationTokenResponse(BaseModel):
    """Réponse après vérification d'un token d'invitation."""
    valid: bool
    mailer: str


# ══════════════════════════════════════════════════════════════════════════════
# APPROVAL WORKFLOW - PROFILE MODIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

class ProfileModificationRequestCreate(BaseModel):
    """User requests profile field modification."""
    field: str
    value: str


class ProfileModificationRequestResponse(BaseModel):
    """Admin/User view of profile modification request."""
    id: int
    user_email: str
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    request_status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# APPROVAL WORKFLOW - ACTIVITY MODIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

class ActivityModificationRequestCreate(BaseModel):
    """User requests activity field modification."""
    field: str
    value: str


class ActivityModificationRequestResponse(BaseModel):
    """Admin/User view of activity modification request."""
    id: int
    activity_id: str
    user_email: str
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    request_status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# APPROVAL WORKFLOW - ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

class PendingApprovalsResponse(BaseModel):
    """All pending items requiring admin approval."""
    profile_modifications: List[dict] = []
    pending_questions: List[dict] = []
    pending_suggestions: List[dict] = []
    pending_activities: List[dict] = []
    pending_contributions: List[dict] = []
    counts: dict


class UserSubmissionsStatusResponse(BaseModel):
    """Count of user's pending submissions."""
    profile_changes: int = 0
    questions_pending: int = 0
    suggestions_pending: int = 0
    activities_pending: int = 0
    participations_pending: int = 0
    total: int = 0
    name: str