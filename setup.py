#!/usr/bin/env python3
"""
Setup script for Photo Cleaner

This script helps users set up the Photo Cleaner environment
and install all necessary dependencies.
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible.")
        return True

def install_requirements():
    """Install required packages."""
    print("\n📦 Installing required packages...")
    
    # Check if pip is available
    success, _ = run_command("pip --version")
    if not success:
        print("❌ Error: pip is not available. Please install pip first.")
        return False
    
    # Install packages
    packages = [
        "tensorflow>=2.8.0",
        "opencv-python>=4.5.0",
        "numpy>=1.21.0",
        "Pillow>=8.3.0",
        "requests>=2.25.0",
        "tqdm>=4.62.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        success, output = run_command(f"pip install {package}")
        if success:
            print(f"✅ {package} installed successfully.")
        else:
            print(f"❌ Failed to install {package}: {output}")
            return False
    
    return True

def create_test_directory():
    """Create a test directory with sample structure."""
    print("\n📁 Creating test directory structure...")
    
    test_dir = "test_photos"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a simple test image (1x1 pixel)
    try:
        from PIL import Image
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        test_image_path = os.path.join(test_dir, 'test_image.jpg')
        img.save(test_image_path)
        
        print(f"✅ Test directory created: {test_dir}")
        print(f"✅ Sample image created: {test_image_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test directory: {e}")
        return False

def run_test():
    """Run a quick test of the photo cleaner."""
    print("\n🧪 Running quick test...")
    
    if not os.path.exists("test_photos"):
        print("❌ Test directory not found. Skipping test.")
        return False
    
    # Test the simple version first
    print("Testing simple_photo_cleaner.py...")
    success, output = run_command("python simple_photo_cleaner.py -i test_photos --dry-run")
    
    if success:
        print("✅ Simple photo cleaner test passed.")
        return True
    else:
        print(f"❌ Test failed: {output}")
        return False

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now use the Photo Cleaner with these commands:")
    print("\n1. Basic usage (simple version):")
    print('   python simple_photo_cleaner.py -i "path/to/photos"')
    print("\n2. Advanced usage (full version):")
    print('   python photo_cleaner.py -i "path/to/photos"')
    print("\n3. Dry run (preview only):")
    print('   python simple_photo_cleaner.py -i "path/to/photos" --dry-run')
    print("\n4. Custom threshold:")
    print('   python simple_photo_cleaner.py -i "path/to/photos" -t 0.5')
    print("\n5. Verbose output:")
    print('   python simple_photo_cleaner.py -i "path/to/photos" -v')
    print("\nFor more options, run:")
    print("   python photo_cleaner.py --help")
    print("\n📖 Check README.md for detailed documentation.")
    print("\n⚠️  IMPORTANT: The simple version uses basic heuristics.")
    print("   For production use, consider implementing proper NSFW models.")

def main():
    """Main setup function."""
    print("🚀 Photo Cleaner Setup")
    print("=" * 30)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation.")
        sys.exit(1)
    
    # Create test directory
    create_test_directory()
    
    # Run test
    run_test()
    
    # Print usage instructions
    print_usage_instructions()
    
    print("\n✅ Setup completed successfully!")

if __name__ == '__main__':
    main()