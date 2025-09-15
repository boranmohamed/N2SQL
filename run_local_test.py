#!/usr/bin/env python3
"""
Simple script to run the local Vanna server test.
"""
import subprocess
import sys
import time

def check_local_server():
    """Check if local Vanna server is running."""
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    print("🚀 Local Vanna Server Test Runner")
    print("=" * 50)
    
    # Check if local server is running
    print("🔍 Checking if local Vanna server is running...")
    if not check_local_server():
        print("❌ Local Vanna server is not running!")
        print("💡 Please start your local server first:")
        print("   cd D:\\vanna")
        print("   python local_vanna_server.py")
        print("\n🔄 Or run this command in another terminal:")
        print("   start cmd /k \"cd /d D:\\vanna && python local_vanna_server.py\"")
        
        choice = input("\n❓ Do you want to continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("👋 Exiting...")
            return
    else:
        print("✅ Local Vanna server is running!")
    
    print("\n🧪 Starting test suite...")
    print("-" * 50)
    
    # Run the test script
    try:
        subprocess.run([sys.executable, "test_app_with_local_vanna.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Test failed with exit code: {e.returncode}")
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    main()
