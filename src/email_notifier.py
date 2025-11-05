"""Email notification module for password reset status."""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict


class EmailNotifier:
    """Send email notifications for password resets."""

    def __init__(self):
        """Initialize email notifier with credentials from environment."""
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.sender_email = os.getenv('EMAIL_SENDER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT')

    def send_reset_notification(self, username: str, success: bool, stats: Dict = None):
        """
        Send email notification about password reset.
        
        Args:
            username: Account username
            success: Whether reset was successful
            stats: Account statistics dictionary
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            self.logger.warning("Email credentials not configured, skipping notification")
            return False

        try:
            status_text = "✓ SUCCESS" if success else "✗ FAILED"
            subject = f"Password Reset {status_text} - {username}"
            
            body = self._build_email_body(username, success, stats)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Notification email sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False

    def _build_email_body(self, username: str, success: bool, stats: Dict = None) -> str:
        """
        Build HTML email body.
        
        Args:
            username: Account username
            success: Whether reset was successful
            stats: Account statistics
            
        Returns:
            HTML email body
        """
        status_color = "green" if success else "red"
        status_text = "Successfully Reset" if success else "Failed"
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ background-color: #f5f5f5; padding: 20px; margin-top: 20px; border-radius: 5px; }}
                    .stat {{ margin: 10px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Password Reset {status_text}</h2>
                        <p>Account: {username}</p>
                    </div>
                    <div class="content">
                        <p><strong>Status:</strong> {status_text}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if stats:
            html += f"""
                        <hr>
                        <h3>Account Statistics:</h3>
                        <div class="stat"><strong>Total Resets:</strong> {stats.get('total_resets', 0)}</div>
                        <div class="stat"><strong>Successful:</strong> {stats.get('successful_resets', 0)}</div>
                        <div class="stat"><strong>Failed:</strong> {stats.get('failed_resets', 0)}</div>
                        <div class="stat"><strong>Last Reset:</strong> {stats.get('last_reset', 'Never')}</div>
            """
        
        html += """
                    </div>
                    <div class="footer">
                        <p>Automated Password Reset System | Do not reply to this email</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html

    def send_batch_report(self, results: Dict):
        """
        Send email report of batch password resets.
        
        Args:
            results: Dictionary with reset results
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            self.logger.warning("Email credentials not configured, skipping report")
            return False

        try:
            subject = f"Batch Password Reset Report - {results.get('timestamp', datetime.now())}"
            
            html = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #2196F3; color: white; padding: 20px; border-radius: 5px; }}
                        .stats {{ background-color: #f5f5f5; padding: 20px; margin-top: 20px; border-radius: 5px; }}
                        .stat-item {{ display: inline-block; margin: 10px 20px; }}
                        .success {{ color: green; font-weight: bold; }}
                        .failed {{ color: red; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Batch Password Reset Report</h2>
                            <p>{results.get('timestamp', datetime.now())}</p>
                        </div>
                        <div class="stats">
                            <h3>Summary:</h3>
                            <div class="stat-item">
                                <strong>Total:</strong> {results.get('total', 0)}
                            </div>
                            <div class="stat-item">
                                <strong class="success">Successful:</strong> {results.get('successful', 0)}
                            </div>
                            <div class="stat-item">
                                <strong class="failed">Failed:</strong> {results.get('failed', 0)}
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Batch report sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send batch report: {str(e)}")
            return False
