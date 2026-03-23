#!/usr/bin/env python3
"""Script pour hacher les mots de passe existants"""

from database import SessionLocal
from models import User
from passlib.context import CryptContext

# Configuration du hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password[:72])

db = SessionLocal()

try:
    users = db.query(User).all()
    print(f"Vérification de {len(users)} utilisateur(s)...")
    
    for user in users:
        if not user.password.startswith('$2'):
            print(f"Hachage du mot de passe pour: {user.mailer}")
            # Hacher le mot de passe existant
            user.password = get_password_hash(user.password)
            print(f"Nouveau hash: {user.password[:30]}...")
        else:
            print(f"Le mot de passe pour {user.mailer} est déjà haché")
    
    # Sauvegarder les changements
    db.commit()
    print("Mise à jour terminée !")
    
except Exception as e:
    print(f"Erreur: {e}")
    db.rollback()
finally:
    db.close()
