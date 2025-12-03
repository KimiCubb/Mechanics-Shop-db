from app import create_app
from app.models import db

app = create_app('DevelopmentConfig')

# Create tables within application context
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

if __name__ == '__main__':
    print("🚀 Starting Mechanic Shop API...")
    print("=" * 50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("=" * 50)
    print("📌 Available Endpoints:")
    print("   • Customers:       http://127.0.0.1:5000/customers")
    print("   • Vehicles:        http://127.0.0.1:5000/vehicles")
    print("   • Mechanics:       http://127.0.0.1:5000/mechanics")
    print("   • Service Tickets: http://127.0.0.1:5000/service-tickets")
    print("=" * 50)
    app.run(debug=True)
