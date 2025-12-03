"""
Migration script to add password column to customer table.
Run this once to update your database schema.
"""
from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app('DevelopmentConfig')

with app.app_context():
    try:
        # Add password column to customer table
        db.session.execute(text(
            "ALTER TABLE customer ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'changeme'"
        ))
        db.session.commit()
        print("✅ Successfully added 'password' column to customer table")
        print("⚠️  Default password is 'changeme' - users should update their passwords")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print("ℹ️  Column 'password' already exists - no changes needed")
        else:
            print(f"❌ Error: {e}")
            db.session.rollback()
