#!/usr/bin/env python3
"""
Simple script to convert PNG to ICO format for Windows applications.
Requires Pillow: pip install Pillow
"""

try:
    from PIL import Image
    import os
    
    def create_ico_from_png(png_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
        """Convert PNG to ICO with multiple sizes"""
        if not os.path.exists(png_path):
            print(f"Error: PNG file not found: {png_path}")
            return False
            
        try:
            # Open the PNG image
            img = Image.open(png_path)
            
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create list of resized images
            icon_images = []
            for size in sizes:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                icon_images.append(resized)
            
            # Save as ICO
            icon_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in icon_images])
            print(f"Successfully created ICO file: {ico_path}")
            return True
            
        except Exception as e:
            print(f"Error creating ICO: {e}")
            return False
    
    # Convert app-icon-logo.jpeg to logo.ico
    png_file = "assets/app-icon-logo.jpeg"
    ico_file = "assets/logo.ico"
    
    if create_ico_from_png(png_file, ico_file):
        print("Icon conversion completed successfully!")
        print("You can now uncomment the icon line in app-gptui.spec")
    else:
        print("Icon conversion failed. Build will continue without icon.")
        
except ImportError:
    print("Pillow not installed. Installing...")
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("Pillow installed successfully. Please run this script again.")
    except Exception as e:
        print(f"Failed to install Pillow: {e}")
        print("You can install it manually with: pip install Pillow")
