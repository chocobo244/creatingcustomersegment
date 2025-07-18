#!/usr/bin/env python3
"""
Startup script for Market Research Segmentation Application
This script provides instructions and runs the application with proper error handling.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import pandas
        import numpy
        import sklearn
        import matplotlib
        import seaborn
        import plotly
        print("✅ All dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements_simple.txt")
        return False

def check_data_file():
    """Check if the data file exists."""
    if os.path.exists('customers.csv'):
        print("✅ Customer data file found!")
        return True
    else:
        print("❌ Customer data file (customers.csv) not found!")
        print("Please ensure customers.csv is in the same directory as this script.")
        return False

def main():
    print("🚀 Market Research Segmentation Application")
    print("=" * 60)
    print()
    
    print("🔍 Checking system requirements...")
    if not check_dependencies():
        return 1
    
    if not check_data_file():
        return 1
    
    print()
    print("📋 Application Information:")
    print("   - Web Interface: http://localhost:5000")
    print("   - Demo Script: python3 demo.py")
    print("   - Documentation: README_APPLICATION.md")
    print()
    
    choice = input("Would you like to run the [W]eb application or [D]emo script? (W/D): ").upper().strip()
    
    if choice == 'D':
        print("\n🎬 Running demo script...")
        try:
            subprocess.run([sys.executable, 'demo.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Demo failed with error: {e}")
            return 1
    elif choice == 'W':
        print("\n🌐 Starting web application...")
        print("💡 Open your browser and navigate to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        try:
            subprocess.run([sys.executable, 'app.py'], check=True)
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Application failed with error: {e}")
            return 1
    else:
        print("❌ Invalid choice. Please run again and choose W or D.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())