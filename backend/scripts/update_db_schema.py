import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine

def update_schema():
    print("Updating database schema...")
    with engine.connect() as connection:
        # Check if columns exist (simple try/except for SQLite/Postgres compatibility in a raw way)
        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE ADD COLUMN until recent versions,
        # so we'll just try and ignore errors if they exist.
        
        columns = [
            ("image_status", "VARCHAR(20) DEFAULT 'normal'"),
            ("sharpness_value", "FLOAT"), 
            ("last_image_check", "TIMESTAMP"),
            ("blur_consistency_count", "INTEGER DEFAULT 0"),
            ("normal_consistency_count", "INTEGER DEFAULT 0"),
            ("building", "VARCHAR(100)"),
            ("floor", "VARCHAR(20)"),
            ("position", "VARCHAR(255)"),
        ]
        
        for col_name, col_type in columns:
            print(f"Adding column {col_name} if not exists...")
            connection.execute(text(f"ALTER TABLE cameras ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
            print(f"  OK: {col_name}")

        connection.commit()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
