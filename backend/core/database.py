"""
Database Module for User Management
====================================
SQLite database for user authentication and management.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """프로젝트 루트 경로 반환"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return project_root


PROJECT_ROOT = get_project_root()


class UserDatabase:
    """User authentication database manager"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(PROJECT_ROOT / "data" / "users.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"✅ UserDatabase initialized at {db_path}")

    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_admin INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                )
            """)
            conn.commit()
            logger.info("✅ Users table initialized")

    def create_user(self, username: str, email: str, hashed_password: str,
                   full_name: Optional[str] = None, is_admin: bool = False) -> Dict:
        """Create a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, full_name,
                                     is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, email, hashed_password, full_name,
                     1 if is_admin else 0, datetime.now().isoformat()))
                conn.commit()
                return self.get_user_by_username(username)
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            raise ValueError("Username or email already exists")

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users SET last_login = ? WHERE username = ?
            """, (datetime.now().isoformat(), username))
            conn.commit()

    def update_user_password(self, username: str, hashed_password: str):
        """Update user password"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users SET hashed_password = ? WHERE username = ?
            """, (hashed_password, username))
            conn.commit()

    def deactivate_user(self, username: str):
        """Deactivate a user account"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users SET is_active = 0 WHERE username = ?
            """, (username,))
            conn.commit()

    def list_users(self) -> list[Dict]:
        """List all users (admin function)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login FROM users")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


# Global instance
user_db = UserDatabase()
