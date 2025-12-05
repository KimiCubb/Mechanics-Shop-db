#!/usr/bin/env python3
"""
Initialize database on Render by calling the /init-db endpoint.

Usage:
    python3 init_render.py https://your-app-name.onrender.com
    
Example:
    python3 init_render.py https://mechanic-shop-api.onrender.com
"""

import requests
import sys

def init_render_database(app_url):
    """
    Call the /init-db endpoint on Render to create database tables.
    
    Args:
        app_url (str): Your Render app URL (e.g., https://mechanic-shop-api.onrender.com)
    """
    if not app_url:
        print("❌ Error: Please provide your Render app URL")
        print("\nUsage: python3 init_render.py https://your-app-name.onrender.com")
        sys.exit(1)
    
    # Ensure URL doesn't end with /
    app_url = app_url.rstrip('/')
    init_endpoint = f"{app_url}/init-db"
    
    print(f"🔄 Calling initialization endpoint: {init_endpoint}")
    print("=" * 60)
    
    try:
        response = requests.post(init_endpoint, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print("-" * 60)
        
        if response.status_code == 201:
            print("✅ SUCCESS! Database tables created!")
            print("\nResponse:")
            import json
            print(json.dumps(response.json(), indent=2))
            
        elif response.status_code == 400:
            print("❌ ERROR! Database initialization failed!")
            print("\nResponse:")
            import json
            print(json.dumps(response.json(), indent=2))
            sys.exit(1)
            
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print("\nResponse:")
            print(response.text)
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print(f"   Could not reach: {init_endpoint}")
        print("   Make sure:")
        print("   • Your app URL is correct")
        print("   • Your app is deployed on Render")
        print("   • Your app is running (not sleeping)")
        sys.exit(1)
        
    except requests.exceptions.Timeout:
        print("❌ Request Timeout!")
        print("   The server took too long to respond.")
        print("   Try again in a moment.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    else:
        # Prompt user for URL
        print("🔧 Mechanic Shop API - Render Database Initializer")
        print("=" * 60)
        app_url = input("Enter your Render app URL (e.g., https://mechanic-shop-api.onrender.com): ").strip()
    
    init_render_database(app_url)
