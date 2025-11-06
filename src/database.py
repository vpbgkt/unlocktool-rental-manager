"""Database management module for tool rental and password management."""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class PasswordResetDB:
    """SQLite database for managing tool rental accounts and password resets."""

    def __init__(self, db_path: str = "database/rental_system.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()
        
        # Enable WAL mode for better concurrent access
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()

    def _get_connection(self):
        """Get a database connection with proper timeout."""
        return sqlite3.connect(self.db_path, timeout=30.0)

    def init_schema(self):
        """Initialize database schema if it doesn't exist."""
        conn = self._get_connection() if hasattr(self, '_get_connection') else sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        # Websites/Tools table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                validity_hours INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Accounts table - stores all accounts for all websites
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                email TEXT,
                current_password TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                rented_at TIMESTAMP,
                available_at TIMESTAMP,
                last_reset TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP,
                exception_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(website_id) REFERENCES websites(id),
                UNIQUE(website_id, username)
            )
        """)

        # Password history table - keeps track of all password changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                old_password TEXT,
                new_password TEXT NOT NULL,
                reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                message TEXT,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)

        # Rentals table - tracks who rented what and when
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                customer_name TEXT,
                customer_email TEXT,
                customer_phone TEXT,
                rented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                returned_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)

        # Error logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                error_type TEXT,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                traceback TEXT,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            )
        """)

        conn.commit()
        conn.close()

    # ===================== WEBSITE MANAGEMENT =====================
    
    def add_website(self, name: str, url: str, validity_hours: int, description: str = None) -> int:
        """
        Add a new website/tool to the system.
        
        Args:
            name: Website name (e.g., 'unlocktool', 'androidmultitool')
            url: Website URL
            validity_hours: How long rental is valid (6 for unlocktool, 2 for androidmultitool)
            description: Optional description
            
        Returns:
            Website ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO websites (name, url, validity_hours, description)
            VALUES (?, ?, ?, ?)
        """, (name, url, validity_hours, description))

        conn.commit()

        cursor.execute("SELECT id FROM websites WHERE name = ?", (name,))
        website_id = cursor.fetchone()[0]
        conn.close()

        return website_id

    def get_website(self, name: str) -> Optional[Dict]:
        """Get website details by name."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM websites WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'validity_hours': row[3],
                'description': row[4],
                'created_at': row[5]
            }
        return None

    # ===================== ACCOUNT MANAGEMENT =====================

    def add_account(self, website_name: str, username: str, password: str, email: str = None) -> int:
        """
        Add a new account to the system.
        
        Args:
            website_name: Name of the website/tool
            username: Account username
            password: Current password
            email: Email address
            
        Returns:
            Account ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get website ID
        cursor.execute("SELECT id FROM websites WHERE name = ?", (website_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise ValueError(f"Website '{website_name}' not found. Add it first using add_website()")
        
        website_id = result[0]

        cursor.execute("""
            INSERT OR IGNORE INTO accounts (website_id, username, current_password, email, status)
            VALUES (?, ?, ?, ?, 'available')
        """, (website_id, username, password, email))

        conn.commit()

        cursor.execute("""
            SELECT id FROM accounts WHERE website_id = ? AND username = ?
        """, (website_id, username))
        account_id = cursor.fetchone()[0]
        conn.close()

        return account_id

    def update_password(self, account_id: int, old_password: str, new_password: str, status: str = 'success'):
        """
        Update account password and log the change.
        
        Args:
            account_id: ID of the account
            old_password: Previous password
            new_password: New password
            status: 'success' or 'failed'
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Update current password
        cursor.execute("""
            UPDATE accounts 
            SET current_password = ?, last_reset = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_password, account_id))

        # Log password history
        cursor.execute("""
            INSERT INTO password_history (account_id, old_password, new_password, status)
            VALUES (?, ?, ?, ?)
        """, (account_id, old_password, new_password, status))

        conn.commit()
        conn.close()

    def get_available_accounts(self, website_name: str) -> List[Dict]:
        """
        Get all available accounts for a specific website.
        
        Args:
            website_name: Name of the website
            
        Returns:
            List of available accounts
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # First, mark expired rentals as available
        cursor.execute("""
            UPDATE accounts 
            SET status = 'available', available_at = CURRENT_TIMESTAMP
            WHERE status = 'rented' AND available_at < CURRENT_TIMESTAMP
        """)
        conn.commit()

        # Get available accounts
        cursor.execute("""
            SELECT a.id, a.username, a.email, a.current_password, a.last_reset, w.name, w.validity_hours
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            WHERE w.name = ? AND a.status = 'available'
            ORDER BY a.last_reset ASC
        """, (website_name,))

        columns = ['id', 'username', 'email', 'password', 'last_reset', 'website', 'validity_hours']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return results

    # ===================== RENTAL MANAGEMENT =====================

    def rent_account(self, account_id: int, customer_name: str = None, 
                    customer_email: str = None, customer_phone: str = None) -> Dict:
        """
        Rent an account to a customer.
        
        Args:
            account_id: ID of the account to rent
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            
        Returns:
            Dictionary with rental details
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get account and website details
        cursor.execute("""
            SELECT a.id, a.username, a.current_password, w.name, w.url, w.validity_hours
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            WHERE a.id = ? AND a.status = 'available'
        """, (account_id,))

        account = cursor.fetchone()
        if not account:
            conn.close()
            return None

        # Calculate expiry time
        validity_hours = account[5]
        expires_at = datetime.now() + timedelta(hours=validity_hours)

        # Create rental record
        cursor.execute("""
            INSERT INTO rentals (account_id, customer_name, customer_email, customer_phone, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (account_id, customer_name, customer_email, customer_phone, expires_at))

        rental_id = cursor.lastrowid

        # Mark account as rented
        cursor.execute("""
            UPDATE accounts 
            SET status = 'rented', rented_at = CURRENT_TIMESTAMP, available_at = ?
            WHERE id = ?
        """, (expires_at, account_id))

        conn.commit()
        conn.close()

        return {
            'id': rental_id,
            'account_id': account[0],
            'username': account[1],
            'password': account[2],
            'website': account[3],
            'url': account[4],
            'validity_hours': validity_hours,
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def return_account(self, account_id: int):
        """
        Mark an account as returned/available.
        
        Args:
            account_id: ID of the account
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE accounts 
            SET status = 'available', available_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (account_id,))

        cursor.execute("""
            UPDATE rentals 
            SET returned_at = CURRENT_TIMESTAMP, status = 'completed'
            WHERE account_id = ? AND status = 'active'
        """, (account_id,))

        conn.commit()
        conn.close()

    # ===================== ACCOUNT STATUS & EXCEPTIONS =====================

    def mark_account_exception(self, account_id: int, reason: str):
        """
        Mark an account with an exception (wrong password, hacked, etc.).
        
        Args:
            account_id: ID of the account
            reason: Reason for exception (e.g., 'wrong_password', 'customer_changed', 'hacked')
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE accounts 
            SET status = 'exception', 
                exception_reason = ?,
                last_failed_login = CURRENT_TIMESTAMP,
                failed_login_attempts = failed_login_attempts + 1
            WHERE id = ?
        """, (reason, account_id))

        conn.commit()
        conn.close()

    def reset_account_exception(self, account_id: int, new_password: str):
        """
        Clear exception status and update password (after manual verification).
        
        Args:
            account_id: ID of the account
            new_password: The correct password
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE accounts 
            SET status = 'available', 
                exception_reason = NULL,
                failed_login_attempts = 0,
                current_password = ?,
                available_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_password, account_id))

        conn.commit()
        conn.close()

    def get_exception_accounts(self) -> List[Dict]:
        """Get all accounts marked with exceptions."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, w.name as website, a.username, a.email, 
                   a.exception_reason, a.failed_login_attempts, a.last_failed_login
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            WHERE a.status = 'exception'
            ORDER BY a.last_failed_login DESC
        """)

        columns = ['id', 'website', 'username', 'email', 'exception_reason', 
                   'failed_attempts', 'last_failed']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_active_rentals(self) -> List[Dict]:
        """Get all currently active rentals."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.id, a.username, w.name, r.customer_name, r.rented_at, r.expires_at
            FROM rentals r
            JOIN accounts a ON r.account_id = a.id
            JOIN websites w ON a.website_id = w.id
            WHERE r.status = 'active' AND r.expires_at > CURRENT_TIMESTAMP
            ORDER BY r.expires_at ASC
        """)

        columns = ['rental_id', 'username', 'website', 'customer', 'rented_at', 'expires_at']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return results

    # ===================== PASSWORD HISTORY =====================

    def get_password_history(self, account_id: int, limit: int = 10) -> List[Dict]:
        """
        Get password change history for an account.
        
        Args:
            account_id: ID of the account
            limit: Maximum number of records
            
        Returns:
            List of password changes
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, new_password, reset_date, status, message
            FROM password_history
            WHERE account_id = ?
            ORDER BY reset_date DESC
            LIMIT ?
        """, (account_id, limit))

        columns = ['id', 'password', 'reset_date', 'status', 'message']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return results

    # ===================== LEGACY METHODS (for compatibility) =====================

    def log_reset(self, account_id: int, status: str, message: str = None):
        """Log a password reset attempt (legacy method)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO password_history (account_id, new_password, status, message)
            VALUES (?, '', ?, ?)
        """, (account_id, status, message))

        conn.commit()
        conn.close()

    def log_error(self, account_id: int, error_type: str, error_message: str, traceback_str: str = None):
        """
        Log an error for an account.
        
        Args:
            account_id: ID of the account
            error_type: Type of error
            error_message: Error message
            traceback_str: Full traceback
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO error_logs (account_id, error_type, error_message, traceback)
            VALUES (?, ?, ?, ?)
        """, (account_id, error_type, error_message, traceback_str))

        conn.commit()
        conn.close()

    # ===================== REPORTING & STATISTICS =====================

    def get_dashboard_stats(self) -> Dict:
        """Get overall system statistics for dashboard."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total accounts by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM accounts
            GROUP BY status
        """)
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Total websites
        cursor.execute("SELECT COUNT(*) FROM websites")
        total_websites = cursor.fetchone()[0]

        # Active rentals
        cursor.execute("""
            SELECT COUNT(*) FROM rentals 
            WHERE status = 'active' AND expires_at > CURRENT_TIMESTAMP
        """)
        active_rentals = cursor.fetchone()[0]

        # Password resets today
        cursor.execute("""
            SELECT COUNT(*) FROM password_history 
            WHERE DATE(reset_date) = DATE('now') AND status = 'success'
        """)
        resets_today = cursor.fetchone()[0]

        conn.close()

        return {
            'total_accounts': sum(status_counts.values()),
            'available_accounts': status_counts.get('available', 0),
            'rented_accounts': status_counts.get('rented', 0),
            'total_websites': total_websites,
            'active_rentals': active_rentals,
            'resets_today': resets_today
        }

    def get_account_stats(self, account_id: int) -> Dict:
        """Get statistics for a specific account (legacy method)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.username, a.email, a.last_reset, a.status, w.name
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            WHERE a.id = ?
        """, (account_id,))

        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None

        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM password_history WHERE account_id = ?
        """, (account_id,))

        stats = cursor.fetchone()
        conn.close()

        return {
            "username": result[0],
            "email": result[1],
            "last_reset": result[2],
            "status": result[3],
            "website": result[4],
            "total_resets": stats[0] or 0,
            "successful_resets": stats[1] or 0,
            "failed_resets": stats[2] or 0
        }

    def get_all_accounts_summary(self) -> List[Dict]:
        """Get summary of all accounts."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, w.name as website, a.username, a.email, a.status, 
                   a.last_reset, a.available_at
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
            ORDER BY w.name, a.username
        """)
        columns = ['id', 'website', 'username', 'email', 'status', 'last_reset', 'available_at']
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return results
