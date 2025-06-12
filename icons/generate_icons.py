#!/usr/bin/env python
"""Generate icon files from SVG for the application"""

import os
import sys

# Check if required libraries are available
try:
    from PIL import Image
    import cairosvg
except ImportError:
    print("This script requires PIL/Pillow and cairosvg libraries.")
    print("Install them with: pip install Pillow cairosvg")
    sys.exit(1)

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