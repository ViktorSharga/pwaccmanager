"""Account management module"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional

from utils.app_paths import get_accounts_file_path, ensure_data_dir_exists


class Account:
    def __init__(self, login: str, password: str, character_name: str = "", 
                 description: str = "", owner: str = ""):
        self.login = login
        self.password = password
        self.character_name = character_name
        self.description = description
        self.owner = owner
        self.pid = None  # Process ID when running
    
    def to_dict(self):
        """Convert account to dictionary"""
        return {
            "login": self.login,
            "password": self.password,
            "character_name": self.character_name,
            "description": self.description,
            "owner": self.owner
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create account from dictionary"""
        return cls(
            login=data.get("login", ""),
            password=data.get("password", ""),
            character_name=data.get("character_name", ""),
            description=data.get("description", ""),
            owner=data.get("owner", "")
        )


class AccountManager:
    def __init__(self):
        ensure_data_dir_exists()
        self.accounts_file = get_accounts_file_path()
        self.accounts: List[Account] = []
        self.load_accounts()
    
    def load_accounts(self):
        """Load accounts from file"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = [Account.from_dict(acc) for acc in data]
            except Exception as e:
                print(f"Error loading accounts: {e}")
                self.accounts = []
        else:
            self.accounts = []
    
    def save_accounts(self):
        """Save accounts to file"""
        try:
            data = [acc.to_dict() for acc in self.accounts]
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False
    
    def add_account(self, account: Account) -> bool:
        """Add a new account"""
        # Check for duplicate login
        if any(acc.login == account.login for acc in self.accounts):
            return False
        
        self.accounts.append(account)
        self.save_accounts()
        return True
    
    def update_account(self, old_login: str, account: Account) -> bool:
        """Update an existing account"""
        # Find the account to update
        for i, acc in enumerate(self.accounts):
            if acc.login == old_login:
                # Check for duplicate login (if login changed)
                if old_login != account.login:
                    if any(a.login == account.login for a in self.accounts):
                        return False
                
                self.accounts[i] = account
                self.save_accounts()
                return True
        return False
    
    def delete_account(self, login: str) -> bool:
        """Delete an account by login"""
        for i, acc in enumerate(self.accounts):
            if acc.login == login:
                del self.accounts[i]
                self.save_accounts()
                return True
        return False
    
    def get_account(self, login: str) -> Optional[Account]:
        """Get account by login"""
        for acc in self.accounts:
            if acc.login == login:
                return acc
        return None
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return self.accounts
    
    def login_exists(self, login: str) -> bool:
        """Check if login already exists"""
        return any(acc.login == login for acc in self.accounts)