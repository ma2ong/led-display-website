#!/usr/bin/env python3
"""
Simple test script to verify backend is working
"""

import requests
import json
import time

def test_backend():
    """Test backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend API...")
    print("=" * 40)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/products", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            print("✅ Products API is accessible")
            
            data = response.json()
            if 'products' in data:
                print(f"✅ Found {len(data['products'])} products in database")
            else:
                print("⚠️  No products found in response")
        else:
            print(f"❌ Products API returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure the backend is running on port 5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend server timeout")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False
    
    # Test 2: Test contact API
    try:
        test_contact = {
            "name": "Test User",
            "email": "test@example.com",
            "company": "Test Company",
            "phone": "+1234567890",
            "product": "LED Display",
            "message": "This is a test inquiry"
        }
        
        response = requests.post(
            f"{base_url}/api/contact",
            json=test_contact,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Contact API is working")
        else:
            print(f"⚠️  Contact API returned status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Contact API test failed: {e}")
    
    print("=" * 40)
    print("🎉 Backend test completed!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    test_backend()