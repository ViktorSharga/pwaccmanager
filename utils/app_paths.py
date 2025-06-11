"""Application path utilities for handling data storage in both development and compiled environments"""

import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Get the appropriate data directory for the application.
    
    Returns different paths depending on whether running from source or compiled exe:
    - Development: Current working directory
    - Compiled exe: User's AppData/Local directory on Windows
    
    Returns:
        Path: The directory where application data should be stored
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform == 'win32':
            # Use AppData/Local on Windows
            app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            data_dir = Path(app_data) / 'PerfectWorldAccountManager'
        else:
            # Use home directory on other platforms
            data_dir = Path.home() / '.perfect_world_account_manager'
        
        # Create directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    else:
        # Running from source - use current directory
        return Path.cwd()


def get_settings_file_path() -> Path:
    """Get the full path to the settings file"""
    return get_app_data_dir() / 'settings.json'


def get_accounts_file_path() -> Path:
    """Get the full path to the accounts file"""
    return get_app_data_dir() / 'accounts.json'


def ensure_data_dir_exists():
    """Ensure the application data directory exists"""
    data_dir = get_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir