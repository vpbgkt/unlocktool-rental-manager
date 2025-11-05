"""
Advanced Cloudflare Bypass using curl-cffi.

This module provides HTTP-level bypass using curl-cffi, which impersonates
real browsers and bypasses Cloudflare at the HTTP level without needing
to use Selenium/automation browser detection.
"""

import logging
from typing import Optional, Dict
from curl_cffi import requests
from curl_cffi.requests import Response
import json
import time

logger = logging.getLogger(__name__)


class CloudflareBypassHTTP:
    """HTTP-level Cloudflare bypass using curl-cffi."""
    
    # Impersonate modern Chrome browsers
    CHROME_VERSIONS = [
        "chrome120",  # Chrome 120
        "chrome119",  # Chrome 119
        "chrome118",  # Chrome 118
    ]
    
    @staticmethod
    def get_session(impersonate: str = "chrome120") -> requests.Session:
        """
        Create a curl-cffi session that impersonates a real browser.
        
        Args:
            impersonate: Browser to impersonate (default: chrome120)
            
        Returns:
            curl-cffi requests.Session object
        """
        session = requests.Session()
        # Default headers
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        return session
    
    @staticmethod
    def get_with_cloudflare_bypass(
        url: str,
        impersonate: str = "chrome120",
        timeout: int = 30,
        **kwargs
    ) -> Optional[Response]:
        """
        Make GET request with Cloudflare bypass.
        
        Args:
            url: URL to fetch
            impersonate: Browser to impersonate
            timeout: Request timeout in seconds
            **kwargs: Additional requests parameters
            
        Returns:
            Response object or None if failed
        """
        try:
            logger.info(f"🔓 Fetching {url} with curl-cffi (impersonating {impersonate})...")
            
            response = requests.get(
                url,
                impersonate=impersonate,
                timeout=timeout,
                **kwargs
            )
            
            # Check if Cloudflare challenge still appears
            if "challenge" in response.text.lower():
                logger.warning("⚠️  Cloudflare challenge detected in response")
                return None
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully bypassed Cloudflare! Status: {response.status_code}")
                return response
            else:
                logger.warning(f"⚠️  Unexpected status code: {response.status_code}")
                return response
                
        except Exception as e:
            logger.error(f"❌ Error fetching URL: {e}")
            return None
    
    @staticmethod
    def post_with_cloudflare_bypass(
        url: str,
        data: Dict = None,
        impersonate: str = "chrome120",
        timeout: int = 30,
        **kwargs
    ) -> Optional[Response]:
        """
        Make POST request with Cloudflare bypass.
        
        Args:
            url: URL to post to
            data: Data to post
            impersonate: Browser to impersonate
            timeout: Request timeout in seconds
            **kwargs: Additional requests parameters
            
        Returns:
            Response object or None if failed
        """
        try:
            logger.info(f"📤 Posting to {url} with curl-cffi...")
            
            response = requests.post(
                url,
                data=data,
                impersonate=impersonate,
                timeout=timeout,
                **kwargs
            )
            
            if response.status_code in [200, 302, 303, 307, 308]:
                logger.info(f"✅ POST successful! Status: {response.status_code}")
                return response
            else:
                logger.warning(f"⚠️  Unexpected status code: {response.status_code}")
                return response
                
        except Exception as e:
            logger.error(f"❌ Error posting to URL: {e}")
            return None
    
    @staticmethod
    def extract_csrf_token(html: str, pattern: str = None) -> Optional[str]:
        """
        Extract CSRF token from HTML.
        
        Args:
            html: HTML content
            pattern: Optional custom pattern to match
            
        Returns:
            CSRF token or None
        """
        if not pattern:
            # Try common patterns
            import re
            patterns = [
                r'name=["\']csrf["\']?\s+value=["\']([^"\']+)',
                r'name=["\']_token["\']?\s+value=["\']([^"\']+)',
                r'name=["\']authenticity_token["\']?\s+value=["\']([^"\']+)',
                r'csrf["\']?\s*:\s*["\']([^"\']+)',
            ]
            for p in patterns:
                match = re.search(p, html, re.IGNORECASE)
                if match:
                    token = match.group(1)
                    logger.info(f"✓ CSRF token extracted: {token[:20]}...")
                    return token
            return None
        else:
            import re
            match = re.search(pattern, html)
            return match.group(1) if match else None
    
    @staticmethod
    def test_cloudflare_bypass(test_url: str = "https://unlocktool.net") -> bool:
        """
        Test if curl-cffi can bypass Cloudflare for the given URL.
        
        Args:
            test_url: URL to test
            
        Returns:
            True if bypass successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("Testing Cloudflare bypass with curl-cffi...")
        logger.info("=" * 60)
        
        response = CloudflareBypassHTTP.get_with_cloudflare_bypass(test_url)
        
        if response:
            logger.info(f"\n✅ SUCCESS! Can access {test_url}")
            logger.info(f"   Status Code: {response.status_code}")
            logger.info(f"   Content Length: {len(response.text)} bytes")
            logger.info(f"   Contains login form: {'login' in response.text.lower()}")
            return True
        else:
            logger.error(f"\n❌ FAILED! Cannot bypass Cloudflare for {test_url}")
            return False


class UnlocktoolHTTPBot:
    """
    Unlocktool password reset using HTTP-level requests (curl-cffi).
    
    This bypasses both Cloudflare and Selenium detection.
    """
    
    def __init__(self, timeout: int = 45):
        """
        Initialize HTTP bot.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.session = CloudflareBypassHTTP.get_session()
        self.base_url = "https://unlocktool.net"
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to unlocktool.net using HTTP requests.
        
        Args:
            username: Account username
            password: Account password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.logger.info(f"🔐 Logging in as {username}...")
            
            # Step 1: Get login page to check for CSRF token
            self.logger.info("Step 1: Fetching login page...")
            response = CloudflareBypassHTTP.get_with_cloudflare_bypass(
                f"{self.base_url}/login",
                impersonate="chrome120",
                timeout=self.timeout
            )
            
            if not response:
                self.logger.error("Failed to fetch login page")
                return False
            
            # Step 2: Extract CSRF token if needed
            csrf_token = CloudflareBypassHTTP.extract_csrf_token(response.text)
            self.logger.info(f"CSRF Token: {csrf_token if csrf_token else 'Not required'}")
            
            # Step 3: Submit login form
            self.logger.info("Step 2: Submitting login credentials...")
            login_data = {
                "username": username,
                "password": password,
            }
            
            if csrf_token:
                login_data["csrf"] = csrf_token
            
            response = CloudflareBypassHTTP.post_with_cloudflare_bypass(
                f"{self.base_url}/login",
                data=login_data,
                impersonate="chrome120",
                timeout=self.timeout
            )
            
            if not response:
                self.logger.error("Failed to submit login")
                return False
            
            # Check if login successful
            if response.status_code in [200, 302, 303]:
                # Follow redirect if needed
                if response.status_code in [302, 303]:
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        self.logger.info(f"Following redirect to {redirect_url}")
                        response = CloudflareBypassHTTP.get_with_cloudflare_bypass(
                            redirect_url,
                            impersonate="chrome120",
                            timeout=self.timeout
                        )
                
                if response and "dashboard" in response.text.lower():
                    self.logger.info("✅ Login successful!")
                    return True
                elif response and "error" in response.text.lower():
                    self.logger.error("❌ Login failed - Invalid credentials")
                    return False
                else:
                    self.logger.warning("⚠️  Login status uncertain - continuing anyway")
                    return True
            else:
                self.logger.error(f"Login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def reset_password(self, new_password: str) -> bool:
        """
        Reset password to new value via HTTP requests.
        
        Args:
            new_password: New password to set
            
        Returns:
            True if reset successful, False otherwise
        """
        try:
            self.logger.info(f"🔄 Resetting password...")
            
            # Fetch password reset page
            response = CloudflareBypassHTTP.get_with_cloudflare_bypass(
                f"{self.base_url}/account/reset-password",
                impersonate="chrome120",
                timeout=self.timeout
            )
            
            if not response:
                self.logger.error("Failed to fetch password reset page")
                return False
            
            # Extract CSRF token
            csrf_token = CloudflareBypassHTTP.extract_csrf_token(response.text)
            
            # Submit password reset
            reset_data = {
                "new_password": new_password,
                "confirm_password": new_password,
            }
            
            if csrf_token:
                reset_data["csrf"] = csrf_token
            
            response = CloudflareBypassHTTP.post_with_cloudflare_bypass(
                f"{self.base_url}/account/reset-password",
                data=reset_data,
                impersonate="chrome120",
                timeout=self.timeout
            )
            
            if response and response.status_code in [200, 302, 303]:
                self.logger.info("✅ Password reset successful!")
                return True
            else:
                self.logger.error(f"Password reset failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Password reset error: {e}")
            return False


if __name__ == "__main__":
    # Test the bypass
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test Cloudflare bypass
    CloudflareBypassHTTP.test_cloudflare_bypass("https://unlocktool.net")
    
    print("\n" + "=" * 60)
    print("To use in password reset automation:")
    print("=" * 60)
    print("""
1. Modify src/password_reset_bot.py to use HTTP requests instead of Selenium
2. Or create a hybrid approach:
   - Use curl-cffi for login
   - Use Selenium only for password reset form (if needed)

Example:
    bot = UnlocktoolHTTPBot()
    if bot.login("vpbgkt", "api@1234"):
        bot.reset_password("NewPassword123!")
    """)
