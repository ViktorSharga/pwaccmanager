"""Batch file generation and parsing module"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, List
import uuid


class BatchGenerator:
    def __init__(self, game_folder: str):
        self.game_folder = game_folder
    
    def generate_batch_file(self, login: str, password: str, character_name: str = "",
                          owner: str = "", description: str = "") -> Optional[str]:
        """Generate a batch file for an account"""
        if not self.game_folder or not os.path.exists(self.game_folder):
            return None
        
        # Create safe filename
        safe_login = re.sub(r'[^\w\-_]', '_', login)
        filename = f"account_{safe_login}.bat"
        filepath = os.path.join(self.game_folder, filename)
        
        # If file exists, use UUID
        if os.path.exists(filepath):
            filename = f"account_{uuid.uuid4().hex[:8]}.bat"
            filepath = os.path.join(self.game_folder, filename)
        
        # Build batch content
        content = "chcp 1251\n"
        content += f"start elementclient.exe startbypatcher user:{login} pwd:{password}"
        
        if character_name:
            content += f" role:{character_name}"
        
        content += "\n"
        
        if owner:
            content += f":: Owner: {owner}\n"
        
        if description:
            content += f":: Description: {description}\n"
        
        try:
            with open(filepath, 'w', encoding='cp1251') as f:
                f.write(content)
            return filepath
        except Exception as e:
            print(f"Error creating batch file: {e}")
            return None
    
    def parse_batch_file(self, filepath: str) -> Optional[Dict[str, str]]:
        """Parse a batch file and extract account information"""
        try:
            with open(filepath, 'r', encoding='cp1251') as f:
                content = f.read()
        except:
            # Try UTF-8 if cp1251 fails
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                return None
        
        # Extract login, password, and character name
        match = re.search(r'user:(\S+)\s+pwd:(\S+)(?:\s+role:(\S+))?', content)
        if not match:
            return None
        
        result = {
            "login": match.group(1),
            "password": match.group(2),
            "character_name": match.group(3) or "",
            "owner": "",
            "description": ""
        }
        
        # Extract owner from comment
        owner_match = re.search(r'::\s*Owner:\s*(.+)$', content, re.MULTILINE)
        if owner_match:
            result["owner"] = owner_match.group(1).strip()
        
        # Extract description from comment
        desc_match = re.search(r'::\s*Description:\s*(.+)$', content, re.MULTILINE)
        if desc_match:
            result["description"] = desc_match.group(1).strip()
        
        return result
    
    def scan_folder(self, folder: str = None) -> List[Dict[str, str]]:
        """Scan folder for batch files and parse them"""
        scan_folder = folder or self.game_folder
        if not scan_folder or not os.path.exists(scan_folder):
            return []
        
        accounts = []
        
        # Walk through directory and subdirectories
        for root, dirs, files in os.walk(scan_folder):
            for file in files:
                if file.lower().endswith('.bat'):
                    filepath = os.path.join(root, file)
                    account_data = self.parse_batch_file(filepath)
                    if account_data:
                        accounts.append(account_data)
        
        return accounts
    
    def delete_batch_file(self, login: str) -> bool:
        """Delete batch file for a specific account"""
        if not self.game_folder:
            return False
        
        # Look for batch files that might contain this login
        for file in os.listdir(self.game_folder):
            if file.endswith('.bat'):
                filepath = os.path.join(self.game_folder, file)
                account_data = self.parse_batch_file(filepath)
                if account_data and account_data.get('login') == login:
                    try:
                        os.remove(filepath)
                        return True
                    except:
                        pass
        
        return False