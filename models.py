"""
Modèles SQLAlchemy — BetaLab.
Nouveautés :
  - User.role         : rôle attribué par l'admin (membre | chercheur | responsable | admin)
  - Event             : événements créés par l'admin
  - Contribute.participation_status : pending | accepted | refused
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean, Text
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    email        = Column(String(100), unique=True, primary_key=True, index=True)
    name         = Column(String(255), index=True)
    birthdate    = Column(Date,        index=True)
    occupation   = Column(String(50),  index=True)
    institution  = Column(String(255), index=True)
    level        = Column(String(20),  index=True)
    domain       = Column(String(255), index=True)
    password     = Column(String(255))
    motivation   = Column(Text)
    validated    = Column(Boolean, default=False, nullable=False)
    suspended    = Column(Boolean, default=False, nullable=False)
    # rôle attribué par l'admin
    role         = Column(String(50), default="membre", nullable=False)

    contributes = relationship("Contribute", back_populates="user",  cascade="all, delete-orphan")
    suggestions = relationship("Sugestion",  back_populates="user", foreign_keys="Sugestion.id_user", cascade="all, delete-orphan")
    questions   = relationship("Question",   back_populates="user", foreign_keys="Question.id_user", cascade="all, delete-orphan")
    statuts     = relationship("Status",     back_populates="user",  cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"
    id_activity    = Column(String(20),  primary_key=True, index=True)
    name_activity  = Column(String(100), index=True)
    description    = Column(Text)
    status         = Column(String(50),  index=True, default="en attente")
    class_activity = Column(String(100), index=True)
    # User creation & approval workflow columns
    created_by           = Column(String(100), nullable=True)
    user_approval_status = Column(String(30), default="approved", nullable=False)  # pending_submission, approved, rejected
    reviewed_at          = Column(DateTime, nullable=True)
    reviewed_by          = Column(String(100), nullable=True)

    contributes = relationship("Contribute", back_populates="activity")


class Event(Base):
    """
    Événements créés par l'administrateur (conférences, hackathons, ateliers…).
    """
    __tablename__ = "events"
    id          = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text)
    event_date  = Column(Date)
    location    = Column(String(255))
    event_type  = Column(String(100), default="événement")
    created_by  = Column(String(100))

    participations = relationship("EventParticipate", back_populates="event", cascade="all, delete-orphan")


class EventParticipate(Base):
    """
    Table de jointure entre User et Event pour gérer les inscriptions.
    """
    __tablename__ = "event_participate"
    id_user              = Column(String(100), ForeignKey("users.email"), primary_key=True, index=True)
    id_event             = Column(Integer,    ForeignKey("events.id"),     primary_key=True, index=True)
    # status: pending | accepted | rejected
    status               = Column(String(20),  default="pending", nullable=False)
    created_at           = Column(DateTime,    default=datetime.utcnow)
    
    user  = relationship("User",  foreign_keys=[id_user])
    event = relationship("Event", back_populates="participations")


class Status(Base):
    __tablename__ = "statuts"
    id_status          = Column(String(50),  primary_key=True, index=True)
    name_status        = Column(String(100), index=True)
    description_status = Column(String(255), index=True)
    user_id            = Column(String(100), ForeignKey("users.email"), index=True)
    user = relationship("User", back_populates="statuts")


class Question(Base):
    __tablename__ = "questions"
    id_question          = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    libele_question      = Column(String(255), index=True)
    description_question = Column(Text)
    id_user              = Column(String(100), ForeignKey("users.email"), index=True)
    # Approval workflow columns
    visibility           = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    reviewed_at          = Column(DateTime, nullable=True)
    reviewed_by          = Column(String(100), ForeignKey("users.email"), nullable=True)
    created_at           = Column(DateTime, default=datetime.utcnow)
    
    user      = relationship("User",     back_populates="questions", foreign_keys=[id_user])
    reviewer  = relationship("User",     foreign_keys=[reviewed_by])
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")


class Sugestion(Base):
    __tablename__ = "suggestions"
    id_suggest          = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    libele              = Column(String(255), index=True)
    description_suggest = Column(Text)
    note                = Column(Integer,    index=True)
    id_user             = Column(String(100), ForeignKey("users.email"), index=True)
    # Approval workflow columns
    visibility          = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    reviewed_at         = Column(DateTime, nullable=True)
    reviewed_by         = Column(String(100), ForeignKey("users.email"), nullable=True)
    created_at          = Column(DateTime, default=datetime.utcnow)
    
    user     = relationship("User", back_populates="suggestions", foreign_keys=[id_user])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class ProfileModificationRequest(Base):
    """Request for user profile modification requiring admin approval."""
    __tablename__ = "profile_modification_request"
    id            = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    user_email    = Column(String(100), ForeignKey("users.email"), nullable=False, index=True)
    field_name    = Column(String(50),  nullable=False)
    old_value     = Column(Text)
    new_value     = Column(Text)
    request_status = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    created_at    = Column(DateTime, default=datetime.utcnow)
    reviewed_at   = Column(DateTime, nullable=True)
    reviewed_by   = Column(String(100), ForeignKey("users.email"), nullable=True)
    admin_notes   = Column(Text)
    
    user    = relationship("User", foreign_keys=[user_email])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class ActivityModificationRequest(Base):
    """Request for activity modification requiring admin approval."""
    __tablename__ = "activity_modification_request"
    id            = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    activity_id   = Column(String(20), ForeignKey("activities.id_activity"), nullable=False, index=True)
    user_email    = Column(String(100), ForeignKey("users.email"), nullable=False, index=True)
    field_name    = Column(String(50),  nullable=False)
    old_value     = Column(Text)
    new_value     = Column(Text)
    request_status = Column(String(20), default="pending", nullable=False)  # pending, approved, rejected
    created_at    = Column(DateTime, default=datetime.utcnow)
    reviewed_at   = Column(DateTime, nullable=True)
    reviewed_by   = Column(String(100), ForeignKey("users.email"), nullable=True)
    admin_notes   = Column(Text)
    
    activity = relationship("Activity", foreign_keys=[activity_id])
    user     = relationship("User", foreign_keys=[user_email])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


class Response(Base):
    """Réponse d'un admin à une question."""
    __tablename__ = "responses"
    id_response          = Column(Integer,    primary_key=True, index=True, autoincrement=True)
    libelle_response     = Column(String(255), index=True)
    description_response = Column(Text)
    id_question          = Column(Integer, ForeignKey("questions.id_question"), index=True)
    question = relationship("Question", back_populates="responses")


