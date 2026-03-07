#!/usr/bin/env python3
"""
Setup Verification Script
Run this script to verify your backend environment is properly configured.
"""

import sys
import os

def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is too old. Need 3.8+")
        return False

def check_imports():
    """Check if all required packages can be imported"""
    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('cv2', 'OpenCV'),
        ('mediapipe', 'MediaPipe'),
        ('librosa', 'Librosa'),
        ('openai', 'OpenAI'),
        ('textblob', 'TextBlob'),
        ('supabase', 'Supabase'),
        ('dotenv', 'python-dotenv'),
        ('google.generativeai', 'Google Generative AI'),
        ('numpy', 'NumPy'),
    ]

    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} NOT installed")
            all_ok = False

    return all_ok

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        print("  → Copy .env.example to .env and add your API keys")
        return False

    print("✓ .env file exists")

    required_vars = [
        'OPENAI_API_KEY',
        'GEMINI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]

    from dotenv import load_dotenv
    load_dotenv()

    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is NOT set")
            all_ok = False

    return all_ok

def check_backend_files():
    """Check if all backend files exist"""
    files = [
        'main.py',
        'analysis_helpers.py',
        'database.py',
        'llm_reporter.py',
        'requirements.txt'
    ]

    all_ok = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} NOT found")
            all_ok = False

    return all_ok

def main():
    print("=" * 60)
    print("TESTIMONY VERACITY SUPPORT SYSTEM - SETUP VERIFICATION")
    print("=" * 60)
    print()

    print("[1/4] Checking Python version...")
    python_ok = check_python_version()
    print()

    print("[2/4] Checking required files...")
    files_ok = check_backend_files()
    print()

    print("[3/4] Checking installed packages...")
    imports_ok = check_imports()
    print()

    print("[4/4] Checking environment variables...")
    env_ok = check_env_file()
    print()

    print("=" * 60)
    if python_ok and files_ok and imports_ok and env_ok:
        print("✓ ALL CHECKS PASSED!")
        print("=" * 60)
        print()
        print("You're ready to start the backend server:")
        print("  uvicorn main:app --reload --port 8000")
        print()
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("=" * 60)
        print()
        print("Please fix the issues above before starting the server.")
        print("See README.md for detailed setup instructions.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
