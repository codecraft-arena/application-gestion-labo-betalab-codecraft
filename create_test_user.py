#!/usr/bin/env python3
"""Script pour créer un utilisateur de test avec mot de passe haché"""

from database import SessionLocal
from models import User
from passlib.context import CryptContext
import datetime

# Configuration du hachage
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

db = SessionLocal()

try:
    # Supprimer l'ancien utilisateur s'il existe
    existing_user = db.query(User).filter(User.mailer == "test@example.com").first()
    if existing_user:
        db.delete(existing_user)
        print("Ancien utilisateur supprimé")
    
    # Créer un nouvel utilisateur de test
    test_user = User(
        mailer="test@example.com",
        name="Utilisateur Test",
        birthdate=datetime.date(1990, 1, 1),
        password=get_password_hash("password123"),  # Mot de passe simple pour tester
        occupation="etudiant",
        institution="Université Test",
        level="M1",
        domain="Informatique",
        motivation="Test de connexion"
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"Utilisateur de test créé: {test_user.mailer}")
    print(f"Mot de passe: password123")
    print(f"Hash: {test_user.password[:30]}...")
    
except Exception as e:
    print(f"Erreur: {e}")
    db.rollback()
finally:
    db.close()
