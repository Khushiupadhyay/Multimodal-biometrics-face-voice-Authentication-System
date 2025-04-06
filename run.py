import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import importlib.util

def check_dependencies():
    """Check if all required libraries are installed"""
    required_packages = [
        'opencv-python', 'numpy', 'torch', 'torchaudio', 
        'sounddevice', 'soundfile', 'librosa', 'scipy', 'insightface'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package.split('-')[0]) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("All required packages installed successfully!")
    
    return True

def create_directories():
    """Create necessary directories for the application"""
    directories = ['./db', './assets']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory {directory} created or already exists.")

def run_application():
    """Run the main application"""
    try:
        import main
        root = tk.Tk()
        app = main.BiometricApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while starting the application: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Welcome to Biometric Authentication System")
    print("Setting up...")
    
    # Check for dependencies
    if check_dependencies():
        # Create necessary directories
        create_directories()
        
        # Run the application
        print("Starting application...")
        run_application()
    else:
        print("Failed to set up the application dependencies. Please check your installation.")