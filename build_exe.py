"""
Script to build The Wizard as a standalone .exe file.
Uses PyInstaller to create a single executable.

Usage:
    python build_exe.py

Requirements:
    pip install pyinstaller
"""

import subprocess
import sys
import os

def build_executable():
    """
    Build the application as a standalone executable.
    """
    print("🔨 Building The Wizard executable...")
    print("="*50)
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single file
        "--windowed",          # No console window
        "--name", "TheWizard", # Executable name
        "--icon", "wizard.ico" if os.path.exists("wizard.ico") else "NONE",
        "--add-data", f"constants.py{os.pathsep}.",
        "--add-data", f"system_utils.py{os.pathsep}.",
        "--hidden-import", "psutil",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("="*50)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("✅ Build successful!")
        print("📁 Executable: dist/TheWizard.exe")
        print("="*50)
    else:
        print("\n❌ Build failed. Check errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(build_executable())
