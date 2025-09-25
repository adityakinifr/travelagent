#!/usr/bin/env python3
"""
Startup script for the AI Travel Agent web application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys. See env_example.txt for reference.")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    print("✅ Environment variables loaded successfully")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting AI Travel Agent Server...")
    print("📱 Open http://localhost:8080 in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main startup function"""
    print("🌟 AI Travel Agent - Web Interface")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()
