"""
Supabase Database Client
Replaces local SQLite with cloud Supabase PostgreSQL
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from supabase import create_client, Client


class SupabaseDB:
    """Supabase cloud database for tool rental management."""
    
    def __init__(self, config_path: str = "config/supabase_config.json"):
        """
        Initialize Supabase connection.
        
        Args:
            config_path: Path to Supabase configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.url = config['url']
        self.key = config['service_key']  # Use service_role key for full access
        
        # Create Supabase client
        self.client: Client = create_client(self.url, self.key)
        
        print(f"✓ Connected to Supabase: {self.url}")
    
    # ===================== WEBSITE MANAGEMENT =====================
    
    def add_website(self, name: str, url: str, validity_hours: int, description: str = None) -> int:
        """Add a new website/tool."""
        try:
            result = self.client.table('websites').insert({
                'name': name,
                'url': url,
                'validity_hours': validity_hours,
                'description': description
            }).execute()
            
            return result.data[0]['id']
        except Exception as e:
            # If website exists, get its ID
            result = self.client.table('websites').select('id').eq('name', name).execute()
            return result.data[0]['id'] if result.data else None
    
    def get_website(self, name: str) -> Optional[Dict]:
        """Get website details by name."""
        result = self.client.table('websites').select('*').eq('name', name).execute()
        return result.data[0] if result.data else None
    
    # ===================== ACCOUNT MANAGEMENT =====================
    
    def add_account(self, website_name: str, username: str, password: str, email: str = None) -> int:
        """Add a new account."""
        # Get website ID
        website = self.get_website(website_name)
        if not website:
            raise ValueError(f"Website '{website_name}' not found")
        
        try:
            result = self.client.table('accounts').insert({
                'website_id': website['id'],
                'username': username,
                'email': email,
                'current_password': password,
                'status': 'available'
            }).execute()
            
            return result.data[0]['id']
        except Exception as e:
            # If account exists, get its ID
            result = self.client.table('accounts').select('id').eq('username', username).eq('website_id', website['id']).execute()
            return result.data[0]['id'] if result.data else None
    
    def update_password(self, account_id: int, old_password: str, new_password: str, status: str = 'success'):
        """Update account password and log to history."""
        # Update current password
        self.client.table('accounts').update({
            'current_password': new_password,
            'last_reset': datetime.now().isoformat()
        }).eq('id', account_id).execute()
        
        # Log to password history
        self.client.table('password_history').insert({
            'account_id': account_id,
            'old_password': old_password,
            'new_password': new_password,
            'status': status,
            'message': 'Password reset completed successfully' if status == 'success' else None
        }).execute()
    
    def get_available_accounts(self, website_name: str = None) -> List[Dict]:
        """Get all available accounts for a website."""
        # Use stored function for auto-expiry
        if website_name:
            result = self.client.rpc('get_available_accounts', {'website_name': website_name}).execute()
            return result.data
        else:
            # Get all available accounts
            result = self.client.table('accounts').select('*, websites(name, validity_hours)').eq('status', 'available').execute()
            return result.data
    
    # ===================== RENTAL MANAGEMENT =====================
    
    def rent_account(self, account_id: int, customer_name: str = None, 
                    customer_email: str = None, customer_phone: str = None) -> Dict:
        """Rent an account to a customer."""
        # Get account and website details
        account = self.client.table('accounts').select('*, websites(*)').eq('id', account_id).eq('status', 'available').execute()
        
        if not account.data:
            return None
        
        account_data = account.data[0]
        website = account_data['websites']
        validity_hours = website['validity_hours']
        expires_at = (datetime.now() + timedelta(hours=validity_hours)).isoformat()
        
        # Create rental record
        rental = self.client.table('rentals').insert({
            'account_id': account_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'expires_at': expires_at,
            'status': 'active'
        }).execute()
        
        # Mark account as rented
        self.client.table('accounts').update({
            'status': 'rented',
            'rented_at': datetime.now().isoformat(),
            'available_at': expires_at
        }).eq('id', account_id).execute()
        
        return {
            'id': rental.data[0]['id'],
            'account_id': account_id,
            'username': account_data['username'],
            'password': account_data['current_password'],
            'website': website['name'],
            'url': website['url'],
            'validity_hours': validity_hours,
            'expires_at': expires_at
        }
    
    def return_account(self, account_id: int):
        """Return a rented account."""
        # Mark account as available
        self.client.table('accounts').update({
            'status': 'available',
            'available_at': datetime.now().isoformat()
        }).eq('id', account_id).execute()
        
        # Mark rental as completed
        self.client.table('rentals').update({
            'returned_at': datetime.now().isoformat(),
            'status': 'completed'
        }).eq('account_id', account_id).eq('status', 'active').execute()
    
    # ===================== EXCEPTION HANDLING =====================
    
    def mark_account_exception(self, account_id: int, reason: str):
        """Mark account as exception."""
        # Get current failed attempts count
        result = self.client.table('accounts').select('failed_login_attempts').eq('id', account_id).execute()
        
        current_attempts = 0
        if result.data and len(result.data) > 0:
            current_attempts = result.data[0].get('failed_login_attempts', 0) or 0
        
        # Update account status
        self.client.table('accounts').update({
            'status': 'exception',
            'exception_reason': reason,
            'failed_login_attempts': current_attempts + 1,
            'last_failed_login': datetime.now().isoformat()
        }).eq('id', account_id).execute()
    
    def reset_account_exception(self, account_id: int, new_password: str):
        """Clear exception status and update password."""
        self.client.table('accounts').update({
            'status': 'available',
            'current_password': new_password,
            'exception_reason': None,
            'failed_login_attempts': 0,
            'last_failed_login': None,
            'last_reset': datetime.now().isoformat()
        }).eq('id', account_id).execute()
    
    def get_exception_accounts(self) -> List[Dict]:
        """Get all accounts with exceptions."""
        result = self.client.table('accounts').select('*, websites(name)').eq('status', 'exception').execute()
        return result.data
    
    # ===================== PASSWORD HISTORY =====================
    
    def get_password_history(self, account_id: int, limit: int = 10) -> List[Dict]:
        """Get password change history for an account."""
        result = self.client.table('password_history').select('*').eq('account_id', account_id).order('reset_date', desc=True).limit(limit).execute()
        return result.data
    
    # ===================== STATISTICS =====================
    
    def get_dashboard_stats(self) -> Dict:
        """Get overall system statistics."""
        # Get counts
        total_accounts = self.client.table('accounts').select('id', count='exact').execute().count
        available_accounts = self.client.table('accounts').select('id', count='exact').eq('status', 'available').execute().count
        rented_accounts = self.client.table('accounts').select('id', count='exact').eq('status', 'rented').execute().count
        exception_accounts = self.client.table('accounts').select('id', count='exact').eq('status', 'exception').execute().count
        active_rentals = self.client.table('rentals').select('id', count='exact').eq('status', 'active').execute().count
        total_rentals = self.client.table('rentals').select('id', count='exact').execute().count
        
        return {
            'total_accounts': total_accounts,
            'available_accounts': available_accounts,
            'rented_accounts': rented_accounts,
            'exception_accounts': exception_accounts,
            'active_rentals': active_rentals,
            'total_rentals': total_rentals
        }
