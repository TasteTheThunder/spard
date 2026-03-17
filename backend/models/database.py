"""
Database models and management for SPARD
Handles user authentication and session management using SQLite
"""

import sqlite3
import bcrypt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for SPARD application"""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
        logger.info(f"Database manager initialized: {self.db_path}")

    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        allergies TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Sessions table for login management
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Analysis history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        doctor_a_medicines TEXT NOT NULL,
                        doctor_b_medicines TEXT NOT NULL,
                        user_allergies TEXT,
                        conflicts_found TEXT,
                        risk_level TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_user(self, name: str, email: str, password_hash: bytes) -> Optional[int]:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                    (name, email, password_hash)
                )
                user_id = cursor.lastrowid
                conn.commit()
                logger.info(f"User created successfully: ID {user_id}")
                return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"User creation failed - email already exists: {email}")
            return None
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Get user by email error: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Get user by ID error: {e}")
            return None

    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET last_login = ? WHERE id = ?',
                    (datetime.now(), user_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Update last login error: {e}")

    def create_session(self, user_id: int, session_token: str, expires_at: datetime) -> bool:
        """Create a new session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)',
                    (session_token, user_id, expires_at)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Create session error: {e}")
            return False

    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user info"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.*, s.expires_at
                    FROM users u
                    JOIN sessions s ON u.id = s.user_id
                    WHERE s.id = ? AND s.is_active = 1 AND s.expires_at > ? AND u.is_active = 1
                ''', (session_token, datetime.now()))
                
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None

    def invalidate_session(self, session_token: str):
        """Invalidate a session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE sessions SET is_active = 0 WHERE id = ?',
                    (session_token,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")

    def update_user_allergies(self, user_id: int, allergies: str) -> bool:
        """Update user allergies"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE users SET allergies = ? WHERE id = ?',
                    (allergies, user_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Update allergies error: {e}")
            return False

    def save_analysis(self, user_id: int, doctor_a_medicines: str, doctor_b_medicines: str, 
                     user_allergies: str, conflicts_found: str, risk_level: str) -> bool:
        """Save analysis history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analysis_history 
                    (user_id, doctor_a_medicines, doctor_b_medicines, user_allergies, conflicts_found, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, doctor_a_medicines, doctor_b_medicines, user_allergies, conflicts_found, risk_level))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Save analysis error: {e}")
            return False

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get analysis count
                cursor.execute('SELECT COUNT(*) as count FROM analysis_history WHERE user_id = ?', (user_id,))
                analysis_count = cursor.fetchone()['count']
                
                # Get last analysis date
                cursor.execute(
                    'SELECT created_at FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
                    (user_id,)
                )
                last_analysis = cursor.fetchone()
                last_analysis_date = last_analysis['created_at'] if last_analysis else None
                
                return {
                    'total_analyses': analysis_count,
                    'last_analysis': last_analysis_date
                }
        except Exception as e:
            logger.error(f"Get user stats error: {e}")
            return {'total_analyses': 0, 'last_analysis': None}

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM sessions WHERE expires_at < ?',
                    (datetime.now(),)
                )
                deleted_count = cursor.rowcount
                conn.commit()
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")

    def get_analysis_history(self, user_id: int, limit: int = 10) -> list:
        """Get user's analysis history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM analysis_history 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Get analysis history error: {e}")
            return []