class Contribute(Base):
    """
    Liaison User ↔ Activity.
    participation_status : pending | accepted | refused
    approval_status : auto_approved | pending_admin_approval | approved | rejected

    ⚠️  Si la table existe déjà :
        ALTER TABLE contributes
          ADD COLUMN participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted';
        ALTER TABLE contributes
          ADD COLUMN approval_status VARCHAR(30) DEFAULT 'auto_approved';
    """
    __tablename__ = "contributes"
    id_user              = Column(String(100), ForeignKey("users.email"),            primary_key=True, index=True)
    id_activity          = Column(String(20),  ForeignKey("activities.id_activity"), primary_key=True, index=True)
    period               = Column(Date)
    participation_status = Column(String(20), default="accepted", nullable=False)  # pending, accepted, refused
    approval_status      = Column(String(30), default="auto_approved", nullable=False)  # auto_approved, pending_admin_approval, approved, rejected

    user     = relationship("User",     back_populates="contributes")
    activity = relationship("Activity", back_populates="contributes")

# ─────────────────────────────────────────────────────────────────────────────
# Contact & Adhésion Models
# ─────────────────────────────────────────────────────────────────────────────

class ContactRequest(Base):
    __tablename__ = "contact_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_join_request = Column(Boolean, default=False)
    status = Column(String(50), default="nouveau")  # nouveau, lu, invité, traité
    created_at = Column(DateTime, default=datetime.utcnow)

class InvitationToken(Base):
    __tablename__ = "invitation_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(100), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    name = Column(String(100), nullable=False)
    used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    contact_id = Column(Integer, ForeignKey("contact_requests.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────────────────────────────────────────
# Sessions Persistantes
# ─────────────────────────────────────────────────────────────────────────────

class Session(Base):
    """Sessions utilisateur persistantes en BD (au lieu de mémoire)."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(256), unique=True, nullable=False, index=True)
    user_mailer = Column(String(100), ForeignKey("users.email"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    session_type = Column(String(20), default="user")  # "user" ou "admin"
    user_agent = Column(String(255))  # Pour audit/sécurité
    ip_address = Column(String(45))   # IPv4 ou IPv6
    
    user = relationship("User", foreign_keys=[user_mailer])

# ─────────────────────────────────────────────────────────────────────────────
# Utilisateurs Admin
# ─────────────────────────────────────────────────────────────────────────────

class AdminUser(Base):
    """Utilisateurs avec accès admin (au lieu de hardcoded)."""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Hashé
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(50), default="admin")  # admin | moderator | viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

# ─────────────────────────────────────────────────────────────────────────────
# CSRF Tokens
# ─────────────────────────────────────────────────────────────────────────────

class CSRFToken(Base):
    """Tokens CSRF pour protection des formulaires."""
    __tablename__ = "csrf_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(256), unique=True, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)