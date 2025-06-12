#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Perfect World Account Manager
Main entry point for the application
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    # Enable high DPI scaling on Windows
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Perfect World Account Manager")
    app.setOrganizationName("PWManager")
    
    # Set application icon globally for all windows
    from PySide6.QtGui import QIcon
    
    # Try ICO file first (better Windows support), then fallback to SVG
    ico_path = os.path.join(os.path.dirname(__file__), 'icons', 'app-icon.ico')
    svg_path = os.path.join(os.path.dirname(__file__), 'icons', 'app-icon.svg')
    
    icon_path = ico_path if os.path.exists(ico_path) else svg_path
    
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        # Set default window icon for all windows in this application
        app.setWindowIcon(app_icon)
        print(f"Global app icon set from: {icon_path}")
    else:
        print(f"Warning: No icon file found at {ico_path} or {svg_path}")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()