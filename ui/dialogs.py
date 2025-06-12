"""Dialog windows for the application"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QFileDialog, QDialogButtonBox, QSpinBox, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os

from core.account_manager import Account
from utils.validators import (validate_login, validate_password, 
                            validate_character_name, validate_description,
                            validate_owner, validate_server)


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
        self.set_dialog_icon()
        
        self.setup_ui()
        self.setup_styling()
        
        if account:
            self.load_account_data()
    
    def set_dialog_icon(self):
        """Set the dialog icon"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
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
        
        # Server field
        self.server_combo = QComboBox()
        self.server_combo.addItems(["Main", "X"])
        self.server_combo.setCurrentText("Main")
        form_layout.addRow("Server:", self.server_combo)
        
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
            self.server_combo.setCurrentText(getattr(self.account, 'server', 'Main'))
    
    def validate_and_accept(self):
        """Validate input and accept if valid"""
        # Get values
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        character = self.character_edit.text().strip()
        description = self.description_edit.text().strip()
        owner = self.owner_edit.text().strip()
        server = self.server_combo.currentText()
        
        # Validate login
        valid, msg = validate_login(login)
        if not valid:
            self.show_message("warning", "Invalid Login", msg)
            self.login_edit.setFocus()
            return
        
        # Check for duplicate login
        if login != self.original_login and login in self.existing_logins:
            self.show_message("warning", "Duplicate Login", 
                              "An account with this login already exists.")
            self.login_edit.setFocus()
            return
        
        # Validate password
        valid, msg = validate_password(password)
        if not valid:
            self.show_message("warning", "Invalid Password", msg)
            self.password_edit.setFocus()
            return
        
        # Validate optional fields
        for value, validator, field_name in [
            (character, validate_character_name, "Character Name"),
            (description, validate_description, "Description"),
            (owner, validate_owner, "Owner"),
            (server, validate_server, "Server")
        ]:
            valid, msg = validator(value)
            if not valid:
                self.show_message("warning", f"Invalid {field_name}", msg)
                return
        
        # Create account object
        self.account = Account(login, password, character, description, owner, server)
        self.accept()
    
    def show_message(self, msg_type, title, text):
        """Show a styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        
        # Apply consistent styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fafafa;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                min-width: 300px;
            }
            QMessageBox QLabel {
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                margin: 10px;
            }
            QMessageBox QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
                margin: 2px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976d2;
                color: #ffffff;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1565c0;
                color: #ffffff;
            }
        """)
        
        msg_box.exec()
    
    def get_account(self):
        """Get the account object"""
        return self.account
    
    def setup_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
            }
            QLabel {
                color: #212121;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                selection-background-color: #2196f3;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                color: #212121;
            }
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                min-width: 100px;
            }
            QComboBox:focus {
                border-color: #2196f3;
                color: #212121;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 5px;
            }
            QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976d2;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1565c0;
                color: #ffffff;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.set_dialog_icon()
        
        self.setup_ui()
        self.setup_styling()
        self.load_settings()
    
    def set_dialog_icon(self):
        """Set the dialog icon"""
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
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
        
        # Launch delay setting
        delay_layout = QHBoxLayout()
        
        delay_layout.addWidget(QLabel("Launch Delay:"))
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(1)
        self.delay_spinbox.setMaximum(30)
        self.delay_spinbox.setSuffix(" seconds")
        self.delay_spinbox.setToolTip("Delay between consecutive game launches when launching multiple accounts (1-30 seconds). Single launches are immediate.")
        delay_layout.addWidget(self.delay_spinbox)
        
        delay_layout.addStretch()
        layout.addLayout(delay_layout)
        
        # Delay info label
        delay_info = QLabel("Time to wait between launching multiple accounts (single launches are immediate)")
        delay_info.setStyleSheet("color: gray;")
        layout.addWidget(delay_info)
        
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
            
            delay = self.settings_manager.get_launch_delay()
            self.delay_spinbox.setValue(delay)
    
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
            self.show_message("warning", "No Folder Selected", 
                              "Please select the game folder.")
            return
        
        if not self.settings_manager.is_valid_game_folder(folder):
            self.show_message("warning", "Invalid Game Folder", 
                              "The selected folder does not contain elementclient.exe")
            return
        
        # Save settings
        self.settings_manager.set_game_folder(folder)
        self.settings_manager.set_launch_delay(self.delay_spinbox.value())
        self.accept()
    
    def show_message(self, msg_type, title, text):
        """Show a styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        if msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        
        # Apply consistent styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #fafafa;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                min-width: 300px;
            }
            QMessageBox QLabel {
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                margin: 10px;
            }
            QMessageBox QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
                margin: 2px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976d2;
                color: #ffffff;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1565c0;
                color: #ffffff;
            }
        """)
        
        msg_box.exec()
    
    def setup_styling(self):
        """Apply modern styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
            }
            QLabel {
                color: #212121;
                font-weight: 600;
                font-size: 13px;
            }
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                color: #212121;
            }
            QLineEdit:read-only {
                background-color: #f5f5f5;
                color: #666666;
            }
            QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                background-color: #ffffff;
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }
            QSpinBox:focus {
                border-color: #2196f3;
                color: #212121;
            }
            QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976d2;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1565c0;
                color: #ffffff;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)