"""Selenium-based password reset automation for unlocktool.net."""

import logging
import time
import os
from typing import Tuple
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)

from src.logger import setup_logging
from src.utils import PasswordValidator


class PasswordResetBot:
    """A bot to automate password resets on unlocktool.net."""

    def __init__(self, username: str, password: str, headless: bool = False, timeout: int = 30):
        """
        Initialize the password reset bot.
        
        Args:
            username: Account username or email
            password: Account password
            headless: Run Chrome in headless mode
            timeout: Timeout for element waits in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.use_uc = True  # Use undetected-chromedriver

        # User credentials
        self.username = username
        self.password = password
        self.new_password = None  # Will be set during password reset

    def _find_chrome_executable(self):
        """Finds the path to the Google Chrome executable."""
        possible_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found Chrome executable at: {path}")
                return path
        self.logger.error("Could not find chrome.exe in standard locations.")
        return None

    def _init_driver(self):
        """Initializes the WebDriver."""
        self.logger.info("Initializing WebDriver...")
        try:
            if self.use_uc:
                self.logger.info("Using undetected-chromedriver.")
                options = uc.ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                # Disable sandbox for compatibility
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                # Find Chrome binary location
                chrome_executable_path = self._find_chrome_executable()
                if not chrome_executable_path:
                    raise FileNotFoundError("Could not find Chrome executable. Please install Google Chrome.")

                self.driver = uc.Chrome(options=options, use_subprocess=True, browser_executable_path=chrome_executable_path)
            else:
                # This is the old code, kept for fallback
                self.logger.info("Using standard Selenium WebDriver.")
                options = ChromeOptions()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument("start-maximized")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

            self.driver.set_page_load_timeout(60)
            self.logger.info("WebDriver initialized successfully.")
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}", exc_info=True)
            raise

    def open_website(self, url: str = "https://unlocktool.net/") -> bool:
        """
        Open the website.
        
        Args:
            url: Website URL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._init_driver()
            self.logger.info(f"Opening URL: {url}")
            self.driver.get(url)
            time.sleep(2) # Wait for page to load
            return True
        except WebDriverException as e:
            self.logger.error(f"Failed to open URL: {str(e)}")
            return False

    def wait_for_cloudflare(self, timeout=90):
        """
        Wait for Cloudflare challenge to pass.
        This typically resolves automatically in non-headless mode.
        """
        self.logger.info("Waiting for Cloudflare challenge to pass...")
        start_time = time.time()
        try:
            self.logger.info("Checking for Cloudflare protection...")
            self.logger.info(f"   Current URL: {self.driver.current_url}")
            self.logger.info(f"   Page Title: {self.driver.title}")
            self.logger.info(f"   Browser visible: {not self.headless}")

            # Check if we are already on the login page
            if "login" in self.driver.current_url.lower() or "post-in" in self.driver.current_url.lower():
                self.logger.info("Already on the login page. No Cloudflare challenge detected.")
                return

            try:
                # More robust check for Cloudflare
                self.logger.info("Explicitly checking for Cloudflare challenge elements...")
                wait = WebDriverWait(self.driver, 10)
                wait.until(
                    EC.any_of(
                        EC.title_contains("Cloudflare"),
                        EC.presence_of_element_located((By.ID, "cf-challenge-running")),
                        EC.presence_of_element_located((By.ID, "cf-wrapper"))
                    )
                )
                
                self.logger.info("Cloudflare challenge detected. Waiting for it to be solved...")
                self.logger.info("   This can be automatic or may require manual intervention.")
                self.logger.info("   Please wait patiently. This can take up to 90 seconds.")

                # Wait for the challenge to be solved and the title to change
                WebDriverWait(self.driver, timeout).until(
                    EC.not_(EC.title_contains("Cloudflare"))
                )
                self.logger.info("Cloudflare challenge passed.")
                
                # Additional wait for the homepage to fully load
                self.logger.info("Waiting for homepage content to fully load...")
                time.sleep(5)
                
            except TimeoutException:
                # If the initial check for Cloudflare times out, we assume it's not there.
                self.logger.info("No Cloudflare challenge detected within the initial 10 seconds. Proceeding.")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while waiting for Cloudflare: {e}", exc_info=True)
                # For now, let's try to continue
                pass

        except TimeoutException:
            self.logger.warning("[WARN] Timeout waiting for Cloudflare challenge to resolve")
            self.logger.info(f"   Current URL after timeout: {self.driver.current_url}")
            # Still continue - might have passed
        except Exception as e:
            self.logger.error(f"Error checking Cloudflare: {e}", exc_info=True)
        finally:
            self.logger.info(f"Cloudflare check finished in {time.time() - start_time:.2f} seconds.")
            self.logger.info(f"Final URL after Cloudflare check: {self.driver.current_url}")
            time.sleep(3) # Add a small delay to stabilize the page

    def handle_recaptcha(self, two_captcha_api_key: str = None) -> bool:
        """
        Handle reCAPTCHA on the page.
        
        For FREE solution: Can use browser automation to detect and wait for manual solving,
        or implement free reCAPTCHA solving via 2captcha free trial.
        
        Args:
            two_captcha_api_key: Optional API key for 2captcha service
            
        Returns:
            True if reCAPTCHA is solved or not present, False otherwise
        """
        try:
            # Check if reCAPTCHA is present - wait up to 10 seconds for it to load
            self.logger.info("Checking for reCAPTCHA on the page...")
            try:
                recaptcha_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "g-recaptcha"))
                )
            except TimeoutException:
                self.logger.info("No reCAPTCHA detected on page")
                return True
            
            if not recaptcha_elements:
                self.logger.info("No reCAPTCHA detected on page")
                return True
            
            self.logger.warning("reCAPTCHA v2 detected - Manual intervention required")
            self.logger.info("Please solve the 'I'm not a robot' challenge now.")
            self.logger.info("The script will automatically continue once solved (max 60 seconds)...")
            
            # Wait for user to solve reCAPTCHA - check every second if it's solved
            max_wait_time = 60
            check_interval = 1
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                time.sleep(check_interval)
                elapsed_time += check_interval
                
                # Check if reCAPTCHA is solved by looking for the response token
                try:
                    is_solved = self.driver.execute_script(
                        "return document.getElementById('g-recaptcha-response') && "
                        "document.getElementById('g-recaptcha-response').value.length > 0;"
                    )
                    
                    if is_solved:
                        self.logger.info(f"reCAPTCHA solved successfully in {elapsed_time} seconds!")
                        return True
                except Exception as e:
                    # If we can't check, just continue waiting
                    pass
            
            # Timeout - check one last time
            try:
                is_solved = self.driver.execute_script(
                    "return document.getElementById('g-recaptcha-response') && "
                    "document.getElementById('g-recaptcha-response').value.length > 0;"
                )
                if is_solved:
                    self.logger.info("reCAPTCHA solved successfully")
                    return True
                else:
                    self.logger.warning(f"reCAPTCHA not solved within {max_wait_time} seconds")
                    return False
            except Exception:
                self.logger.warning(f"Could not verify reCAPTCHA status after {max_wait_time} seconds")
                return False
                
        except NoSuchElementException:
            self.logger.info("reCAPTCHA element not found")
            return True
        except Exception as e:
            self.logger.error(f"Error handling reCAPTCHA: {str(e)}")
            return False

    def login(self):
        """Logs into the website."""
        self.logger.info("Navigating to the login page...")
        self.driver.get("https://unlocktool.net/post-in/")
        
        # Handle reCAPTCHA before attempting to fill form
        self.handle_recaptcha()

        self.logger.info(f"Attempting to log in as user: {self.username}")
        try:
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            self.logger.info("Found username field.")
            username_field.send_keys(self.username)

            password_field = self.driver.find_element(By.NAME, 'password')
            self.logger.info("Found password field.")
            password_field.send_keys(self.password)

            # Click the login button
            login_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')
            self.logger.info("Found login button. Clicking...")
            login_button.click()

            # Wait for login success by looking for a logout link
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'logout')]"))
            )

            self.logger.info("Login successful (logout link found).")
            return True

        except (TimeoutException, NoSuchElementException) as e:
            # Check if there's an error message on the page
            try:
                error_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'correct username and password') or contains(text(), 'Invalid') or contains(text(), 'incorrect')]")
                if error_elements:
                    error_text = error_elements[0].text
                    self.logger.error(f"Login failed with error: {error_text}")
                    self.take_screenshot("login_error.png")
                    raise Exception(f"Login failed: Please enter a correct username and password")
            except Exception as ex:
                if "Please enter a correct username and password" in str(ex):
                    raise ex
            
            self.logger.error(f"Login failed. Could not confirm login within 20 seconds. Error: {e}", exc_info=True)
            self.take_screenshot("login_error.png")
            raise Exception("Login failed: Could not verify successful login")

    def reset_password(self) -> bool:
        """
        Reset the password to a new value.
        
        Args:
            new_password: New password to set
            
        Returns:
            True if reset successful, False otherwise
        """
        self.logger.info("Attempting to reset password...")
        try:
            # 1. Navigate to the change password page
            change_password_url = "https://unlocktool.net/password-change/"
            self.logger.info(f"Navigating to {change_password_url}")
            self.driver.get(change_password_url)

            # Wait for the form to be present by locating a unique element within it
            form = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//form[.//button[contains(text(), 'Change password')]]"))
            )
            self.logger.info("Password change form loaded.")

            # 2. Fill out the form
            self.new_password = PasswordValidator.generate_strong_password()
            self.logger.info(f"Generated new password: {self.new_password}")

            form.find_element(By.NAME, 'old_password').send_keys(self.password)
            self.logger.info("Filled old password.")
            form.find_element(By.NAME, 'new_password1').send_keys(self.new_password)
            self.logger.info("Filled new password.")
            form.find_element(By.NAME, 'new_password2').send_keys(self.new_password)
            self.logger.info("Filled password confirmation.")

            # 3. Submit the form
            submit_button = form.find_element(By.XPATH, './/button[contains(text(), "Change password")]')
            self.logger.info("Submitting password change form...")
            submit_button.click()

            # 4. Wait for confirmation - look for success message or page change
            self.logger.info("Waiting for confirmation...")
            try:
                # Wait for either a success message or redirect
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Password change successful')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'password has been changed')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'successfully')]")),
                        EC.url_contains("/post-in/")
                    )
                )
                
                self.logger.info("Password reset successful!")
                self.logger.info(f"New password: {self.new_password}")
                return True
            except TimeoutException:
                # Even if we timeout, check the current URL - sometimes it redirects anyway
                if "/post-in/" in self.driver.current_url or "login" in self.driver.current_url:
                    self.logger.info("Password reset successful (redirected to login page).")
                    self.logger.info(f"New password: {self.new_password}")
                    return True
                else:
                    self.logger.error("Could not confirm password reset success.")
                    self.take_screenshot("password_reset_error.png")
                    return False

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Failed to confirm password reset. Error: {e}", exc_info=True)
            self.take_screenshot("password_reset_error.png")
            return False

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")

    def take_screenshot(self, filename: str = "screenshot.png"):
        """
        Take a screenshot for debugging.
        
        Args:
            filename: Screenshot filename
        """
        if self.driver:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        try:
            self.close()
        except OSError as e:
            if "The handle is invalid" not in str(e):
                self.logger.error(f"Error during browser close: {e}")
