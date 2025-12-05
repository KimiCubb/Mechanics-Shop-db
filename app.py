import os
from app import create_app
from app.models import db

# Use ProductionConfig if DATABASE_URL is set (Render), otherwise DevelopmentConfig
config_name = 'ProductionConfig' if os.environ.get('DATABASE_URL') else 'DevelopmentConfig'
app = create_app(config_name)

# Create tables within application context
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not create tables: {e}")
        print("   This is normal if tables already exist in production.")

if __name__ == '__main__':
    print("🚀 Starting Mechanic Shop API...")
    print("=" * 60)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("=" * 60)
    print("📌 Available Endpoints:")
    print("   • Customers:       http://127.0.0.1:5000/customers")
    print("   • Vehicles:        http://127.0.0.1:5000/vehicles")
    print("   • Mechanics:       http://127.0.0.1:5000/mechanics")
    print("   • Service Tickets: http://127.0.0.1:5000/service-tickets")
    print("   • Inventory:       http://127.0.0.1:5000/inventory")
    print("=" * 60)
    print("🔐 Authentication Endpoints:")
    print("   • POST /customers/login      - Get auth token")
    print("   • GET  /customers/my-tickets - Get your tickets (requires token)")
    print("=" * 60)
    print("📊 Advanced Endpoints:")
    print("   • GET  /mechanics/top-performers       - Mechanics by ticket count")
    print("   • PUT  /service-tickets/<id>/edit      - Add/remove mechanics")
    print("   • POST /service-tickets/<id>/add-part  - Add part to ticket")
    print("   • GET  /customers/?page=1&per_page=10  - Paginated customers")
    print("=" * 60)
    app.run(debug=True)

