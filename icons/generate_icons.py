#!/usr/bin/env python
"""Generate icon files from SVG for the application"""

import os
import sys
import subprocess

def install_dependencies():
    """Try to install required dependencies"""
    try:
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "cairosvg"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies automatically.")
        return False

# Check if required libraries are available
PIL_AVAILABLE = False
CAIROSVG_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    pass

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    pass

if not (PIL_AVAILABLE and CAIROSVG_AVAILABLE):
    print("Missing required libraries:")
    if not PIL_AVAILABLE:
        print("- PIL/Pillow")
    if not CAIROSVG_AVAILABLE:
        print("- cairosvg")
    
    print("\nAttempting to install dependencies...")
    if install_dependencies():
        # Try importing again
        try:
            from PIL import Image
            import cairosvg
            PIL_AVAILABLE = True
            CAIROSVG_AVAILABLE = True
        except ImportError:
            pass
    
    if not (PIL_AVAILABLE and CAIROSVG_AVAILABLE):
        print("\nCould not install dependencies automatically.")
        print("Please install them manually with: pip install Pillow cairosvg")
        print("\nAlternatively:")
        print("1. Run this script again after installing dependencies")
        print("2. Use an online SVG to ICO converter")
        print("3. Skip the icon for now and remove --icon from PyInstaller command")
        
        # Try to create a basic ICO file from embedded data as last resort
        if create_fallback_ico():
            print("4. Created basic fallback ICO file")
        
        if not os.path.exists("app-icon.ico"):
            sys.exit(1)

def create_fallback_ico():
    """Create a basic ICO file as fallback"""
    try:
        # This is a simple 32x32 blue square ICO file (base64 encoded)
        ico_data = """
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAA4Oj8AHiCoACE4qAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANDs/
AB0hqAAhOKkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAORo4+AAhOaYA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATU7PwAdIakAITmpAA==
"""
        
        import base64
        ico_bytes = base64.b64decode(ico_data.strip().replace('\n', ''))
        
        with open("app-icon.ico", "wb") as f:
            f.write(ico_bytes)
        
        print("Created fallback ICO file")
        return True
    except Exception as e:
        print(f"Failed to create fallback ICO: {e}")
        return False

def generate_icons():
    """Generate icon files in various sizes from the SVG"""
    svg_path = "app-icon.svg"
    
    if not os.path.exists(svg_path):
        print(f"Error: {svg_path} not found!")
        return
    
    # Sizes to generate
    sizes = [16, 32, 48, 64, 128, 256]
    
    # Generate PNG files
    for size in sizes:
        png_path = f"app-icon-{size}.png"
        print(f"Generating {png_path}...")
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=size,
            output_height=size
        )
    
    # Generate ICO file for Windows
    print("Generating app-icon.ico...")
    # Load the various PNG sizes
    images = []
    for size in [16, 32, 48, 256]:
        if os.path.exists(f"app-icon-{size}.png"):
            img = Image.open(f"app-icon-{size}.png")
            images.append(img)
    
    if images:
        # Save as ICO
        images[0].save(
            "app-icon.ico",
            format='ICO',
            sizes=[(img.width, img.height) for img in images]
        )
        print("Icon generation complete!")
    else:
        print("Error: No PNG files found to create ICO")

if __name__ == "__main__":
    # Change to icons directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    generate_icons()