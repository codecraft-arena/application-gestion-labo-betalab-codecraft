"""
Migration Python robuste — BetaLab
Compatible avec toutes les versions MySQL 5.7+
Vérifie l'existence des colonnes avant de les ajouter
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "luc")
DB_PASSWORD = os.getenv("DB_PASSWORD", "luc123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "db_lab")

def column_exists(conn, table_name, column_name):
    """Vérifie si une colonne existe dans une table."""
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_name}'
            AND TABLE_SCHEMA = '{DB_NAME}'
        """)
        return cursor.fetchone() is not None

def run_migration():
    """Exécute la migration."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Connexion à la base de données réussie")
        
        with conn.cursor() as cursor:
            # 1. Ajouter colonne 'role' à users
            if not column_exists(conn, 'users', 'role'):
                print("➕ Ajout colonne 'role' à users...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'membre' AFTER suspended
                """)
                print("   ✅ Colonne 'role' ajoutée")
            else:
                print("ℹ️  Colonne 'role' existe déjà")
            
            # 2. Ajouter colonne 'participation_status' à contributes
            if not column_exists(conn, 'contributes', 'participation_status'):
                print("➕ Ajout colonne 'participation_status' à contributes...")
                cursor.execute("""
                    ALTER TABLE contributes 
                    ADD COLUMN participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted'
                """)
                print("   ✅ Colonne 'participation_status' ajoutée")
            else:
                print("ℹ️  Colonne 'participation_status' existe déjà")
            
            # 3. Créer table sessions
            print("📋 Création table sessions...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    token VARCHAR(256) NOT NULL UNIQUE,
                    user_email VARCHAR(100) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    user_agent VARCHAR(255),
                    ip_address VARCHAR(45),
                    KEY idx_token (token),
                    KEY idx_user (user_email),
                    KEY idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table sessions prête")
            
            # 4. Créer table admin_users
            print("📋 Création table admin_users...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    role VARCHAR(50) DEFAULT 'admin',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    KEY idx_username (username),
                    KEY idx_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table admin_users prête")
            
            # 5. Créer table csrf_tokens
            print("📋 Création table csrf_tokens...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS csrf_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    token VARCHAR(256) NOT NULL UNIQUE,
                    session_id INT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    KEY idx_token (token),
                    KEY idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table csrf_tokens prête")
            
            # 6. Créer table contact_requests si n'existe pas
            print("📋 Création table contact_requests...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contact_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(120) NOT NULL,
                    subject VARCHAR(255),
                    message TEXT,
                    is_join_request BOOLEAN DEFAULT FALSE,
                    status VARCHAR(50) DEFAULT 'nouveau',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    KEY idx_email (email),
                    KEY idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table contact_requests prête")
            
            # 7. Créer table invitation_tokens si n'existe pas
            print("📋 Création table invitation_tokens...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invitation_tokens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    token VARCHAR(150) NOT NULL UNIQUE,
                    email VARCHAR(120) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    contact_id INT,
                    KEY idx_token (token),
                    KEY idx_email (email),
                    KEY idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table invitation_tokens prête")
            
            # 8. Créer table events si n'existe pas
            print("📋 Création table events...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    event_date DATE,
                    location VARCHAR(255),
                    event_type VARCHAR(100) DEFAULT 'événement',
                    created_by VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    KEY idx_date (event_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ Table events prête")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ MIGRATION RÉUSSIE!")
        print("="*60)
        print("\nRésumé des tables prêtes:")
        print("  ✅ users (colonne 'role' ajoutée)")
        print("  ✅ contributes (colonne 'participation_status' ajoutée)")
        print("  ✅ sessions (persistance des sessions)")
        print("  ✅ admin_users (authentification admin améliorée)")
        print("  ✅ csrf_tokens (protection CSRF)")
        print("  ✅ contact_requests (demandes de contact)")
        print("  ✅ invitation_tokens (tokens d'adhésion)")
        print("  ✅ events (événements)")
        
    except pymysql.Error as e:
        print(f"❌ Erreur MySQL: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        exit(1)

if __name__ == "__main__":
    print("🚀 Démarrage de la migration BetaLab...")
    print("="*60)
    run_migration()
