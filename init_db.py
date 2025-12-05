#!/usr/bin/env python3
"""
Database initialization script.
Run this once to create all tables in the database.

Usage:
    python3 init_db.py
    
Or on Render after deployment:
    python init_db.py
"""

from app import create_app
from app.models import db

def init_database():
    """Initialize the database with all tables"""
    # Create app context - will use DATABASE_URL if set (Render), otherwise local SQLite (dev)
    app = create_app('DevelopmentConfig')
    
    with app.app_context():
        print("🔧 Creating all database tables...")
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            print("\nTables created:")
            inspector = db.inspect(db.engine)
            for table_name in inspector.get_table_names():
                print(f"  • {table_name}")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = init_database()
    exit(0 if success else 1)
