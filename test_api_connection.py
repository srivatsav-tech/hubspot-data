#!/usr/bin/env python3
"""
Simple test to verify HubSpot API connection
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_hubspot_connection():
    """Test if we can connect to HubSpot API"""
    access_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ HUBSPOT_ACCESS_TOKEN not found in environment")
        return False
    
    print(f"✅ Token found: {access_token[:15]}...")
    
    # Test API connection
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Simple API call to test connection
        response = requests.get(
            "https://api.hubapi.com/crm/v3/objects/deals?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ HubSpot API connection successful!")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing HubSpot API Connection...")
    test_hubspot_connection()
