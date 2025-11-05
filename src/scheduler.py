"""Scheduler for automatic password resets."""

import logging
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import json

from src.password_reset_bot import PasswordResetBot
from src.database import PasswordResetDB
from src.email_notifier import EmailNotifier


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
        self.db = PasswordResetDB()
        self.emailer = EmailNotifier()
        self.scheduler = BackgroundScheduler()
        self._load_config()

    def _load_config(self):
        """Load accounts and settings from config file."""
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
            self.accounts = self.config.get('accounts', [])
            self.settings = self.config.get('settings', {})

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
                    self.db.update_password(
                        account_id=account_id,
                        old_password=account['current_password'],
                        new_password=bot.new_password,
                        status='success'
                    )
                    # Update config file
                    account['current_password'] = bot.new_password
                    self._save_config()
                    self.logger.info(f"Password reset successful for {account['username']}")
                    self.logger.info(f"New password saved to database and config")
                
            except Exception as e:
                error_msg = str(e)
                self.db.log_reset(account_id, 'failed', error_msg)
                self.db.log_error(account_id, 'PasswordResetError', error_msg)
                
                # Check if it's a wrong password error
                if 'correct username and password' in error_msg.lower() or \
                   'invalid credentials' in error_msg.lower() or \
                   'login failed' in error_msg.lower():
                    self.logger.error(f"WRONG PASSWORD detected for {account['username']}!")
                    self.logger.error(f"Marking account as EXCEPTION - possible customer password change")
                    self.db.mark_account_exception(account_id, 'wrong_password_detected')
                else:
                    self.logger.error(f"Password reset failed for {account['username']}: {error_msg}")
                
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
        """Reset passwords for all enabled accounts."""
        self.logger.info("=" * 60)
        self.logger.info(f"Starting batch password reset at {datetime.now()}")
        self.logger.info("=" * 60)
        
        results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for account in self.accounts:
            if account.get('enabled', True):
                results['total'] += 1
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
