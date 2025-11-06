"""
API Management System for Tool Rental
Handles API key creation, account rentals, and usage tracking
"""

import sqlite3
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict, List


class APIManager:
    """Manages API keys and tracks their usage."""
    
    def __init__(self, db_path: str = "database/rental_system.db"):
        self.db_path = db_path
        self._init_api_tables()
    
    def _init_api_tables(self):
        """Initialize API management tables."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        # API Keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key TEXT UNIQUE NOT NULL,
                api_key_hash TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                total_requests INTEGER DEFAULT 0,
                rate_limit INTEGER DEFAULT 100,
                notes TEXT
            )
        """)
        
        # API Usage Log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                website TEXT NOT NULL,
                action TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_status TEXT,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_usage_api_key 
            ON api_usage(api_key_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp 
            ON api_usage(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_keys_hash 
            ON api_keys(api_key_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def generate_api_key(self, name: str, email: str = None, 
                        rate_limit: int = 100, notes: str = None) -> Dict:
        """
        Generate a new API key.
        
        Args:
            name: Name/identifier for this API key
            email: Email of the API key owner
            rate_limit: Maximum requests per day
            notes: Additional notes
            
        Returns:
            Dict with api_key and details
        """
        # Generate secure random API key
        api_key = f"urt_{secrets.token_urlsafe(32)}"
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys (api_key_hash, name, email, rate_limit, notes, api_key)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (api_key_hash, name, email, rate_limit, notes, api_key))
        
        api_key_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': api_key_id,
            'api_key': api_key,
            'name': name,
            'email': email,
            'rate_limit': rate_limit,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Validate an API key and return its details.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            API key details if valid, None otherwise
        """
        if not api_key or not api_key.startswith('urt_'):
            return None
        
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, status, rate_limit, total_requests, created_at, last_used
            FROM api_keys
            WHERE api_key_hash = ? AND status = 'active'
        """, (api_key_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'status': row[3],
            'rate_limit': row[4],
            'total_requests': row[5],
            'created_at': row[6],
            'last_used': row[7]
        }
    
    def update_api_usage(self, api_key_id: int):
        """Update API key usage statistics."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys 
            SET total_requests = total_requests + 1,
                last_used = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (api_key_id,))
        
        conn.commit()
        conn.close()
    
    def log_api_request(self, api_key_id: int, account_id: int, website: str,
                       action: str, response_status: str, ip_address: str = None,
                       user_agent: str = None):
        """
        Log an API request.
        
        Args:
            api_key_id: ID of the API key used
            account_id: ID of the account accessed
            website: Website/tool name
            action: Action performed (rent, return, check)
            response_status: Response status (success, error, etc.)
            ip_address: IP address of requester
            user_agent: User agent string
        """
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_usage 
            (api_key_id, account_id, website, action, response_status, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (api_key_id, account_id, website, action, response_status, ip_address, user_agent))
        
        conn.commit()
        conn.close()
    
    def get_api_keys(self, status: str = None) -> List[Dict]:
        """Get all API keys, optionally filtered by status."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, name, email, status, rate_limit, total_requests, 
                       created_at, last_used, notes
                FROM api_keys
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, name, email, status, rate_limit, total_requests, 
                       created_at, last_used, notes
                FROM api_keys
                ORDER BY created_at DESC
            """)
        
        keys = []
        for row in cursor.fetchall():
            keys.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'status': row[3],
                'rate_limit': row[4],
                'total_requests': row[5],
                'created_at': row[6],
                'last_used': row[7],
                'notes': row[8]
            })
        
        conn.close()
        return keys
    
    def revoke_api_key(self, api_key_id: int) -> bool:
        """Revoke an API key."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys 
            SET status = 'revoked'
            WHERE id = ?
        """, (api_key_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_usage_stats(self, api_key_id: int = None, days: int = 30) -> Dict:
        """
        Get usage statistics for an API key or all keys.
        
        Args:
            api_key_id: Specific API key ID, or None for all keys
            days: Number of days to look back
            
        Returns:
            Usage statistics
        """
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        if api_key_id:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT account_id) as unique_accounts,
                    COUNT(DISTINCT website) as websites_used,
                    SUM(CASE WHEN action = 'rent' THEN 1 ELSE 0 END) as rentals,
                    SUM(CASE WHEN action = 'return' THEN 1 ELSE 0 END) as returns
                FROM api_usage
                WHERE api_key_id = ?
                AND timestamp >= datetime('now', '-' || ? || ' days')
            """, (api_key_id, days))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT account_id) as unique_accounts,
                    COUNT(DISTINCT api_key_id) as active_api_keys,
                    SUM(CASE WHEN action = 'rent' THEN 1 ELSE 0 END) as rentals,
                    SUM(CASE WHEN action = 'return' THEN 1 ELSE 0 END) as returns
                FROM api_usage
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            """, (days,))
        
        row = cursor.fetchone()
        conn.close()
        
        if api_key_id:
            return {
                'total_requests': row[0] or 0,
                'unique_accounts': row[1] or 0,
                'websites_used': row[2] or 0,
                'rentals': row[3] or 0,
                'returns': row[4] or 0
            }
        else:
            return {
                'total_requests': row[0] or 0,
                'unique_accounts': row[1] or 0,
                'active_api_keys': row[2] or 0,
                'rentals': row[3] or 0,
                'returns': row[4] or 0
            }
    
    def get_recent_activity(self, api_key_id: int = None, limit: int = 50) -> List[Dict]:
        """Get recent API activity."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        
        if api_key_id:
            cursor.execute("""
                SELECT 
                    u.timestamp, u.action, u.website, u.response_status,
                    a.username, k.name as api_key_name, u.ip_address
                FROM api_usage u
                JOIN accounts a ON u.account_id = a.id
                JOIN api_keys k ON u.api_key_id = k.id
                WHERE u.api_key_id = ?
                ORDER BY u.timestamp DESC
                LIMIT ?
            """, (api_key_id, limit))
        else:
            cursor.execute("""
                SELECT 
                    u.timestamp, u.action, u.website, u.response_status,
                    a.username, k.name as api_key_name, u.ip_address
                FROM api_usage u
                JOIN accounts a ON u.account_id = a.id
                JOIN api_keys k ON u.api_key_id = k.id
                ORDER BY u.timestamp DESC
                LIMIT ?
            """, (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'timestamp': row[0],
                'action': row[1],
                'website': row[2],
                'status': row[3],
                'username': row[4],
                'api_key_name': row[5],
                'ip_address': row[6]
            })
        
        conn.close()
        return activities
