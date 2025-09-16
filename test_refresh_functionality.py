#!/usr/bin/env python3
"""
Test script to verify the refresh functionality works correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_setup():
    """Test if environment variables are properly set"""
    access_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ HUBSPOT_ACCESS_TOKEN not found in environment")
        print("💡 Please create a .env file with your HubSpot token:")
        print("   HUBSPOT_ACCESS_TOKEN=your_token_here")
        return False
    else:
        print("✅ HUBSPOT_ACCESS_TOKEN found in environment")
        print(f"   Token starts with: {access_token[:10]}...")
        return True

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import streamlit as st
        import pandas as pd
        import requests
        import csv
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dashboard_import():
    """Test if the dashboard can be imported"""
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        # Import the dashboard module
        import simple_deal_dashboard
        print("✅ Dashboard module imported successfully")
        
        # Test if the HubSpotExtractor class exists
        if hasattr(simple_deal_dashboard, 'HubSpotExtractor'):
            print("✅ HubSpotExtractor class found")
        else:
            print("❌ HubSpotExtractor class not found")
            return False
            
        # Test if the refresh function exists
        if hasattr(simple_deal_dashboard, 'refresh_data_from_hubspot'):
            print("✅ refresh_data_from_hubspot function found")
        else:
            print("❌ refresh_data_from_hubspot function not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing HubSpot Dashboard Refresh Functionality")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Module Imports", test_imports),
        ("Dashboard Import", test_dashboard_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refresh functionality should work correctly.")
        print("\n🚀 To run the dashboard:")
        print("   streamlit run simple_deal_dashboard.py")
        print("\n🔄 The refresh button will appear in the top-right corner of the dashboard.")
    else:
        print("❌ Some tests failed. Please fix the issues before running the dashboard.")
        return False
    
    return True

if __name__ == "__main__":
    main()
