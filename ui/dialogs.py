"""Dialog windows for the application"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QFileDialog, QDialogButtonBox)
from PySide6.QtCore import Qt

from core.account_manager import Account
from utils.validators import (validate_login, validate_password, 
                            validate_character_name, validate_description,
                            validate_owner)


class AccountDialog(QDialog):
    """Dialog for adding/editing accounts"""
    
    def __init__(self, parent=None, account=None, existing_logins=None):
        super().__init__(parent)
        self.account = account
        self.existing_logins = existing_logins or []
        self.original_login = account.login if account else None
        
        self.setWindowTitle("Edit Account" if account else "Add Account")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
        if account:
            self.load_account_data()
    
    def setup_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Login field
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Required - must be unique")
        form_layout.addRow("Login:", self.login_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Required")
        form_layout.addRow("Password:", self.password_edit)
        
        # Character name field
        self.character_edit = QLineEdit()
        self.character_edit.setPlaceholderText("Optional")
        form_layout.addRow("Character Name:", self.character_edit)
        
        # Description field
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Optional")
        form_layout.addRow("Description:", self.description_edit)
        
        # Owner field
        self.owner_edit = QLineEdit()
        self.owner_edit.setPlaceholderText("Optional")
        form_layout.addRow("Owner:", self.owner_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_account_data(self):
        """Load existing account data into fields"""
        if self.account:
            self.login_edit.setText(self.account.login)
            self.password_edit.setText(self.account.password)
            self.character_edit.setText(self.account.character_name)
            self.description_edit.setText(self.account.description)
            self.owner_edit.setText(self.account.owner)
    
    def validate_and_accept(self):
        """Validate input and accept if valid"""
        # Get values
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        character = self.character_edit.text().strip()
        description = self.description_edit.text().strip()
        owner = self.owner_edit.text().strip()
        
        # Validate login
        valid, msg = validate_login(login)
        if not valid:
            QMessageBox.warning(self, "Invalid Login", msg)
            self.login_edit.setFocus()
            return
        
        # Check for duplicate login
        if login != self.original_login and login in self.existing_logins:
            QMessageBox.warning(self, "Duplicate Login", 
                              "An account with this login already exists.")
            self.login_edit.setFocus()
            return
        
        # Validate password
        valid, msg = validate_password(password)
        if not valid:
            QMessageBox.warning(self, "Invalid Password", msg)
            self.password_edit.setFocus()
            return
        
        # Validate optional fields
        for value, validator, field_name in [
            (character, validate_character_name, "Character Name"),
            (description, validate_description, "Description"),
            (owner, validate_owner, "Owner")
        ]:
            valid, msg = validator(value)
            if not valid:
                QMessageBox.warning(self, f"Invalid {field_name}", msg)
                return
        
        # Create account object
        self.account = Account(login, password, character, description, owner)
        self.accept()
    
    def get_account(self):
        """Get the account object"""
        return self.account


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Create the settings dialog UI"""
        layout = QVBoxLayout()
        
        # Game folder selection
        folder_layout = QHBoxLayout()
        
        folder_layout.addWidget(QLabel("Game Folder:"))
        
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        folder_layout.addWidget(self.folder_edit)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        
        layout.addLayout(folder_layout)
        
        # Info label
        info_label = QLabel("The game folder must contain elementclient.exe")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        # Add stretch
        layout.addStretch()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load current settings"""
        if self.settings_manager:
            folder = self.settings_manager.get_game_folder()
            self.folder_edit.setText(folder)
    
    def browse_folder(self):
        """Open folder browser dialog"""
        current_folder = self.folder_edit.text()
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Perfect World Game Folder",
            current_folder,
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.folder_edit.setText(folder)
    
    def validate_and_accept(self):
        """Validate settings and save"""
        folder = self.folder_edit.text()
        
        if not folder:
            QMessageBox.warning(self, "No Folder Selected", 
                              "Please select the game folder.")
            return
        
        if not self.settings_manager.is_valid_game_folder(folder):
            QMessageBox.warning(self, "Invalid Game Folder", 
                              "The selected folder does not contain elementclient.exe")
            return
        
        # Save settings
        self.settings_manager.set_game_folder(folder)
        self.accept()