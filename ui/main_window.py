"""Main application window"""

from functools import partial

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QStatusBar, QMenu,
                             QCheckBox, QToolBar, QStyle)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

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
        self.setup_ui()
        self.load_accounts()
        
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
        layout.addWidget(self.table)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
        # Set minimum size
        self.setMinimumSize(800, 400)
    
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
        
        # Settings button
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
    
    def create_table(self):
        """Create the accounts table"""
        self.table = QTableWidget()
        
        # Set columns
        columns = ["", "Login", "Password", "Character Name", "Description", "Owner", "Actions"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Configure table
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.resizeSection(0, 30)  # Checkbox column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Login
        header.resizeSection(2, 100)  # Password
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Character
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Owner
        header.resizeSection(6, 120)  # Actions
    
    def load_accounts(self):
        """Load accounts into the table"""
        accounts = self.account_manager.get_all_accounts()
        
        # Clear table
        self.table.setRowCount(0)
        
        # Add accounts
        for account in accounts:
            self.add_account_to_table(account)
        
        self.update_status_bar()
    
    def add_account_to_table(self, account):
        """Add an account to the table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_widget.setLayout(checkbox_layout)
        self.table.setCellWidget(row, 0, checkbox_widget)
        
        # Login
        self.table.setItem(row, 1, QTableWidgetItem(account.login))
        
        # Password (masked)
        password_item = QTableWidgetItem("••••••")
        password_item.setData(Qt.UserRole, account.password)
        self.table.setItem(row, 2, password_item)
        
        # Character name
        self.table.setItem(row, 3, QTableWidgetItem(account.character_name))
        
        # Description
        self.table.setItem(row, 4, QTableWidgetItem(account.description))
        
        # Owner
        self.table.setItem(row, 5, QTableWidgetItem(account.owner))
        
        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 0, 5, 0)
        
        # Play button
        play_btn = QPushButton("▶")
        play_btn.setFixedSize(30, 25)
        play_btn.setToolTip("Launch game")
        play_btn.clicked.connect(partial(self.launch_account, row))
        actions_layout.addWidget(play_btn)
        
        # Kill button
        kill_btn = QPushButton("✖")
        kill_btn.setFixedSize(30, 25)
        kill_btn.setToolTip("Close game")
        kill_btn.clicked.connect(partial(self.close_account, row))
        actions_layout.addWidget(kill_btn)
        
        # Menu button
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(30, 25)
        menu_btn.setToolTip("More options")
        
        # Create menu and connect it properly
        menu = QMenu()
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        
        # Use partial to properly bind the row value
        edit_action.triggered.connect(partial(self.edit_account, row))
        delete_action.triggered.connect(partial(self.delete_account, row))
        
        menu_btn.setMenu(menu)
        actions_layout.addWidget(menu_btn)
        
        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 6, actions_widget)
        
        # Store account reference
        self.table.item(row, 1).setData(Qt.UserRole, account)
    
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
            else:
                QMessageBox.warning(self, "Error", "Failed to add account.")
    
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
    
    def delete_account(self, row):
        """Delete an account"""
        login_item = self.table.item(row, 1)
        if not login_item:
            return
        
        account = login_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Delete Account",
            f"Are you sure you want to delete the account '{account.login}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Terminate if running
            if self.game_launcher and self.game_launcher.is_account_running(account.login):
                self.game_launcher.terminate_account(account.login)
            
            # Delete batch file
            if self.batch_generator:
                self.batch_generator.delete_batch_file(account.login)
            
            # Delete from manager
            if self.account_manager.delete_account(account.login):
                self.table.removeRow(row)
                self.update_status_bar()
    
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
            QMessageBox.information(self, "Already Running", 
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
            QMessageBox.warning(self, "Error", "Failed to create batch file.")
            return
        
        # Launch the game
        pid = self.game_launcher.launch_account(account.login, batch_file)
        if pid:
            self.update_row_status(row, True)
            QMessageBox.information(self, "Success", 
                                  f"Account '{account.login}' launched successfully.")
        else:
            QMessageBox.warning(self, "Error", 
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
            QMessageBox.information(self, "Success", 
                                  f"Account '{account.login}' closed successfully.")
        else:
            QMessageBox.warning(self, "Error", 
                              f"Failed to close account '{account.login}'.")
    
    def launch_selected(self):
        """Launch all selected accounts"""
        if not self.check_game_folder():
            return
        
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", 
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
            QMessageBox.information(self, "Nothing to Launch", 
                                  "No accounts need to be launched (already running or errors).")
            return
        
        # Queue all launches with callback
        queued = 0
        for login, batch_file, row in launch_data:
            callback = partial(self._launch_callback, row)
            self.game_launcher.queue_launch(login, batch_file, callback)
            queued += 1
        
        QMessageBox.information(self, "Launch Queued", 
                              f"Queued {queued} account(s) for launch with delay.")
    
    def close_selected(self):
        """Close all selected accounts"""
        if not self.game_launcher:
            return
        
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", 
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
        
        QMessageBox.information(self, "Close Complete", 
                              f"Closed {closed} account(s).")
    
    def scan_folder(self):
        """Scan game folder for batch files"""
        if not self.check_game_folder():
            return
        
        accounts_data = self.batch_generator.scan_folder()
        
        if not accounts_data:
            QMessageBox.information(self, "Scan Complete", 
                                  "No account batch files found.")
            return
        
        # Filter out existing accounts
        existing_logins = [acc.login for acc in self.account_manager.get_all_accounts()]
        new_accounts = [acc for acc in accounts_data if acc['login'] not in existing_logins]
        
        if not new_accounts:
            QMessageBox.information(self, "Scan Complete", 
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
                owner=acc_data.get('owner', '')
            )
            
            if self.account_manager.add_account(account):
                self.add_account_to_table(account)
                added += 1
        
        self.update_status_bar()
        QMessageBox.information(self, "Scan Complete", 
                              f"Found {len(accounts_data)} account(s).\n"
                              f"Added {added} new account(s).")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.settings_manager)
        
        if dialog.exec():
            # Reinitialize game components with new folder
            self.init_game_components()
            QMessageBox.information(self, "Settings Saved", 
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
    
    def cleanup_processes(self):
        """Clean up dead processes"""
        if self.game_launcher:
            self.game_launcher.cleanup_dead_processes()
    
    def update_status_bar(self):
        """Update the status bar"""
        count = self.table.rowCount()
        self.status_bar.showMessage(f"{count} account(s) loaded")
    
    def check_game_folder(self):
        """Check if game folder is set"""
        if not self.settings_manager.get_game_folder():
            QMessageBox.warning(self, "No Game Folder", 
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
                reply = QMessageBox.question(
                    self, "Close Application",
                    f"There are {running} game client(s) still running.\n"
                    "Do you want to close them before exiting?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    event.ignore()
                    return
                elif reply == QMessageBox.Yes:
                    self.game_launcher.terminate_all()
            
            # Shutdown the launch queue worker
            self.game_launcher.shutdown()
        
        event.accept()