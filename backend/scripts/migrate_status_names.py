import sys
import os

# Add parent directory to path to import app modules
# Assumes script is run from backend/scripts/ or backend root via python -m scripts.migrate_status_names
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine

def migrate_status():
    print("Migrating status values...")
    with engine.connect() as connection:
        try:
            # Update 'up' -> 'online'
            result = connection.execute(text("UPDATE cameras SET status = 'online' WHERE status = 'up'"))
            print(f"Updated {result.rowcount} cameras from 'up' to 'online'")
            
            # Update 'down' -> 'offline'
            result = connection.execute(text("UPDATE cameras SET status = 'offline' WHERE status = 'down'"))
            print(f"Updated {result.rowcount} cameras from 'down' to 'offline'")
            
            connection.commit()
            print("Migration complete.")
        except Exception as e:
            print(f"Error migrating status: {e}")

if __name__ == "__main__":
    migrate_status()
