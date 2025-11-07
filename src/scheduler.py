"""Scheduler for automatic password resets."""

import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import json
from typing import List, Dict, Optional

from src.password_reset_bot import PasswordResetBot
from src.database import PasswordResetDB
from src.email_notifier import EmailNotifier
from src.supabase_db import SupabaseDB


class ResetScheduler:
    """Manages scheduled password reset jobs."""

    def __init__(self, config_path: str = "config/accounts.json"):
        """
        Initialize the scheduler.
        
        Args:
            config_path: Path to accounts configuration file
        """
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.db = PasswordResetDB()  # Local SQLite backup
        self.emailer = EmailNotifier()
        self.scheduler = BackgroundScheduler()
        
        # Initialize Supabase for cloud sync
        self.cloud_db = self._init_supabase()
        
        self._load_config()

    def _init_supabase(self):
        """Initialize Supabase connection for cloud sync."""
        try:
            cloud_db = SupabaseDB()
            self.logger.info("✓ Supabase cloud sync enabled")
            return cloud_db
        except Exception as e:
            self.logger.warning(f"⚠ Supabase not available, using local SQLite only: {e}")
            return None

    def _load_config(self):
        """Load accounts and settings from config file."""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            self.accounts = self.config.get('accounts', [])
            self.settings = self.config.get('settings', {})
    
    def check_rental_expiry(self, warning_minutes: int = 30) -> List[Dict]:
        """
        Check for accounts with rentals expiring soon.
        
        Args:
            warning_minutes: Minutes before expiry to show warning (default: 30)
            
        Returns:
            List of accounts with expiring rentals, sorted by urgency
        """
        expiring_accounts = []
        
        if not self.cloud_db:
            self.logger.warning("Supabase not available, cannot check rental expiry")
            return []
        
        try:
            # Get all active rentals
            result = self.cloud_db.client.table('rentals').select(
                '*, accounts(id, username, email, websites(name, validity_hours))'
            ).eq('status', 'active').execute()
            
            now = datetime.now()
            warning_threshold = now + timedelta(minutes=warning_minutes)
            
            for rental in result.data:
                expires_at = datetime.fromisoformat(rental['expires_at'].replace('Z', '+00:00'))
                account = rental['accounts']
                website = account['websites']
                
                # Calculate time remaining
                time_remaining = expires_at - now
                minutes_remaining = int(time_remaining.total_seconds() / 60)
                
                # Check if expiring soon
                if expires_at <= warning_threshold:
                    urgency = 'CRITICAL' if minutes_remaining <= 5 else 'HIGH' if minutes_remaining <= 15 else 'MEDIUM'
                    
                    expiring_accounts.append({
                        'account_id': account['id'],
                        'username': account['username'],
                        'website': website['name'],
                        'validity_hours': website['validity_hours'],
                        'rental_id': rental['id'],
                        'customer': rental.get('customer_name', 'Unknown'),
                        'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'minutes_remaining': minutes_remaining,
                        'urgency': urgency,
                        'should_reset_now': minutes_remaining <= 10  # Reset if ≤10 min remaining
                    })
            
            # Sort by urgency (soonest first)
            expiring_accounts.sort(key=lambda x: x['minutes_remaining'])
            
            return expiring_accounts
            
        except Exception as e:
            self.logger.error(f"Error checking rental expiry: {e}")
            return []
    
    def display_rental_status(self):
        """Display a dashboard of current rentals and upcoming expirations."""
        print("\n" + "="*80)
        print(" 📊 RENTAL STATUS DASHBOARD")
        print("="*80)
        
        # Get expiring rentals
        expiring = self.check_rental_expiry(warning_minutes=60)  # Check next hour
        
        if not expiring:
            print("\n✅ No rentals expiring in the next 60 minutes")
            print("\n💡 All accounts available for password reset")
        else:
            print(f"\n⚠️  Found {len(expiring)} active rental(s) to monitor:")
            print("-"*80)
            
            for i, account in enumerate(expiring, 1):
                urgency_icon = "🔴" if account['urgency'] == 'CRITICAL' else "🟠" if account['urgency'] == 'HIGH' else "🟡"
                
                print(f"\n{i}. {urgency_icon} {account['urgency']} - {account['username']} ({account['website']})")
                print(f"   Customer: {account['customer']}")
                print(f"   Expires: {account['expires_at']}")
                print(f"   Time Remaining: {account['minutes_remaining']} minutes")
                
                if account['should_reset_now']:
                    print(f"   ⏰ ACTION REQUIRED: Reset password NOW!")
                else:
                    reset_time = datetime.now() + timedelta(minutes=account['minutes_remaining'] - 5)
                    print(f"   ⏰ Reset password at: {reset_time.strftime('%H:%M:%S')}")
        
        # Get overall statistics
        if self.cloud_db:
            try:
                stats = self.cloud_db.get_dashboard_stats()
                print("\n" + "-"*80)
                print(f"\n📈 Overall Statistics:")
                print(f"   Total Accounts: {stats['total_accounts']}")
                print(f"   Available: {stats['available_accounts']}")
                print(f"   Rented: {stats['rented_accounts']}")
                print(f"   Exceptions: {stats['exception_accounts']}")
            except Exception as e:
                self.logger.debug(f"Could not fetch stats: {e}")
        
        print("\n" + "="*80)
        print(f" Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def get_accounts_to_reset(self) -> List[Dict]:
        """
        Get list of accounts that need password reset, prioritized by rental expiry.
        
        Returns:
            List of accounts to reset, sorted by priority
        """
        accounts_to_reset = []
        expiring_rentals = self.check_rental_expiry(warning_minutes=30)
        
        # Get usernames of accounts with expiring rentals
        expiring_usernames = {acc['username'] for acc in expiring_rentals if acc['should_reset_now']}
        
        # Prioritize accounts with expiring rentals
        for account in self.accounts:
            if not account.get('enabled', True):
                continue
            
            priority = 1 if account['username'] in expiring_usernames else 2
            accounts_to_reset.append({
                'account': account,
                'priority': priority,
                'reason': 'Rental expiring soon' if priority == 1 else 'Regular reset'
            })
        
        # Sort by priority
        accounts_to_reset.sort(key=lambda x: x['priority'])
        
        return accounts_to_reset

    def _save_config(self):
        """Save accounts and settings to config file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        self.logger.info("Configuration file updated successfully")

    def reset_single_account(self, account: dict) -> bool:
        """
        Reset password for a single account.
        
        Args:
            account: Account dictionary with username, passwords, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Starting password reset for {account['username']}")
            
            # Get website info
            website = self.db.get_website(account.get('website', 'unlocktool'))
            if not website:
                self.logger.error(f"Website '{account.get('website')}' not found in database")
                return False
            
            # Add account to database if not exists
            account_id = self.db.add_account(
                website_name=website['name'],
                username=account['username'],
                password=account['current_password'],
                email=account.get('email')
            )
            
            # Initialize bot
            bot = PasswordResetBot(
                username=account['username'],
                password=account['current_password'],
                headless=self.settings.get('headless', False)
            )
            
            # Perform reset
            success = False
            
            try:
                # Open website
                bot.open_website()
                
                # Wait for Cloudflare
                bot.wait_for_cloudflare()
                
                # Login
                if not bot.login():
                    raise Exception("Login failed")
                
                # Reset password
                if not bot.reset_password():
                    raise Exception("Password reset failed")
                
                success = True
                self.db.log_reset(account_id, 'success', 'Password reset completed successfully')
                
                # Update password in database
                if bot.new_password:
                    # 1. Save to local SQLite (backup)
                    self.db.update_password(
                        account_id=account_id,
                        old_password=account['current_password'],
                        new_password=bot.new_password,
                        status='success'
                    )
                    
                    # 2. Sync to Supabase (cloud)
                    if self.cloud_db:
                        try:
                            self.cloud_db.update_password(
                                account_id=account_id,
                                old_password=account['current_password'],
                                new_password=bot.new_password,
                                status='success'
                            )
                            self.logger.info(f"✓ Password synced to Supabase cloud for {account['username']}")
                        except Exception as e:
                            self.logger.warning(f"⚠ Supabase sync failed (local backup OK): {e}")
                    
                    # 3. Update config file
                    account['current_password'] = bot.new_password
                    self._save_config()
                    self.logger.info(f"✓ Password reset successful for {account['username']}")
                    self.logger.info(f"✓ New password saved to local database and config")
                
            except Exception as e:
                error_msg = str(e)
                self.db.log_reset(account_id, 'failed', error_msg)
                self.db.log_error(account_id, 'PasswordResetError', error_msg)
                
                # Check if it's a wrong password error
                if 'correct username and password' in error_msg.lower() or \
                   'invalid credentials' in error_msg.lower() or \
                   'login failed' in error_msg.lower():
                    self.logger.error(f"⚠ WRONG PASSWORD detected for {account['username']}!")
                    self.logger.error(f"⚠ Marking account as EXCEPTION - possible customer password change")
                    
                    # Mark in local database
                    self.db.mark_account_exception(account_id, 'wrong_password_detected')
                    
                    # Mark in Supabase
                    if self.cloud_db:
                        try:
                            self.cloud_db.mark_account_exception(account_id, 'wrong_password_detected')
                            self.logger.info(f"✓ Exception synced to Supabase for {account['username']}")
                        except Exception as e:
                            self.logger.warning(f"⚠ Supabase exception sync failed: {e}")
                else:
                    self.logger.error(f"✗ Password reset failed for {account['username']}: {error_msg}")
                
            finally:
                bot.close()
            
            # Send notification email
            if self.settings.get('email_notifications'):
                stats = self.db.get_account_stats(account_id)
                self.emailer.send_reset_notification(
                    account['username'],
                    success,
                    stats
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Unexpected error in reset_single_account: {str(e)}")
            return False

    def reset_all_accounts(self):
        """Reset passwords for all enabled accounts, prioritized by rental expiry."""
        # Display rental status dashboard first
        self.display_rental_status()
        
        # Get accounts prioritized by expiry
        prioritized_accounts = self.get_accounts_to_reset()
        
        if prioritized_accounts:
            print("\n🔄 PASSWORD RESET ORDER:")
            for i, item in enumerate(prioritized_accounts, 1):
                print(f"   {i}. {item['account']['username']} - {item['reason']}")
            print()
        
        self.logger.info("=" * 60)
        self.logger.info(f"Starting batch password reset at {datetime.now()}")
        self.logger.info("=" * 60)
        
        results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Reset accounts in priority order
        for item in prioritized_accounts:
            account = item['account']
            results['total'] += 1
            
            self.logger.info(f"Priority: {item['reason']}")
            if self.reset_single_account(account):
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        self.logger.info("=" * 60)
        self.logger.info(f"Batch reset completed: {results['successful']}/{results['total']} successful")
        self.logger.info("=" * 60)
        
        return results

    def schedule_job(self, hour: int = 2, minute: int = 0, day_of_week: str = "0"):
        """
        Schedule the password reset job.
        
        Args:
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            day_of_week: Day of week (0-6, 0 = Monday)
        """
        self.scheduler.add_job(
            self.reset_all_accounts,
            CronTrigger(
                day_of_week=day_of_week,
                hour=hour,
                minute=minute
            ),
            id='password_reset_job',
            name='Automated Password Reset',
            replace_existing=True
        )
        
        self.logger.info(
            f"Job scheduled for {day_of_week} at {hour:02d}:{minute:02d}"
        )

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")

    def get_next_run_time(self):
        """Get the next scheduled run time."""
        job = self.scheduler.get_job('password_reset_job')
        if job:
            return job.next_run_time
        return None

    def run_now(self) -> dict:
        """Run password reset immediately (for testing)."""
        return self.reset_all_accounts()
