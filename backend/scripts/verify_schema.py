import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.db.session import engine

def verify_schema():
    print("Verifying database schema...")
    inspector = inspect(engine)
    if not inspector.has_table("cameras"):
        print("Table 'cameras' does not exist.")
        return

    columns = inspector.get_columns("cameras")
    column_names = [col['name'] for col in columns]
    
    expected_columns = [
        "image_status",
        "sharpness_value",
        "last_image_check",
        "blur_consistency_count",
        "normal_consistency_count"
    ]
    
    missing = [col for col in expected_columns if col not in column_names]
    
    if missing:
        print(f"Missing columns: {missing}")
    else:
        print("All expected columns operate correctly.")
        
    print(f"Existing columns: {column_names}")

if __name__ == "__main__":
    verify_schema()
