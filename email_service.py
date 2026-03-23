"""
Utilitaire d'envoi d'emails — BetaLab.

Variables d'environnement requises dans .env :
  SMTP_HOST      = smtp.gmail.com
  SMTP_PORT      = 587
  SMTP_USER      = votre@gmail.com
  SMTP_PASSWORD  = xxxx xxxx xxxx xxxx   (mot de passe d'application Gmail)
  SMTP_FROM      = BetaLab 
  FRONTEND_URL   = http://localhost:30000
"""

import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM     = os.getenv("SMTP_FROM",     f"BetaLab ")
FRONTEND_URL  = os.getenv("FRONTEND_URL",  "http://localhost:30000")


def _send(to: str, subject: str, html: str) -> None:
    """Envoie un email HTML via SMTP/TLS. Lève RuntimeError en cas d'échec."""
    if not SMTP_USER or not SMTP_PASSWORD:
        # Mode développement : affiche dans la console au lieu d'envoyer
        print(f"\n{'='*60}")
        print(f"[EMAIL – DEV MODE]  To: {to}")
        print(f"Subject: {subject}")
        print(f"{'='*60}\n")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = SMTP_FROM
        msg["To"]      = to
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as srv:
            srv.ehlo(); srv.starttls(); srv.login(SMTP_USER, SMTP_PASSWORD)
            srv.sendmail(SMTP_FROM, to, msg.as_string())
    except Exception as exc:
        raise RuntimeError(f"Échec envoi email : {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
def send_contact_acknowledgment(to_email: str, to_name: str) -> None:
    """Accusé de réception après soumission du formulaire de contact."""
    html = f"""
BetaLab
Accusé de réception
            Merci pour votre message, {to_name} !
          
            Nous avons bien reçu votre demande. Notre équipe l'examinera dans les plus brefs délais.
          
            Si votre demande concerne une adhésion au laboratoire, vous recevrez très bientôt
            un email d'invitation avec un lien pour compléter votre dossier.
        
"""
    _send(to_email, "📬 BetaLab — Nous avons reçu votre message", html)


# ─────────────────────────────────────────────────────────────────────────────
def send_invitation_email(to_email: str, to_name: str, token: str) -> None:
    """Envoie le lien d'adhésion (valable 72 h)."""
    link = f"{FRONTEND_URL}/adhesion/{token}"
    html = f"""
BetaLab
Laboratoire de Recherche en Informatique
            Bonjour {to_name} 👋
          
            Votre demande a été examinée par l'équipe BetaLab. Nous sommes heureux de vous inviter
            à compléter votre dossier d'adhésion au laboratoire.
          
            Cliquez sur le bouton ci-dessous pour accéder au formulaire.
            Ce lien expire dans 72 heures.
[
              Compléter mon dossier d'adhésion →
            ]({link})
            Lien direct : {link}
          
            Si vous n'avez pas effectué cette demande, ignorez cet email.
          
"""
    _send(to_email, "🎓 Invitation à rejoindre BetaLab — Formulaire d'adhésion", html)


# ─────────────────────────────────────────────────────────────────────────────
def send_credentials_email(to_email: str, to_name: str, password: str) -> None:
    """Envoie les identifiants après création du compte via le formulaire d'adhésion."""
    html = f"""
BetaLab
Bienvenue dans la famille !
            Félicitations, {to_name} ! 🎉
          
            Votre compte BetaLab a été créé avec succès. Voici vos identifiants :
          
                Email de connexion
              {to_email}
                Mot de passe
              {password}
[
              Me connecter →
            ]({FRONTEND_URL}/login)
            ⚠️ Conservez ces identifiants. Votre compte sera activé après validation
            par un administrateur. Vous recevrez une notification.
          
"""
    _send(to_email, "✅ Votre compte BetaLab — Identifiants de connexion", html)


# ═══════════════════════════════════════════════════════════════════════════════
# APPROVAL WORKFLOW NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def send_profile_modification_request_notification(to_admin_email: str, user_name: str, user_email: str, field_name: str, old_value: str, new_value: str) -> None:
    """Notify admin that a user requested to modify their profile."""
    html = f"""
BetaLab
Demande de modification de profil
            Bonjour,
          
            L'utilisateur <strong>{user_name}</strong> ({user_email}) a demandé une modification de son profil :
          
            <strong>Champ :</strong> {field_name}
            <strong>Ancienne valeur :</strong> {old_value or "—"}
            <strong>Nouvelle valeur :</strong> {new_value}
          
            Veuillez examiner cette demande et l'approuver ou la rejeter dans le tableau de bord admin.
          
[
              Voir le tableau de bord →
            ]({FRONTEND_URL}/admin/dashboard)
        
"""
    _send(to_admin_email, f"📋 BetaLab — Demande de modification de profil de {user_name}", html)


def send_profile_modification_approved_email(to_email: str, to_name: str, field_name: str) -> None:
    """Notify user that their profile modification was approved."""
    html = f"""
BetaLab
Modification de profil approuvée
            Bonjour {to_name},
          
            Votre demande de modification a été <strong>approuvée</strong> ✅
          
            <strong>Champ modifié :</strong> {field_name}
          
            La modification a été appliquée à votre profil. Vous pouvez consulter votre profil mis à jour
            en vous connectant à votre tableau de bord.
          
[
              Consulter mon profil →
            ]({FRONTEND_URL}/user/dashboard)
        
"""
    _send(to_email, "✅ BetaLab — Votre modification a été approuvée", html)


def send_profile_modification_rejected_email(to_email: str, to_name: str, field_name: str, admin_notes: str = None) -> None:
    """Notify user that their profile modification was rejected."""
    notes_section = f"<strong>Raison :</strong> {admin_notes}" if admin_notes else ""
    html = f"""
BetaLab
Modification de profil rejetée
            Bonjour {to_name},
          
            Votre demande de modification a été <strong>rejetée</strong> ❌
          
            <strong>Champ :</strong> {field_name}
            {notes_section}
          
            Si vous pensez que c'est une erreur, veuillez contacter l'équipe BetaLab ou
            réessayer avec une valeur différente.
        
"""
    _send(to_email, "❌ BetaLab — Votre modification a été rejetée", html)


def send_question_approved_email(to_email: str, to_name: str, question_text: str) -> None:
    """Notify user that their question was approved by admin."""
    html = f"""
BetaLab
Votre question approuvée
            Bonjour {to_name},
          
            Votre question a été <strong>approuvée</strong> ✅ et est maintenant visible dans le forum.
          
            <em>«{question_text[:100]}...»</em>
          
            Vous recevrez une notification dès que quelqu'un répondra à votre question.
          
[
              Voir mes questions →
            ]({FRONTEND_URL}/user/questions)
        
"""
    _send(to_email, "✅ BetaLab — Votre question a été approuvée", html)


def send_question_rejected_email(to_email: str, to_name: str, question_text: str, admin_notes: str = None) -> None:
    """Notify user that their question was rejected by admin."""
    notes_section = f"<strong>Raison :</strong> {admin_notes}" if admin_notes else ""
    html = f"""
BetaLab
Votre question rejetée
            Bonjour {to_name},
          
            Votre question a été <strong>rejetée</strong> ❌ et ne sera pas publiée.
          
            <em>«{question_text[:100]}...»</em>
            {notes_section}
          
            Si vous pensez que c'est une erreur, veuillez réessayer ou contacter l'équipe BetaLab.
        
"""
    _send(to_email, "❌ BetaLab — Votre question a été rejetée", html)


def send_question_answered_notification(to_email: str, to_name: str, question_text: str, answer_text: str) -> None:
    """Notify user that their question has been answered."""
    html = f"""
BetaLab
Réponse à votre question
            Bonjour {to_name},
          
            Un administrateur a répondu à votre question ✅
          
            <strong>Question :</strong>
            <em>«{question_text[:100]}...»</em>
          
            <strong>Réponse :</strong>
            {answer_text[:200]}...
          
[
              Voir la réponse complète →
            ]({FRONTEND_URL}/user/questions)
        
"""
    _send(to_email, "✅ BetaLab — Une réponse à votre question", html)


def send_activity_approved_email(to_email: str, to_name: str, activity_name: str) -> None:
    """Notify user that their activity modification was approved."""
    html = f"""
BetaLab
Activité approuvée
            Bonjour {to_name},
          
            Votre activité <strong>{activity_name}</strong> a été <strong>approuvée</strong> ✅
            et est maintenant disponible dans le système.
          
[
              Voir l'activité →
            ]({FRONTEND_URL}/user/activities)
        
"""
    _send(to_email, f"✅ BetaLab — {activity_name} approuvée", html)


def send_activity_rejected_email(to_email: str, to_name: str, activity_name: str, admin_notes: str = None) -> None:
    """Notify user that their activity modification was rejected."""
    notes_section = f"<strong>Raison :</strong> {admin_notes}" if admin_notes else ""
    html = f"""
BetaLab
Activité rejetée
            Bonjour {to_name},
          
            Votre demande de modification pour l'activité <strong>{activity_name}</strong> a été <strong>rejetée</strong> ❌
          
            {notes_section}
          
            Si vous pensez que c'est une erreur, veuillez contacter l'équipe BetaLab.
        
"""
    _send(to_email, f"❌ BetaLab — {activity_name} rejetée", html)