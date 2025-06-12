"""Main application window"""

from functools import partial

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QStatusBar, QMenu,
                             QCheckBox, QToolBar, QStyle, QApplication, QFileDialog,
                             QDialog, QVBoxLayout as QVBoxLayoutDialog, QListWidget,
                             QDialogButtonBox, QProgressBar, QLabel)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QIcon, QPixmap

import json
import os
from datetime import datetime

from core.account_manager import AccountManager, Account
from core.settings_manager import SettingsManager
from core.game_launcher import GameLauncher
from core.batch_generator import BatchGenerator
from ui.dialogs import AccountDialog, SettingsDialog


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.account_manager = AccountManager()
        self.game_launcher = None
        self.batch_generator = None
        
        # Initialize game folder dependent components
        self.init_game_components()
        
        # Setup UI
        self.setWindowTitle("Perfect World Account Manager")
        self.set_app_icon()
        self.setup_ui()
        self.load_accounts()
        
        # Ensure proper initial state
        self.update_welcome_screen_visibility()
        
        # Restore window geometry
        self.restore_geometry()
        
        # Setup process cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_processes)
        self.cleanup_timer.start(5000)  # Check every 5 seconds
    
    def init_game_components(self):
        """Initialize components that depend on game folder"""
        game_folder = self.settings_manager.get_game_folder()
        if game_folder:
            self.game_launcher = GameLauncher(game_folder)
            self.batch_generator = BatchGenerator(game_folder)
            
            # Apply launch delay setting
            if self.game_launcher:
                delay = self.settings_manager.get_launch_delay()
                self.game_launcher.set_launch_delay(delay)
    
    def set_app_icon(self):
        """Set the application icon"""
        # Try ICO file first (better Windows support), then fallback to SVG
        ico_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.ico')
        svg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.svg')
        
        icon_path = ico_path if os.path.exists(ico_path) else svg_path
        
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            
            # Set window icon (appears in title bar top-left corner)
            self.setWindowIcon(app_icon)
            
            # Also set for the application instance (taskbar, alt-tab, etc.)
            QApplication.instance().setWindowIcon(app_icon)
            
            # Force refresh the window icon display
            self.repaint()
            
            print(f"Window and app icon set from: {icon_path}")
        else:
            print(f"Warning: No icon file found at {ico_path} or {svg_path}")
    
    def setup_ui(self):
        """Create the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create table
        self.create_table()
        
        # Create welcome screen
        self.create_welcome_screen()
        
        # Add table and welcome widget to layout
        layout.addWidget(self.table)
        layout.addWidget(self.welcome_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
        # Set minimum size
        self.setMinimumSize(800, 400)
        
        # Apply modern theme to the main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QToolBar {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
                spacing: 6px;
            }
            QToolBar QToolButton {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 2px;
                font-weight: 600;
                font-size: 13px;
            }
            QToolBar QToolButton:hover {
                background-color: #e3f2fd;
                border-color: #2196f3;
                color: #1976d2;
            }
            QToolBar QToolButton:pressed {
                background-color: #bbdefb;
                color: #0d47a1;
            }
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
                color: #666666;
                font-size: 12px;
            }
            QCheckBox {
                spacing: 6px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #2196f3;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjMgNy43TDEuNCA0LjgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QLabel {
                color: #333333;
                font-weight: 500;
            }
        """)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Add Account button
        add_action = QAction("Add Account", self)
        add_action.triggered.connect(self.add_account)
        toolbar.addAction(add_action)
        
        # Launch Selected button
        launch_action = QAction("Launch Selected", self)
        launch_action.triggered.connect(self.launch_selected)
        toolbar.addAction(launch_action)
        
        # Close Selected button
        close_action = QAction("Close Selected", self)
        close_action.triggered.connect(self.close_selected)
        toolbar.addAction(close_action)
        
        # Scan Folder button
        scan_action = QAction("Scan Folder", self)
        scan_action.triggered.connect(self.scan_folder)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        # Import/Export buttons
        import_action = QAction("Import", self)
        import_action.triggered.connect(self.import_accounts)
        toolbar.addAction(import_action)
        
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_accounts)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        
        # No more select all in toolbar - will be in table header
    
    def create_welcome_screen(self):
        """Create welcome screen for when no accounts are loaded"""
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Perfect World Account Manager")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin: 20px;
            }
        """)
        welcome_layout.addWidget(welcome_label)
        
        # Instructions
        instructions = QLabel("""
        Get started by:
        • Adding your first account using the "Add Account" button
        • Importing accounts from a JSON file
        • Scanning your game folder for existing batch files
        • Configuring your game folder in Settings
        """)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                line-height: 1.6;
                margin: 10px;
            }
        """)
        welcome_layout.addWidget(instructions)
        
        # Quick action buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        add_button = QPushButton("Add First Account")
        add_button.clicked.connect(self.add_account)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        button_layout.addWidget(add_button)
        
        settings_button = QPushButton("Open Settings")
        settings_button.clicked.connect(self.open_settings)
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #2196f3;
                border: 2px solid #2196f3;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        button_layout.addWidget(settings_button)
        
        welcome_layout.addLayout(button_layout)
        
        self.welcome_widget.setLayout(welcome_layout)
        # Don't hide initially - let update_welcome_screen_visibility decide
    
    def show_message(self, msg_type, title, text, buttons=None):
        """Show a styled message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        if msg_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type == "question":
            msg_box.setIcon(QMessageBox.Question)
            if buttons:
                msg_box.setStandardButtons(buttons)
            else:
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
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
            QMessageBox QPushButton:default {
                background-color: #1976d2;
                color: #ffffff;
            }
        """)
        
        if msg_type == "question":
            return msg_box.exec()
        else:
            msg_box.exec()
            return None
    
    def create_table(self):
        """Create the accounts table"""
        self.table = QTableWidget()
        
        # Set columns
        columns = ["", "Login", "Password", "Character Name", "Description", "Owner", "Server", "Actions"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Create master checkbox in the header of first column
        self.create_header_checkbox()
        
        # Start with 0 rows - only add rows when accounts are added
        self.table.setRowCount(0)
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Disable editing for all items
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Connect cell click events for clipboard copy
        self.table.cellClicked.connect(self.on_table_cell_clicked)
        
        # Add modern styling for the table
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                selection-background-color: #e3f2fd;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #212121;
                font-weight: 500;
            }
            QTableWidget::item:hover {
                background-color: #f0f8ff;
                color: #212121;
            }
            QTableWidget::item:selected {
                background-color: #1976d2;
                color: #ffffff;
                font-weight: 600;
            }
            QTableWidget QHeaderView::section {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                padding: 8px;
                font-weight: bold;
                color: #212121;
                font-size: 13px;
            }
            QTableWidget QHeaderView::section:hover {
                background-color: #e0e0e0;
                color: #212121;
            }
            QTableWidget QHeaderView::section:first {
                text-align: center;
            }
        """)
        
        # Set column widths  
        header = self.table.horizontalHeader()
        header.resizeSection(0, 40)  # Checkbox column (for master checkbox)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Login
        header.resizeSection(2, 100)  # Password
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Character
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Owner
        header.resizeSection(6, 60)  # Server
        header.resizeSection(7, 120)  # Actions
        
        # Set row height to accommodate buttons (24px button + 16px padding)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setMinimumSectionSize(40)
        
        # Hide row numbers/vertical header
        self.table.verticalHeader().setVisible(False)
        
        # Initially hide table - let update_welcome_screen_visibility decide
        self.table.hide()
    
    def create_header_checkbox(self):
        """Create master checkbox in table header first column"""
        # Set up first column for checkbox
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().resizeSection(0, 40)
        
        # Create checkbox widget for the header
        self.master_checkbox = QCheckBox()
        self.master_checkbox.setToolTip("Select/Unselect all accounts")
        self.master_checkbox.stateChanged.connect(self.on_master_checkbox_changed)
        
        # Style the master checkbox
        self.master_checkbox.setStyleSheet("""
            QCheckBox {
                background-color: transparent;
                spacing: 0px;
                margin: 0px;
                padding: 0px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #2196f3;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjMgNy43TDEuNCA0LjgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
        
        # Create container widget for centering
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.addStretch()
        header_layout.addWidget(self.master_checkbox)
        header_layout.addStretch()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Try to set the widget for the first column header
        try:
            self.table.horizontalHeader().setSectionWidget(0, header_widget)
            print("Master checkbox created as header widget")
        except AttributeError:
            # Fallback: Use a different approach
            print("setSectionWidget not available, using alternative approach")
            self.create_header_checkbox_alternative()
    
    def create_header_checkbox_alternative(self):
        """Alternative method to create header checkbox"""
        # Set header text to checkbox symbol and handle clicks
        header = self.table.horizontalHeader()
        
        # Set the first column header to show a checkbox symbol
        self.master_checkbox_checked = False
        self.update_header_checkbox_symbol()
        
        # Connect header click to toggle function
        header.sectionClicked.connect(self.on_header_section_clicked)
        
        print("Alternative header checkbox created")
    
    def update_header_checkbox_symbol(self):
        """Update the header checkbox symbol"""
        symbol = "☑" if self.master_checkbox_checked else "☐"
        columns = ["", "Login", "Password", "Character Name", "Description", "Owner", "Server", "Actions"]
        columns[0] = symbol
        self.table.setHorizontalHeaderLabels(columns)
    
    def on_header_section_clicked(self, section):
        """Handle header section clicks"""
        if section == 0:  # First column (checkbox column)
            self.master_checkbox_checked = not self.master_checkbox_checked
            self.update_header_checkbox_symbol()
            # Trigger the checkbox action
            state = Qt.Checked if self.master_checkbox_checked else Qt.Unchecked
            self.on_master_checkbox_changed(state)
    
    def load_accounts(self):
        """Load accounts into the table"""
        accounts = self.account_manager.get_all_accounts()
        
        # Clear table completely
        self.table.setRowCount(0)
        self.table.clearContents()
        
        # Only add rows for actual accounts
        if accounts:
            for account in accounts:
                self.add_account_to_table(account)
        
        self.update_status_bar()
        self.update_welcome_screen_visibility()
        # Update master checkbox state
        QTimer.singleShot(100, self.update_master_checkbox_state)
    
    def add_account_to_table(self, account):
        """Add an account to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setFixedSize(20, 20)
        checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 0px;
                margin: 0px;
                padding: 0px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #2196f3;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjMgNy43TDEuNCA0LjgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
        # Connect checkbox to update master checkbox state
        checkbox.stateChanged.connect(lambda: self.update_master_checkbox_state())
        
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.addStretch()
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setSpacing(0)
        self.table.setCellWidget(row, 0, checkbox_widget)
        
        # Login (clickable for clipboard copy)
        login_item = QTableWidgetItem(account.login)
        login_item.setToolTip("Click to copy login to clipboard")
        login_item.setData(Qt.UserRole + 1, "login")  # Mark as login field
        login_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 1, login_item)
        
        # Password (masked, clickable for clipboard copy)
        password_item = QTableWidgetItem("••••••")
        password_item.setData(Qt.UserRole, account.password)
        password_item.setData(Qt.UserRole + 1, "password")  # Mark as password field
        password_item.setToolTip("Click to copy password to clipboard")
        password_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 2, password_item)
        
        # Character name
        character_item = QTableWidgetItem(account.character_name)
        character_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 3, character_item)
        
        # Description
        description_item = QTableWidgetItem(account.description)
        description_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 4, description_item)
        
        # Owner
        owner_item = QTableWidgetItem(account.owner)
        owner_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.table.setItem(row, 5, owner_item)
        
        # Server
        server_value = getattr(account, 'server', 'Main')
        server_item = QTableWidgetItem(server_value)
        server_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.table.setItem(row, 6, server_item)
        
        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 0, 5, 0)
        actions_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        
        # Play button
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(24, 24)
        play_btn.setToolTip("Launch game")
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: #ffffff;
                border: 1px solid #1b5e20;
                border-radius: 2px;
                font-size: 9px;
                font-weight: 900;
                font-family: Arial, sans-serif;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #388e3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
                color: #ffffff;
            }
        """)
        play_btn.clicked.connect(partial(self.launch_account, row))
        actions_layout.addWidget(play_btn)
        
        # Kill button
        kill_btn = QPushButton("✖")
        kill_btn.setFixedSize(24, 24)
        kill_btn.setToolTip("Close game")
        kill_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: #ffffff;
                border: 1px solid #b71c1c;
                border-radius: 2px;
                font-size: 9px;
                font-weight: 900;
                font-family: Arial, sans-serif;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f44336;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
                color: #ffffff;
            }
        """)
        kill_btn.clicked.connect(partial(self.close_account, row))
        actions_layout.addWidget(kill_btn)
        
        # Menu button
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(24, 24)
        menu_btn.setToolTip("More options")
        menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: #ffffff;
                border: 1px solid #0d47a1;
                border-radius: 2px;
                font-size: 10px;
                font-weight: 900;
                font-family: Arial, sans-serif;
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2196f3;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
                color: #ffffff;
            }
        """)
        
        # Create menu and connect it properly
        menu = QMenu(menu_btn)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        # Use partial to properly bind the row value
        edit_action.triggered.connect(partial(self.edit_account, row))
        delete_action.triggered.connect(partial(self.delete_account, row))
        
        # Connect button click to show menu - use partial to capture menu
        menu_btn.clicked.connect(partial(self.show_row_menu, menu))
        actions_layout.addWidget(menu_btn)
        
        self.table.setCellWidget(row, 7, actions_widget)
        
        # Store account reference
        self.table.item(row, 1).setData(Qt.UserRole, account)
    
    def show_row_menu(self, menu):
        """Show the row context menu"""
        menu.exec_(QCursor.pos())
    
    def add_account(self):
        """Show add account dialog"""
        existing_logins = [acc.login for acc in self.account_manager.get_all_accounts()]
        dialog = AccountDialog(self, existing_logins=existing_logins)
        
        if dialog.exec():
            account = dialog.get_account()
            if self.account_manager.add_account(account):
                # Generate batch file
                if self.batch_generator:
                    self.batch_generator.generate_batch_file(
                        account.login, account.password, account.character_name,
                        account.owner, account.description
                    )
                
                self.add_account_to_table(account)
                self.update_status_bar()
                self.update_master_checkbox_state()
                self.update_welcome_screen_visibility()
            else:
                self.show_message("warning", "Error", "Failed to add account.")
    
    def edit_account(self, row):
        """Edit an account"""
        login_item = self.table.item(row, 1)
        if not login_item:
            return
        
        account = login_item.data(Qt.UserRole)
        existing_logins = [acc.login for acc in self.account_manager.get_all_accounts() 
                          if acc.login != account.login]
        
        dialog = AccountDialog(self, account=account, existing_logins=existing_logins)
        
        if dialog.exec():
            new_account = dialog.get_account()
            
            # Delete old batch file if login changed
            if account.login != new_account.login and self.batch_generator:
                self.batch_generator.delete_batch_file(account.login)
            
            if self.account_manager.update_account(account.login, new_account):
                # Generate new batch file
                if self.batch_generator:
                    self.batch_generator.generate_batch_file(
                        new_account.login, new_account.password, new_account.character_name,
                        new_account.owner, new_account.description
                    )
                
                # Update table
                self.table.item(row, 1).setText(new_account.login)
                self.table.item(row, 1).setData(Qt.UserRole, new_account)
                self.table.item(row, 2).setData(Qt.UserRole, new_account.password)
                self.table.item(row, 3).setText(new_account.character_name)
                self.table.item(row, 4).setText(new_account.description)
                self.table.item(row, 5).setText(new_account.owner)
                self.table.item(row, 6).setText(getattr(new_account, 'server', 'Main'))
    
    def delete_account(self, row):
        """Delete an account"""
        login_item = self.table.item(row, 1)
        if not login_item:
            return
        
        account = login_item.data(Qt.UserRole)
        
        # Show custom delete confirmation dialog
        result = self.show_delete_confirmation_dialog(account.login)
        if result is None:  # User cancelled
            return
        
        confirm_delete, delete_batch_file = result
        
        if confirm_delete:
            # Terminate if running
            if self.game_launcher and self.game_launcher.is_account_running(account.login):
                self.game_launcher.terminate_account(account.login)
            
            # Delete batch file if requested
            if delete_batch_file and self.batch_generator:
                self.batch_generator.delete_batch_file(account.login)
            
            # Delete from manager
            if self.account_manager.delete_account(account.login):
                self.table.removeRow(row)
                self.update_status_bar()
                self.update_master_checkbox_state()
                self.update_welcome_screen_visibility()
                
                # Show success message
                batch_msg = " and batch file" if delete_batch_file else ""
                self.show_message("information", "Account Deleted", 
                                 f"Account '{account.login}'{batch_msg} deleted successfully.")
            else:
                self.show_message("warning", "Error", 
                                 f"Failed to delete account '{account.login}'.")
    
    def show_delete_confirmation_dialog(self, login):
        """Show custom delete confirmation dialog with batch file option"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete Account")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        # Set dialog icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.svg')
        if os.path.exists(icon_path):
            dialog.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        
        # Main message
        message_label = QLabel(f"Are you sure you want to delete the account '{login}'?")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #212121;
                font-size: 14px;
                font-weight: 600;
                margin: 10px 0px;
            }
        """)
        layout.addWidget(message_label)
        
        # Checkbox for batch file deletion
        batch_checkbox = QCheckBox("Also delete associated batch file (.bat)")
        batch_checkbox.setChecked(True)  # Default to checked
        batch_checkbox.setStyleSheet("""
            QCheckBox {
                color: #212121;
                font-size: 13px;
                font-weight: 500;
                margin: 10px 0px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #2196f3;
            }
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjMgNy43TDEuNCA0LjgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
        layout.addWidget(batch_checkbox)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        button_box.button(QDialogButtonBox.Yes).setText("Delete")
        button_box.button(QDialogButtonBox.No).setText("Cancel")
        
        # Style the buttons
        button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
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
            QDialogButtonBox QPushButton:hover {
                background-color: #1976d2;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #1565c0;
            }
            QDialogButtonBox QPushButton[text="Delete"] {
                background-color: #d32f2f;
            }
            QDialogButtonBox QPushButton[text="Delete"]:hover {
                background-color: #f44336;
            }
            QDialogButtonBox QPushButton[text="Delete"]:pressed {
                background-color: #b71c1c;
            }
        """)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Set dialog styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
            }
        """)
        
        dialog.setLayout(layout)
        
        # Execute dialog
        result = dialog.exec()
        if result == QDialog.Accepted:
            return (True, batch_checkbox.isChecked())
        else:
            return None
    
    def launch_account(self, row):
        """Launch a single account"""
        if not self.check_game_folder():
            return
        
        login_item = self.table.item(row, 1)
        if not login_item:
            return
        
        account = login_item.data(Qt.UserRole)
        
        # Check if already running
        if self.game_launcher.is_account_running(account.login):
            self.show_message("information", "Already Running", 
                                  f"Account '{account.login}' is already running.")
            return
        
        # Generate batch file if needed
        batch_file = None
        if self.batch_generator:
            batch_file = self.batch_generator.generate_batch_file(
                account.login, account.password, account.character_name,
                account.owner, account.description
            )
        
        if not batch_file:
            self.show_message("warning", "Error", "Failed to create batch file.")
            return
        
        # Launch the game
        pid = self.game_launcher.launch_account(account.login, batch_file)
        if pid:
            self.update_row_status(row, True)
            self.show_message("information", "Success", 
                                  f"Account '{account.login}' launched successfully.")
        else:
            self.show_message("warning", "Error", 
                              f"Failed to launch account '{account.login}'.")
    
    def close_account(self, row):
        """Close a single account"""
        if not self.game_launcher:
            return
        
        login_item = self.table.item(row, 1)
        if not login_item:
            return
        
        account = login_item.data(Qt.UserRole)
        
        if self.game_launcher.terminate_account(account.login):
            self.update_row_status(row, False)
            self.show_message("information", "Success", 
                                  f"Account '{account.login}' closed successfully.")
        else:
            self.show_message("warning", "Error", 
                              f"Failed to close account '{account.login}'.")
    
    def launch_selected(self):
        """Launch all selected accounts"""
        if not self.check_game_folder():
            return
        
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            self.show_message("information", "No Selection", 
                             "Please select accounts to launch.")
            return
        
        # Prepare launch data for queuing
        launch_data = []
        for row in selected_rows:
            login_item = self.table.item(row, 1)
            if login_item:
                account = login_item.data(Qt.UserRole)
                
                if not self.game_launcher.is_account_running(account.login):
                    batch_file = self.batch_generator.generate_batch_file(
                        account.login, account.password, account.character_name,
                        account.owner, account.description
                    )
                    
                    if batch_file:
                        launch_data.append((account.login, batch_file, row))
        
        if not launch_data:
            self.show_message("information", "Nothing to Launch", 
                             "No accounts need to be launched (already running or errors).")
            return
        
        # Queue all launches with callback
        queued = 0
        for login, batch_file, row in launch_data:
            callback = partial(self._launch_callback, row)
            self.game_launcher.queue_launch(login, batch_file, callback)
            queued += 1
        
        if queued == 1:
            self.show_message("information", "Launch Queued", 
                             f"Launching 1 account immediately.")
        else:
            self.show_message("information", "Launch Queued", 
                             f"Launching {queued} account(s) - first launches immediately, others with delay.")
    
    def close_selected(self):
        """Close all selected accounts"""
        if not self.game_launcher:
            return
        
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            self.show_message("information", "No Selection", 
                             "Please select accounts to close.")
            return
        
        closed = 0
        for row in selected_rows:
            login_item = self.table.item(row, 1)
            if login_item:
                account = login_item.data(Qt.UserRole)
                
                if self.game_launcher.terminate_account(account.login):
                    self.update_row_status(row, False)
                    closed += 1
        
        self.show_message("information", "Close Complete", 
                         f"Closed {closed} account(s).")
    
    def scan_folder(self):
        """Scan game folder for batch files"""
        if not self.check_game_folder():
            return
        
        accounts_data = self.batch_generator.scan_folder()
        
        if not accounts_data:
            self.show_message("information", "Scan Complete", 
                             "No account batch files found.")
            return
        
        # Filter out existing accounts
        existing_logins = [acc.login for acc in self.account_manager.get_all_accounts()]
        new_accounts = [acc for acc in accounts_data if acc['login'] not in existing_logins]
        
        if not new_accounts:
            self.show_message("information", "Scan Complete", 
                             "No new accounts found. All found accounts already exist.")
            return
        
        # Add new accounts
        added = 0
        for acc_data in new_accounts:
            account = Account(
                login=acc_data['login'],
                password=acc_data['password'],
                character_name=acc_data.get('character_name', ''),
                description=acc_data.get('description', ''),
                owner=acc_data.get('owner', ''),
                server=acc_data.get('server', 'Main')
            )
            
            if self.account_manager.add_account(account):
                self.add_account_to_table(account)
                added += 1
        
        self.update_status_bar()
        self.update_welcome_screen_visibility()
        self.show_message("information", "Scan Complete", 
                         f"Found {len(accounts_data)} account(s).\n"
                         f"Added {added} new account(s).")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.settings_manager)
        
        if dialog.exec():
            # Reinitialize game components with new folder
            self.init_game_components()
            self.show_message("information", "Settings Saved", 
                                  "Settings have been saved successfully.")
    
    def get_selected_rows(self):
        """Get all rows with checked checkboxes"""
        selected = []
        
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected.append(row)
        
        return selected
    
    def update_row_status(self, row, running):
        """Update visual status of a row"""
        # Could add visual indicators here (e.g., background color)
        pass
    
    def _launch_callback(self, row, login, pid):
        """Callback for queued launch completion"""
        if pid:
            self.update_row_status(row, True)
            # Could add status notification here
        else:
            # Could add error notification here
            pass
    
    def on_table_cell_clicked(self, row, column):
        """Handle table cell clicks for clipboard copy functionality"""
        if column == 1 or column == 2:  # Login or Password columns
            item = self.table.item(row, column)
            if item:
                field_type = item.data(Qt.UserRole + 1)
                if field_type == "login":
                    # Copy login to clipboard
                    text_to_copy = item.text()
                    self.copy_to_clipboard(text_to_copy, "Login")
                elif field_type == "password":
                    # Copy password to clipboard
                    password = item.data(Qt.UserRole)
                    self.copy_to_clipboard(password, "Password")
    
    def copy_to_clipboard(self, text, field_name):
        """Copy text to clipboard with user feedback"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Show temporary feedback
            self.status_bar.showMessage(f"{field_name} copied to clipboard", 2000)
            
        except Exception as e:
            self.show_message("warning", "Clipboard Error", 
                             f"Failed to copy {field_name.lower()} to clipboard: {e}")
    
    def on_master_checkbox_changed(self, state):
        """Handle master checkbox in header - simple implementation"""
        if state == Qt.Checked:
            # Check all row checkboxes
            self.set_all_row_checkboxes(True)
        else:
            # Uncheck all row checkboxes
            self.set_all_row_checkboxes(False)
    
    def set_all_row_checkboxes(self, checked):
        """Set all row checkboxes to the specified state"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                # Find the checkbox in the widget
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    # Block signals to prevent infinite recursion
                    checkbox.blockSignals(True)
                    checkbox.setChecked(checked)
                    checkbox.blockSignals(False)
    
    def update_master_checkbox_state(self):
        """Update master checkbox state based on row checkboxes"""
        # Count checked checkboxes
        checked_count = 0
        total_count = self.table.rowCount()
        
        for row in range(total_count):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    checked_count += 1
        
        # Update master checkbox state
        try:
            if hasattr(self, 'master_checkbox') and self.master_checkbox:
                # Standard checkbox approach - try to access the checkbox
                self.master_checkbox.blockSignals(True)
                if checked_count == 0:
                    self.master_checkbox.setChecked(False)
                elif checked_count == total_count:
                    self.master_checkbox.setChecked(True)
                else:
                    # Partially checked - Qt doesn't support tristate for this use case, so uncheck
                    self.master_checkbox.setChecked(False)
                self.master_checkbox.blockSignals(False)
        except (RuntimeError, AttributeError):
            # Checkbox was deleted or not accessible, fall back to alternative approach
            pass
            
        # Alternative symbol approach (used when widget approach fails or isn't available)
        if hasattr(self, 'master_checkbox_checked'):
            if checked_count == 0:
                self.master_checkbox_checked = False
            elif checked_count == total_count:
                self.master_checkbox_checked = True
            else:
                self.master_checkbox_checked = False
            self.update_header_checkbox_symbol()
    
    def export_accounts(self):
        """Export accounts to JSON file"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            self.show_message("information", "No Accounts", "No accounts to export.")
            return
        
        # Show export options dialog
        selected_accounts = self.show_export_dialog()
        if selected_accounts is None:
            return  # User cancelled
        
        # Get save file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pw_accounts_export_{timestamp}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Accounts",
            default_filename,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Create export data
            export_data = {
                "metadata": {
                    "version": "1.0",
                    "exportDate": datetime.now().isoformat(),
                    "accountCount": len(selected_accounts),
                    "encrypted": False
                },
                "accounts": []
            }
            
            # Add selected accounts
            for account in selected_accounts:
                account_data = account.to_dict()
                export_data["accounts"].append(account_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.show_message("information", "Export Successful", 
                                  f"Exported {len(selected_accounts)} account(s) to:\n{file_path}")
            
        except Exception as e:
            self.show_message("critical", "Export Error", 
                               f"Failed to export accounts:\n{str(e)}")
    
    def show_export_dialog(self):
        """Show dialog to select accounts for export"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Accounts to Export")
        dialog.setModal(True)
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayoutDialog()
        
        # Instructions
        label = QLabel("Select accounts to export:")
        layout.addWidget(label)
        
        # Account list
        account_list = QListWidget()
        accounts = self.account_manager.get_all_accounts()
        
        for account in accounts:
            item_text = f"{account.login} ({account.server}) - {account.character_name or 'No character'}"
            item = account_list.addItem(item_text)
            account_list.item(account_list.count() - 1).setData(Qt.UserRole, account)
            account_list.item(account_list.count() - 1).setCheckState(Qt.Checked)
        
        account_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(account_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self.set_all_items_checked(account_list, True))
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(lambda: self.set_all_items_checked(account_list, False))
        button_layout.addWidget(select_none_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            # Get selected accounts
            selected_accounts = []
            for i in range(account_list.count()):
                item = account_list.item(i)
                if item.checkState() == Qt.Checked:
                    account = item.data(Qt.UserRole)
                    selected_accounts.append(account)
            return selected_accounts
        
        return None
    
    def set_all_items_checked(self, list_widget, checked):
        """Set all items in list widget to checked or unchecked"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    
    def import_accounts(self):
        """Import accounts from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Accounts",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Read and validate JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate JSON structure
            if not self.validate_import_data(import_data):
                self.show_message("critical", "Invalid File", 
                                 "The selected file is not a valid account export file.")
                return
            
            accounts_data = import_data.get("accounts", [])
            if not accounts_data:
                self.show_message("information", "No Accounts", 
                                 "No accounts found in the import file.")
                return
            
            # Show import preview dialog
            accounts_to_import = self.show_import_dialog(accounts_data)
            if accounts_to_import is None:
                return  # User cancelled
            
            # Import accounts
            imported_count = 0
            skipped_count = 0
            error_count = 0
            
            for account_data in accounts_to_import:
                try:
                    # Create account object
                    account = Account(
                        login=account_data.get("login", ""),
                        password=account_data.get("password", ""),
                        character_name=account_data.get("character_name", ""),
                        description=account_data.get("description", ""),
                        owner=account_data.get("owner", ""),
                        server=account_data.get("server", "Main")
                    )
                    
                    # Check for duplicate
                    if self.account_manager.login_exists(account.login):
                        skipped_count += 1
                        continue
                    
                    # Add account
                    if self.account_manager.add_account(account):
                        # Generate batch file
                        if self.batch_generator:
                            self.batch_generator.generate_batch_file(
                                account.login, account.password, account.character_name,
                                account.owner, account.description
                            )
                        
                        self.add_account_to_table(account)
                        imported_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"Error importing account: {e}")
                    error_count += 1
            
            # Update UI
            self.update_status_bar()
            self.update_master_checkbox_state()
            self.update_welcome_screen_visibility()
            
            # Show results
            message = f"Import completed:\n"
            message += f"• Imported: {imported_count} account(s)\n"
            if skipped_count > 0:
                message += f"• Skipped (duplicates): {skipped_count} account(s)\n"
            if error_count > 0:
                message += f"• Errors: {error_count} account(s)\n"
            
            self.show_message("information", "Import Complete", message)
            
        except json.JSONDecodeError:
            self.show_message("critical", "Invalid File", 
                             "The selected file is not a valid JSON file.")
        except Exception as e:
            self.show_message("critical", "Import Error", 
                             f"Failed to import accounts:\n{str(e)}")
    
    def validate_import_data(self, data):
        """Validate import JSON data structure"""
        if not isinstance(data, dict):
            return False
        
        # Check for required structure
        if "accounts" not in data:
            return False
        
        accounts = data["accounts"]
        if not isinstance(accounts, list):
            return False
        
        # Validate account structure
        for account in accounts:
            if not isinstance(account, dict):
                return False
            if "login" not in account or "password" not in account:
                return False
        
        return True
    
    def show_import_dialog(self, accounts_data):
        """Show dialog to preview and select accounts for import"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Preview")
        dialog.setModal(True)
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayoutDialog()
        
        # Instructions
        label = QLabel("Preview accounts to import (duplicates will be skipped):")
        layout.addWidget(label)
        
        # Account list
        account_list = QListWidget()
        existing_logins = [acc.login for acc in self.account_manager.get_all_accounts()]
        
        for account_data in accounts_data:
            login = account_data.get("login", "Unknown")
            server = account_data.get("server", "Main")
            character = account_data.get("character_name", "No character")
            
            item_text = f"{login} ({server}) - {character}"
            if login in existing_logins:
                item_text += " [DUPLICATE - WILL BE SKIPPED]"
            
            item = account_list.addItem(item_text)
            account_list.item(account_list.count() - 1).setData(Qt.UserRole, account_data)
            
            # Check by default unless it's a duplicate
            check_state = Qt.Unchecked if login in existing_logins else Qt.Checked
            account_list.item(account_list.count() - 1).setCheckState(check_state)
        
        layout.addWidget(account_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self.set_all_items_checked(account_list, True))
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(lambda: self.set_all_items_checked(account_list, False))
        button_layout.addWidget(select_none_btn)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            # Get selected accounts
            selected_accounts = []
            for i in range(account_list.count()):
                item = account_list.item(i)
                if item.checkState() == Qt.Checked:
                    account_data = item.data(Qt.UserRole)
                    selected_accounts.append(account_data)
            return selected_accounts
        
        return None
    
    def cleanup_processes(self):
        """Clean up dead processes"""
        if self.game_launcher:
            self.game_launcher.cleanup_dead_processes()
    
    def update_status_bar(self):
        """Update the status bar"""
        count = self.table.rowCount()
        self.status_bar.showMessage(f"{count} account(s) loaded")
    
    def update_welcome_screen_visibility(self):
        """Show welcome screen if no accounts, hide if accounts exist"""
        if self.table.rowCount() == 0:
            self.table.hide()
            self.welcome_widget.show()
        else:
            self.welcome_widget.hide()
            self.table.show()
    
    def check_game_folder(self):
        """Check if game folder is set"""
        if not self.settings_manager.get_game_folder():
            self.show_message("warning", "No Game Folder", 
                              "Please set the game folder in Settings first.")
            self.open_settings()
            return False
        return True
    
    def restore_geometry(self):
        """Restore window geometry from settings"""
        geometry = self.settings_manager.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        self.settings_manager.set_window_geometry(self.saveGeometry())
        
        # Terminate all running processes
        if self.game_launcher:
            running = sum(1 for acc in self.account_manager.get_all_accounts() 
                         if self.game_launcher.is_account_running(acc.login))
            
            if running > 0:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Close Application")
                msg_box.setText(f"There are {running} game client(s) still running.\n"
                               "Do you want to close them before exiting?")
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                
                # Set icon for dialog
                icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icons', 'app-icon.svg')
                if os.path.exists(icon_path):
                    msg_box.setWindowIcon(QIcon(icon_path))
                
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
                    QMessageBox QPushButton:default {
                        background-color: #1976d2;
                        color: #ffffff;
                    }
                """)
                
                reply = msg_box.exec()
                
                if reply == QMessageBox.Cancel:
                    event.ignore()
                    return
                elif reply == QMessageBox.Yes:
                    self.game_launcher.terminate_all()
            
            # Shutdown the launch queue worker
            self.game_launcher.shutdown()
        
        event.accept()