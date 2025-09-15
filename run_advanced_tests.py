#!/usr/bin/env python3
"""
Quick runner script for the Advanced Vanna AI Test Suite
Usage: python run_advanced_tests.py
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from advanced_test_suite import main

if __name__ == "__main__":
    print("🚀 Starting Advanced Vanna AI Test Suite")
    print("=" * 50)
    asyncio.run(main())
