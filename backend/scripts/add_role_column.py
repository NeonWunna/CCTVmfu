"""
Migration: Add role column to users table.
Run this script once after deploying the superadmin role feature.

Usage:
    docker exec cctv_backend python scripts/add_role_column.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings


def migrate():
    print("Starting migration: add role column to users table...")

    with engine.connect() as connection:
        # Add 'role' column if it doesn't already exist
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user'"))
            connection.commit()
            print("✓ Added 'role' column to users table")
        except Exception as e:
            print(f"⚠ Could not add column (might already exist): {e}")

        # Set superadmin role for configured emails
        superadmin_emails = [e.strip() for e in settings.SUPERADMIN_EMAILS.split(",") if e.strip()]
        if superadmin_emails:
            for email in superadmin_emails:
                try:
                    result = connection.execute(
                        text("UPDATE users SET role = 'superadmin' WHERE email = :email"),
                        {"email": email}
                    )
                    connection.commit()
                    if result.rowcount > 0:
                        print(f"✓ Set superadmin role for: {email}")
                    else:
                        print(f"ℹ User not found yet (will be set on first login): {email}")
                except Exception as e:
                    print(f"✗ Error updating role for {email}: {e}")
        else:
            print("ℹ No SUPERADMIN_EMAILS configured")

    print("Migration complete.")


if __name__ == "__main__":
    migrate()
