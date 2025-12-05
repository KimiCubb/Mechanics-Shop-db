#!/usr/bin/env python3
"""
Helper script to find your Render app URL and initialize the database.

This script helps you:
1. Find your Render app URL
2. Test the connection
3. Initialize the database
"""

import subprocess
import sys

def open_render_dashboard():
    """Open Render dashboard in browser"""
    import webbrowser
    print("\n🌐 Opening Render Dashboard...")
    webbrowser.open('https://dashboard.render.com')
    print("✓ Dashboard opened in your browser")

def get_render_app_url():
    """Get Render app URL from user with helpful instructions"""
    print("\n" + "="*70)
    print("🔍 FINDING YOUR RENDER APP URL")
    print("="*70)
    print("\nSteps to find your Render app URL:")
    print("\n1. Go to https://dashboard.render.com")
    print("2. Click on your Flask app (NOT the database)")
    print("3. Look at the top of the page - you'll see:")
    print("   • Service Name (e.g., 'mechanic-shop-api')")
    print("   • URL (e.g., 'https://mechanic-shop-api.onrender.com')")
    print("\n4. Your app URL will be in format: https://[service-name].onrender.com")
    print("\nExample URLs:")
    print("  • https://mechanic-shop-api.onrender.com")
    print("  • https://my-flask-app.onrender.com")
    print("  • https://service-12345.onrender.com")
    
    while True:
        app_url = input("\n📍 Enter your Render app URL: ").strip()
        
        if not app_url:
            print("❌ URL cannot be empty")
            continue
        
        if not app_url.startswith('https://'):
            print("⚠️  URL should start with 'https://'")
            app_url = 'https://' + app_url
        
        app_url = app_url.rstrip('/')
        
        print(f"\n✓ Using URL: {app_url}")
        confirm = input("Is this correct? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            return app_url
        else:
            print("Let's try again...")

def test_connection(app_url):
    """Test if we can reach the app"""
    print(f"\n🔗 Testing connection to {app_url}...")
    
    try:
        import requests
        response = requests.get(f"{app_url}/api/docs", timeout=10)
        
        if response.status_code == 200:
            print("✅ Connection successful! App is running.")
            return True
        elif response.status_code == 302:  # Redirect to /api/docs
            print("✅ Connection successful! App is running.")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print("   App might be sleeping. Waiting for it to wake up...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("   Possible reasons:")
        print("   • App is sleeping (free tier Render apps sleep after 15 min inactivity)")
        print("   • Wrong URL")
        print("   • App is not deployed yet")
        return False
    except Exception as e:
        print(f"⚠️  Error: {str(e)}")
        return False

def initialize_database(app_url):
    """Initialize database on Render"""
    print(f"\n{'='*70}")
    print("🚀 INITIALIZING DATABASE")
    print('='*70)
    
    try:
        import requests
        import json
        
        init_url = f"{app_url}/init-db"
        print(f"\n📡 Calling: POST {init_url}")
        
        response = requests.post(init_url, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201:
            print("\n✅ SUCCESS! Database tables created!")
            data = response.json()
            print("\nTables created:")
            for table in data.get('tables', []):
                print(f"  • {table}")
            return True
            
        elif response.status_code == 400:
            print("\n❌ ERROR! Database initialization failed!")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
            return False
        else:
            print(f"\n⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def main():
    """Main flow"""
    print("\n" + "="*70)
    print("🔧 MECHANIC SHOP API - RENDER INITIALIZATION HELPER")
    print("="*70)
    
    # Option to open dashboard
    open_dash = input("\nWould you like to open the Render dashboard? (yes/no): ").strip().lower()
    if open_dash in ['yes', 'y']:
        open_render_dashboard()
        input("\nPress Enter once you have your URL ready...")
    
    # Get app URL
    app_url = get_render_app_url()
    
    # Test connection
    if not test_connection(app_url):
        retry = input("\nRetry connection? (yes/no): ").strip().lower()
        if retry not in ['yes', 'y']:
            print("\n❌ Aborted. Please check your URL and try again.")
            sys.exit(1)
        if not test_connection(app_url):
            print("\n❌ Still cannot connect. Please:")
            print("   1. Make sure your app is deployed on Render")
            print("   2. Check the URL is correct")
            print("   3. Wait a moment if the app is starting up")
            sys.exit(1)
    
    # Initialize database
    if initialize_database(app_url):
        print("\n" + "="*70)
        print("✅ ALL DONE!")
        print("="*70)
        print("\nYour API is now ready to use! 🎉")
        print("\nNext steps:")
        print(f"  1. Visit: {app_url}/api/docs")
        print("  2. Try creating a customer, vehicle, or service ticket")
        print("  3. Everything should work now!")
    else:
        print("\n" + "="*70)
        print("❌ INITIALIZATION FAILED")
        print("="*70)
        print("\nPlease check:")
        print("  1. Your app URL is correct")
        print("  2. Your app is running on Render")
        print("  3. DATABASE_URL is set in Render environment variables")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
