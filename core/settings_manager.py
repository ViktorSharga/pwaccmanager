"""Settings management module"""

import json
import os
from pathlib import Path

from utils.app_paths import get_settings_file_path, ensure_data_dir_exists


class SettingsManager:
    def __init__(self):
        ensure_data_dir_exists()
        self.settings_file = get_settings_file_path()
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or create default settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    print(f"Settings loaded from: {self.settings_file}")  # Keep this for verification
                    return settings
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading settings: {e}")
                print(f"Backing up corrupted settings file and creating new one")
                # Backup the corrupted file
                try:
                    backup_path = self.settings_file.with_suffix('.json.backup')
                    self.settings_file.rename(backup_path)
                    print(f"Corrupted settings backed up to: {backup_path}")
                except Exception:
                    pass
        
        # Default settings
        default_settings = {
            "game_folder": "",
            "window_geometry": None,
            "launch_delay": 3  # Default 3 seconds delay between launches
        }
        print("Using default settings")
        return default_settings
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            print(f"Settings saved to: {self.settings_file}")  # Keep this for verification
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_game_folder(self):
        """Get the game folder path"""
        return self.settings.get("game_folder", "")
    
    def set_game_folder(self, path):
        """Set the game folder path"""
        print(f"Setting game folder to: {path}")  # Keep this for verification
        self.settings["game_folder"] = path
        self.save_settings()
    
    def is_valid_game_folder(self, path):
        """Check if the folder contains elementclient.exe"""
        if not path or not os.path.exists(path):
            return False
        
        exe_path = os.path.join(path, "elementclient.exe")
        return os.path.exists(exe_path)
    
    def get_window_geometry(self):
        """Get saved window geometry"""
        geometry_data = self.settings.get("window_geometry")
        if geometry_data and isinstance(geometry_data, list):
            # Convert list back to QByteArray
            from PySide6.QtCore import QByteArray
            return QByteArray(bytes(geometry_data))
        return geometry_data
    
    def set_window_geometry(self, geometry):
        """Save window geometry"""
        # Convert QByteArray to bytes for JSON serialization
        if hasattr(geometry, 'data'):
            # It's a QByteArray, convert to bytes then to list for JSON
            geometry_data = list(geometry.data())
        else:
            geometry_data = geometry
        
        # Debug info for troubleshooting
        if geometry:
            print(f"Saving window geometry (type: {type(geometry)})")
        self.settings["window_geometry"] = geometry_data
        self.save_settings()
    
    def get_launch_delay(self):
        """Get the launch delay in seconds"""
        return self.settings.get("launch_delay", 3)
    
    def set_launch_delay(self, delay):
        """Set the launch delay in seconds"""
        self.settings["launch_delay"] = max(1, min(30, delay))  # Clamp between 1-30 seconds
        self.save_settings()