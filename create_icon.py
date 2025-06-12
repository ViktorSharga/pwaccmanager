#!/usr/bin/env python
"""Simple icon creation script for PyInstaller"""

import os
import sys

def create_basic_ico():
    """Create a basic ICO file for PyInstaller"""
    print("Creating basic icon file for PyInstaller...")
    
    # Create a minimal ICO file (16x16 blue square)
    ico_header = bytearray([
        0x00, 0x00,  # Reserved, must be 0
        0x01, 0x00,  # Type: 1 for ICO
        0x01, 0x00,  # Number of images: 1
    ])
    
    # Image directory entry (16 bytes)
    ico_entry = bytearray([
        0x20,        # Width: 32 pixels
        0x20,        # Height: 32 pixels  
        0x00,        # Color count: 0 (no palette)
        0x00,        # Reserved: 0
        0x01, 0x00,  # Color planes: 1
        0x20, 0x00,  # Bits per pixel: 32
        0x80, 0x04, 0x00, 0x00,  # Size of image data: 1152 bytes
        0x16, 0x00, 0x00, 0x00,  # Offset to image data: 22 bytes
    ])
    
    # Create a simple 32x32 blue bitmap
    # BMP header (40 bytes)
    bmp_header = bytearray([
        0x28, 0x00, 0x00, 0x00,  # Header size: 40
        0x20, 0x00, 0x00, 0x00,  # Width: 32
        0x40, 0x00, 0x00, 0x00,  # Height: 64 (32*2 for ICO format)
        0x01, 0x00,              # Planes: 1
        0x20, 0x00,              # Bits per pixel: 32
        0x00, 0x00, 0x00, 0x00,  # Compression: none
        0x00, 0x10, 0x00, 0x00,  # Image size: 4096
        0x00, 0x00, 0x00, 0x00,  # X pixels per meter: 0
        0x00, 0x00, 0x00, 0x00,  # Y pixels per meter: 0
        0x00, 0x00, 0x00, 0x00,  # Colors used: 0
        0x00, 0x00, 0x00, 0x00,  # Important colors: 0
    ])
    
    # Create blue pixel data (32x32 = 1024 pixels, 4 bytes each = 4096 bytes)
    blue_color = bytearray([0xFF, 0x40, 0x1E, 0xFF])  # Blue (BGRA format)
    pixel_data = blue_color * (32 * 32)
    
    # AND mask (32x32 bits = 128 bytes, all zeros for opaque)
    and_mask = bytearray(128)
    
    # Combine all parts
    ico_data = ico_header + ico_entry + bmp_header + pixel_data + and_mask
    
    # Write to file
    ico_path = os.path.join("icons", "app-icon.ico")
    os.makedirs("icons", exist_ok=True)
    
    with open(ico_path, "wb") as f:
        f.write(ico_data)
    
    print(f"Created basic icon file: {ico_path}")
    return True

if __name__ == "__main__":
    try:
        create_basic_ico()
        print("Icon creation successful!")
    except Exception as e:
        print(f"Error creating icon: {e}")
        print("You can:")
        print("1. Download an ICO file manually and place it in icons/app-icon.ico")
        print("2. Use an online SVG to ICO converter")
        print("3. Remove the --icon parameter from PyInstaller command")
        sys.exit(1)