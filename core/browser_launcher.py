"""Browser launcher module for auto-login functionality"""

import os
import sys
import subprocess
import time
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path


class BrowserLauncher:
    """Handles launching browsers with auto-login functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.login_url = "https://asgard.pw/lk/"
        
        # Browser paths for different operating systems
        self.browser_paths = {
            'chrome': self._get_chrome_paths(),
            'firefox': self._get_firefox_paths(),
            'edge': self._get_edge_paths()
        }
        
        # Track launched browser processes
        self.launched_processes = []
    
    def _get_chrome_paths(self) -> List[str]:
        """Get possible Chrome installation paths"""
        if sys.platform == "win32":
            return [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
        elif sys.platform == "darwin":
            return [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        else:  # Linux
            return [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser"
            ]
    
    def _get_firefox_paths(self) -> List[str]:
        """Get possible Firefox installation paths"""
        if sys.platform == "win32":
            return [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
        elif sys.platform == "darwin":
            return [
                "/Applications/Firefox.app/Contents/MacOS/firefox"
            ]
        else:  # Linux
            return [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr"
            ]
    
    def _get_edge_paths(self) -> List[str]:
        """Get possible Edge installation paths"""
        if sys.platform == "win32":
            return [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        elif sys.platform == "darwin":
            return [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        else:  # Linux
            return [
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable"
            ]
    
    def detect_available_browsers(self) -> List[str]:
        """Detect which browsers are installed on the system"""
        available = []
        
        for browser, paths in self.browser_paths.items():
            for path in paths:
                if os.path.exists(path):
                    available.append(browser)
                    self.logger.info(f"Found {browser} at: {path}")
                    break
        
        return available
    
    def get_browser_executable(self, browser: str) -> Optional[str]:
        """Get the executable path for a specific browser"""
        if browser not in self.browser_paths:
            return None
        
        for path in self.browser_paths[browser]:
            if os.path.exists(path):
                return path
        
        return None
    
    def launch_browser_simple(self, browser: str, username: str, password: str) -> bool:
        """Launch browser in incognito mode with URL (Phase 1 implementation)"""
        try:
            executable = self.get_browser_executable(browser)
            if not executable:
                self.logger.error(f"Browser {browser} not found")
                return False
            
            # Build command based on browser type
            cmd = self._build_browser_command(browser, executable, username)
            
            if not cmd:
                return False
            
            # Launch browser
            process = subprocess.Popen(cmd, shell=False)
            self.launched_processes.append(process)
            
            self.logger.info(f"Launched {browser} for user {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch {browser}: {e}")
            return False
    
    def _build_browser_command(self, browser: str, executable: str, username: str) -> Optional[List[str]]:
        """Build browser command with appropriate flags"""
        url = self.login_url
        
        if browser == "chrome":
            # Create temporary user data directory for isolation
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'pwam_chrome_{username}')
            
            cmd = [
                executable,
                "--incognito",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-popup-blocking",
                f"--user-data-dir={temp_dir}",
                url
            ]
            
        elif browser == "firefox":
            cmd = [
                executable,
                "-private-window",
                url
            ]
            
        elif browser == "edge":
            # Create temporary user data directory for isolation
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'pwam_edge_{username}')
            
            cmd = [
                executable,
                "--inprivate",
                "--no-default-browser-check",
                "--disable-extensions",
                f"--user-data-dir={temp_dir}",
                url
            ]
        else:
            self.logger.error(f"Unsupported browser: {browser}")
            return None
        
        return cmd
    
    def launch_browser_with_autofill(self, browser: str, username: str, password: str) -> bool:
        """Launch browser with Selenium auto-fill (Phase 2+ implementation)"""
        try:
            # Check if selenium is available
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.common.exceptions import TimeoutException, WebDriverException
            except ImportError:
                self.logger.warning("Selenium not available, falling back to simple launch")
                return self.launch_browser_simple(browser, username, password)
            
            driver = None
            
            if browser == "chrome":
                driver = self._create_chrome_driver(username)
            elif browser == "firefox":
                driver = self._create_firefox_driver(username)
            elif browser == "edge":
                driver = self._create_edge_driver(username)
            
            if not driver:
                return False
            
            # Navigate and auto-fill
            success = self._auto_fill_login(driver, username, password)
            
            if success:
                self.logger.info(f"Successfully launched {browser} with auto-fill for {username}")
                # Don't close the driver - let user continue browsing
                return True
            else:
                if driver:
                    driver.quit()
                return False
                
        except Exception as e:
            self.logger.error(f"Auto-fill launch failed: {e}")
            return self.launch_browser_simple(browser, username, password)
    
    def _create_chrome_driver(self, username: str):
        """Create Chrome WebDriver with appropriate options"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--incognito")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            
            # Create isolated user data directory
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'pwam_chrome_{username}')
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Try to find Chrome executable
            chrome_path = self.get_browser_executable('chrome')
            if chrome_path:
                options.binary_location = chrome_path
            
            driver = webdriver.Chrome(options=options)
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {e}")
            return None
    
    def _create_firefox_driver(self, username: str):
        """Create Firefox WebDriver with appropriate options"""
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.options import Options
            from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
            
            options = Options()
            options.add_argument("-private")
            
            # Create private profile
            profile = FirefoxProfile()
            profile.set_preference("browser.privatebrowsing.autostart", True)
            profile.set_preference("browser.cache.disk.enable", False)
            profile.set_preference("browser.cache.memory.enable", False)
            profile.set_preference("browser.cache.offline.enable", False)
            
            # Try to find Firefox executable
            firefox_path = self.get_browser_executable('firefox')
            if firefox_path:
                options.binary_location = firefox_path
            
            driver = webdriver.Firefox(options=options, firefox_profile=profile)
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create Firefox driver: {e}")
            return None
    
    def _create_edge_driver(self, username: str):
        """Create Edge WebDriver with appropriate options"""
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options
            
            options = Options()
            options.add_argument("--inprivate")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            
            # Create isolated user data directory
            temp_dir = os.path.join(os.environ.get('TEMP', '/tmp'), f'pwam_edge_{username}')
            options.add_argument(f"--user-data-dir={temp_dir}")
            
            # Try to find Edge executable
            edge_path = self.get_browser_executable('edge')
            if edge_path:
                options.binary_location = edge_path
            
            driver = webdriver.Edge(options=options)
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create Edge driver: {e}")
            return None
    
    def _auto_fill_login(self, driver, username: str, password: str) -> bool:
        """Navigate to login page and auto-fill credentials"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            # Navigate to login page
            self.logger.info(f"Navigating to {self.login_url}")
            driver.get(self.login_url)
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Try different common field names/IDs for username
            username_selectors = [
                (By.NAME, "username"),
                (By.NAME, "login"),
                (By.NAME, "email"),
                (By.ID, "username"),
                (By.ID, "login"),
                (By.ID, "email"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[type='email']")
            ]
            
            username_field = None
            for selector_type, selector_value in username_selectors:
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                self.logger.error("Could not find username field")
                return False
            
            # Fill username
            username_field.clear()
            username_field.send_keys(username)
            self.logger.info("Username field filled")
            
            # Try different common field names/IDs for password
            password_selectors = [
                (By.NAME, "password"),
                (By.NAME, "pass"),
                (By.ID, "password"),
                (By.ID, "pass"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]
            
            password_field = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = driver.find_element(selector_type, selector_value)
                    break
                except:
                    continue
            
            if not password_field:
                self.logger.error("Could not find password field")
                return False
            
            # Fill password
            password_field.clear()
            password_field.send_keys(password)
            self.logger.info("Password field filled")
            
            # Do NOT submit - let user review and click login
            self.logger.info(f"Auto-filled login form for {username} - ready for user review")
            return True
            
        except Exception as e:
            self.logger.error(f"Auto-fill failed: {e}")
            return False
    
    def launch_account_browser(self, username: str, password: str, preferred_browser: str = "auto") -> tuple[bool, str]:
        """Main method to launch browser for an account"""
        if not username or not password:
            error_msg = self.get_error_message('credentials_missing')
            self.logger.error(error_msg)
            return False, error_msg
        
        # Validate URL is HTTPS
        if not self.login_url.startswith('https://'):
            error_msg = "Login URL must use HTTPS for security"
            self.logger.error(error_msg)
            return False, error_msg
        
        # Detect available browsers
        available_browsers = self.detect_available_browsers()
        
        if not available_browsers:
            error_msg = self.get_error_message('browser_not_found')
            self.logger.error(error_msg)
            return False, error_msg
        
        # Choose browser
        if preferred_browser == "auto" or preferred_browser not in available_browsers:
            # Use first available browser (preference order: chrome, firefox, edge)
            browser_preference = ["chrome", "firefox", "edge"]
            browser = None
            for pref in browser_preference:
                if pref in available_browsers:
                    browser = pref
                    break
            
            if not browser:
                browser = available_browsers[0]
        else:
            browser = preferred_browser
        
        self.logger.info(f"Using browser: {browser}")
        
        # Try auto-fill first, fall back to simple launch
        success = self.launch_browser_with_autofill(browser, username, password)
        if success:
            return True, f"Browser launched successfully with {browser.title()}"
        else:
            return False, self.get_error_message('launch_failed')
    
    def cleanup_temp_profiles(self):
        """Clean up temporary browser profiles"""
        try:
            import shutil
            
            temp_base = os.environ.get('TEMP', '/tmp')
            
            # Clean up Chrome profiles
            chrome_pattern = os.path.join(temp_base, 'pwam_chrome_*')
            for path in Path(temp_base).glob('pwam_chrome_*'):
                if path.is_dir():
                    try:
                        shutil.rmtree(path)
                        self.logger.info(f"Cleaned up Chrome profile: {path}")
                    except Exception as e:
                        self.logger.warning(f"Could not clean up {path}: {e}")
            
            # Clean up Edge profiles
            for path in Path(temp_base).glob('pwam_edge_*'):
                if path.is_dir():
                    try:
                        shutil.rmtree(path)
                        self.logger.info(f"Cleaned up Edge profile: {path}")
                    except Exception as e:
                        self.logger.warning(f"Could not clean up {path}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Profile cleanup failed: {e}")
    
    def get_error_message(self, error_type: str) -> str:
        """Get user-friendly error messages"""
        error_messages = {
            'browser_not_found': "No supported browser found. Please install Chrome, Firefox, or Edge.",
            'driver_missing': "Browser driver not found. Auto-fill may not work properly.",
            'launch_failed': "Failed to launch browser. Please try again.",
            'page_timeout': "Login page took too long to load. Check your internet connection.",
            'form_not_found': "Could not find login form. The website may have changed.",
            'credentials_missing': "Username or password is missing for this account.",
            'selenium_missing': "Advanced features require Selenium. Using basic browser launch."
        }
        
        return error_messages.get(error_type, "An unknown error occurred.")