"""Advanced configuration and utilities module."""

import json
import hashlib
import secrets
import os
from pathlib import Path
from typing import List, Dict


class AccountManager:
    """Manage account configurations and credentials."""

    def __init__(self, config_path: str = "config/accounts.json"):
        """
        Initialize account manager.
        
        Args:
            config_path: Path to accounts configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            return {"accounts": [], "settings": {}}
        
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        """Save configuration to file."""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def add_account(self, username: str, current_password: str, 
                   new_password: str, email: str = None, enabled: bool = True) -> Dict:
        """
        Add a new account.
        
        Args:
            username: Account username
            current_password: Current password
            new_password: New password to set
            email: Email for notifications
            enabled: Whether account is enabled
            
        Returns:
            Account dictionary
        """
        account_id = max([a.get('id', 0) for a in self.config['accounts']], default=0) + 1
        
        account = {
            "id": account_id,
            "username": username,
            "current_password": current_password,
            "new_password": new_password,
            "email": email or username,
            "enabled": enabled
        }
        
        self.config['accounts'].append(account)
        self.save_config()
        
        return account

    def remove_account(self, account_id: int) -> bool:
        """Remove an account."""
        self.config['accounts'] = [
            a for a in self.config['accounts'] if a['id'] != account_id
        ]
        self.save_config()
        return True

    def enable_account(self, account_id: int):
        """Enable an account."""
        for account in self.config['accounts']:
            if account['id'] == account_id:
                account['enabled'] = True
        self.save_config()

    def disable_account(self, account_id: int):
        """Disable an account."""
        for account in self.config['accounts']:
            if account['id'] == account_id:
                account['enabled'] = False
        self.save_config()

    def list_accounts(self) -> List[Dict]:
        """List all accounts (excluding sensitive data)."""
        return [
            {
                'id': a['id'],
                'username': a['username'],
                'email': a.get('email'),
                'enabled': a.get('enabled', True)
            }
            for a in self.config['accounts']
        ]

    def get_account(self, account_id: int) -> Dict:
        """Get account details."""
        for account in self.config['accounts']:
            if account['id'] == account_id:
                return account
        return None


class PasswordValidator:
    """Validate and generate secure passwords."""

    @staticmethod
    def is_strong(password: str) -> tuple[bool, List[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if len(password) < 12:
            issues.append("Password must be at least 12 characters")
        
        if not any(c.isupper() for c in password):
            issues.append("Must contain uppercase letters")
        
        if not any(c.islower() for c in password):
            issues.append("Must contain lowercase letters")
        
        if not any(c.isdigit() for c in password):
            issues.append("Must contain numbers")
        
        if not any(c in "!@#$%^&*()-_=+[]{};:,.<>?" for c in password):
            issues.append("Must contain special characters")
        
        if len(set(password)) < len(password) * 0.7:
            issues.append("Too many repeated characters")
        
        return len(issues) == 0, issues

    @staticmethod
    def generate_strong_password(length: int = 16) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Password length
            
        Returns:
            Random strong password
        """
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
        
        while True:
            password = ''.join(secrets.choice(charset) for _ in range(length))
            is_valid, _ = PasswordValidator.is_strong(password)
            if is_valid:
                return password


class ConfigValidator:
    """Validate configuration files."""

    @staticmethod
    def validate_accounts_config(config: Dict) -> tuple[bool, List[str]]:
        """
        Validate accounts configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        if 'accounts' not in config:
            errors.append("Missing 'accounts' key")
        
        if 'settings' not in config:
            errors.append("Missing 'settings' key")
        
        if not config.get('settings', {}).get('site_url'):
            errors.append("Missing 'site_url' in settings")
        
        for i, account in enumerate(config.get('accounts', [])):
            if not account.get('username'):
                errors.append(f"Account {i} missing 'username'")
            
            if not account.get('current_password'):
                errors.append(f"Account {i} missing 'current_password'")
            
            if not account.get('new_password'):
                errors.append(f"Account {i} missing 'new_password'")
        
        return len(errors) == 0, errors


class SecurityHelper:
    """Security utility functions."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password for storage (NOT for actual authentication).
        
        Args:
            password: Password to hash
            
        Returns:
            SHA256 hash of password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def mask_password(password: str) -> str:
        """
        Mask a password for logging.
        
        Args:
            password: Password to mask
            
        Returns:
            Masked password (e.g., "pass****word")
        """
        if len(password) <= 4:
            return "*" * len(password)
        
        show_start = len(password) // 4
        show_end = len(password) // 4
        
        return (password[:show_start] + "*" * (len(password) - show_start - show_end) 
                + password[-show_end:])

    @staticmethod
    def get_security_score(username: str, password: str) -> Dict:
        """
        Calculate security score for account.
        
        Args:
            username: Account username
            password: Account password
            
        Returns:
            Security score breakdown
        """
        score = 0
        max_score = 100
        details = {}
        
        # Length score
        length_score = min(len(password) * 5, 25)
        score += length_score
        details['length'] = f"{length_score}/25"
        
        # Complexity score
        complexity_score = 0
        if any(c.isupper() for c in password):
            complexity_score += 15
        if any(c.islower() for c in password):
            complexity_score += 15
        if any(c.isdigit() for c in password):
            complexity_score += 15
        if any(c in "!@#$%^&*()-_=+[]{};:,.<>?" for c in password):
            complexity_score += 20
        if len(set(password)) > len(password) * 0.8:
            complexity_score += 20
        
        score += complexity_score
        details['complexity'] = f"{complexity_score}/85"
        
        # Username similarity (penalty)
        if username.lower() in password.lower():
            score -= 25
            details['username_similarity'] = "Contains username (penalty)"
        
        details['total_score'] = f"{max(0, score)}/{max_score}"
        
        return details
