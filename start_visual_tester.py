#!/usr/bin/env python3
"""
Startup script for Vanna Visual Tester
Checks prerequisites and starts the web interface.
"""
import subprocess
import sys
import os
import time
import requests

def check_local_server():
    """Check if local Vanna server is running."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def check_database():
    """Check if database file exists."""
    db_files = ["vanna_app_clean.db", "vanna_app.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"✅ Found database: {db_file}")
            return True
    print("❌ No database file found (vanna_app_clean.db or vanna_app.db)")
    return False

def install_requirements():
    """Install required packages."""
    try:
        print("📦 Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Flask", "pandas"], 
                      check=True, capture_output=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def main():
    print("🌐 Vanna Visual Tester Startup")
    print("=" * 50)
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check database
    if not check_database():
        print("💡 Please make sure you have a database file in the current directory")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            return
    
    # Check local server
    print("🔍 Checking local Vanna server...")
    if not check_local_server():
        print("⚠️ Local Vanna server is not running!")
        print("💡 To start it, run in another terminal:")
        print("   cd D:\\vanna")
        print("   python local_vanna_server.py")
        print()
        choice = input("Continue anyway? The interface will show connection errors. (y/n): ").lower()
        if choice != 'y':
            return
    else:
        print("✅ Local Vanna server is running")
    
    # Install requirements
    print("\n📦 Checking requirements...")
    try:
        import flask
        import pandas
        print("✅ All requirements already installed")
    except ImportError:
        if not install_requirements():
            print("❌ Failed to install requirements. Please install manually:")
            print("   pip install Flask pandas")
            return
    
    # Start the web interface
    print("\n🚀 Starting Visual Tester Web Interface...")
    print("📱 The interface will open at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the visual tester
        from vanna_visual_tester import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Visual tester stopped by user")
    except Exception as e:
        print(f"❌ Error starting visual tester: {e}")
        print("💡 Make sure all files are in the correct location")

if __name__ == "__main__":
    main()
