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
                    return json.load(f)
            except Exception:
                pass
        
        # Default settings
        return {
            "game_folder": "",
            "window_geometry": None,
            "launch_delay": 3  # Default 3 seconds delay between launches
        }
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_game_folder(self):
        """Get the game folder path"""
        return self.settings.get("game_folder", "")
    
    def set_game_folder(self, path):
        """Set the game folder path"""
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
        return self.settings.get("window_geometry")
    
    def set_window_geometry(self, geometry):
        """Save window geometry"""
        self.settings["window_geometry"] = geometry
        self.save_settings()
    
    def get_launch_delay(self):
        """Get the launch delay in seconds"""
        return self.settings.get("launch_delay", 3)
    
    def set_launch_delay(self, delay):
        """Set the launch delay in seconds"""
        self.settings["launch_delay"] = max(1, min(30, delay))  # Clamp between 1-30 seconds
        self.save_settings()