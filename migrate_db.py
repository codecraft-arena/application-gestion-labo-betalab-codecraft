#!/usr/bin/env python3
"""
Migration de base de données BetaLab — Compatible avec toutes les versions MySQL 5.7+.
Exécuter: python migrate_db.py
"""

import os
from sqlalchemy import inspect, text, create_engine
from sqlalchemy.orm import sessionmaker
from database import engine, Base, SessionLocal
import models

def column_exists(table_name: str, column_name: str) -> bool:
    """Vérifie si une colonne existe dans une table."""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except:
        return False

def table_exists(table_name: str) -> bool:
    """Vérifie si une table existe."""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except:
        return False

def run_migrations():
    """Exécute toutes les migrations dans le bon ordre."""
    
    print("\n1️⃣  Créer les tables de base (users, activities, etc.)...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 2. Ajouter colonne 'role' à users si elle n'existe pas
        if table_exists("users"):
            if not column_exists("users", "role"):
                print("   ➕ Ajout de colonne 'role' à 'users'...")
                db.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'membre'
                """))
                db.commit()
            else:
                print("   ✓ Colonne 'role' existe déjà")
        else:
            print("   ⚠️  Table 'users' n'existe pas encore")
        
        # 3. Ajouter colonne 'participation_status' à contributes si elle n'existe pas
        if table_exists("contributes"):
            if not column_exists("contributes", "participation_status"):
                print("   ➕ Ajout de colonne 'participation_status' à 'contributes'...")
                db.execute(text("""
                    ALTER TABLE contributes 
                    ADD COLUMN participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted'
                """))
                db.commit()
            else:
                print("   ✓ Colonne 'participation_status' existe déjà")
        else:
            print("   ⚠️  Table 'contributes' n'existe pas")
        
        # 4. Vérifier/créer les nouvelles tables de sécurité
        print("\n2️⃣  Vérifier les tables de sécurité...")
        security_tables = {
            "sessions": "sessions persistantes",
            "admin_users": "utilisateurs admin",
            "csrf_tokens": "tokens CSRF",
        }
        
        for table_name, description in security_tables.items():
            if table_exists(table_name):
                print(f"   ✓ Table '{table_name}' ({description}) existe")
            else:
                print(f"   ➕ Table '{table_name}' ({description}) sera créée")
        
        # 5. Créer explicitement les nouvelles tables si elles n'existent pas
        print("\n3️⃣  Créer les tables de sécurité manquantes...")
        
        # Table sessions
        if not table_exists("sessions"):
            print("   ➕ Création table 'sessions'...")
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    token VARCHAR(256) UNIQUE NOT NULL,
                    user_mailer VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    user_agent VARCHAR(255),
                    ip_address VARCHAR(45),
                    FOREIGN KEY(user_mailer) REFERENCES users(mailer)
                )
            """))
            db.commit()
        
        # Table admin_users
        if not table_exists("admin_users"):
            print("   ➕ Création table 'admin_users'...")
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    role VARCHAR(50) DEFAULT 'admin',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            """))
            db.commit()
        
        # Table csrf_tokens
        if not table_exists("csrf_tokens"):
            print("   ➕ Création table 'csrf_tokens'...")
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS csrf_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    token VARCHAR(256) UNIQUE NOT NULL,
                    session_id INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL
                )
            """))
            db.commit()
        
        print("\n✅ Migration complétée avec succès!")
        print("\n📋 État final des tables:")
        inspector = inspect(engine)
        for table in sorted(inspector.get_table_names()):
            cols = len(inspector.get_columns(table))
            print(f"   - {table:30} ({cols} colonnes)")
    
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        print("🔄 Démarrage de la migration BetaLab v2.0...")
        run_migrations()
    except Exception as e:
        print(f"\n❌ Migration échouée")
        exit(1)
