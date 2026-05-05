import sqlite3
import json
import hashlib
from typing import List, Optional, Dict

DB_FILE = "biometrics.db"

def _hash_password(password: str) -> str:
    """Hashes a password for the admin table."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initializes the SQLite database and creates users and admins tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            embedding TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Seed default admin if none exist
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
            ('admin', _hash_password('admin123'))
        )
        
    conn.commit()
    conn.close()

def save_user(user_id: str, embedding: List[float], category: str):
    """Saves a user's biometric embedding and sets status to PENDING."""
    embedding_json = json.dumps(embedding)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, embedding, category, status, timestamp)
        VALUES (?, ?, ?, 'PENDING', CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET 
        embedding=excluded.embedding,
        category=excluded.category,
        status='PENDING',
        timestamp=CURRENT_TIMESTAMP
    ''', (user_id, embedding_json, category))
    
    conn.commit()
    conn.close()

def get_user(user_id: str) -> Optional[Dict]:
    """Retrieves a user's record."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT embedding, status, category FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "embedding": json.loads(row[0]),
            "status": row[1],
            "category": row[2]
        }
    return None

def get_all_users() -> List[Dict]:
    """Retrieves all users for the admin dashboard."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, category, status, timestamp FROM users ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            "user_id": row[0],
            "category": row[1],
            "status": row[2],
            "timestamp": row[3]
        })
    return users

def update_user_status(user_id: str, new_status: str) -> bool:
    """Updates a user's approval status."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (new_status, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def verify_admin(username: str, password: str) -> bool:
    """Verifies admin credentials."""
    pwd_hash = _hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE username = ? AND password_hash = ?', (username, pwd_hash))
    result = cursor.fetchone()
    conn.close()
    return result is not None
