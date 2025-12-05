import os
from flask import redirect
from app import create_app
from app.models import db
import requests

# Read environment from .env (defaults to 'development')
env = os.environ.get('FLASK_ENV', 'development')
config_name = 'DevelopmentConfig' if env == 'development' else 'ProductionConfig'

app = create_app(config_name)

@app.route('/', methods=['GET'])
def index():
    return redirect('/api/docs')

# Database initialization endpoint (one-time use)
@app.route('/init-db', methods=['POST'])
def init_db():
    """
    Initialize database tables.
    One-time use endpoint for Render deployment.
    
    Usage: POST https://your-app.onrender.com/init-db
    
    After running once, you can delete this endpoint or it will do nothing if tables exist.
    """
    try:
        with app.app_context():
            db.create_all()
        return {
            'status': 'success',
            'message': 'Database tables created successfully!',
            'tables': [
                'customer',
                'vehicle', 
                'mechanic',
                'service_ticket',
                'service_ticket_mechanic',
                'inventory',
                'service_ticket_part'
            ]
        }, 201
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error creating tables: {str(e)}'
        }, 400

# Test the init-db endpoint (uncomment to use)
# response = requests.post('https://your-app-name.onrender.com/init-db')
# print(response.json())

application = app

# Create tables only when running directly
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
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
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

