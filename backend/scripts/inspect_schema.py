import sys
import os
from sqlalchemy import inspect

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine

def inspect_schema():
    inspector = inspect(engine)
    table_name = "cameras"
    
    if inspector.has_table(table_name):
        print(f"Table '{table_name}' exists.")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"Column: {column['name']}, Type: {column['type']}")
    else:
        print(f"Table '{table_name}' does not exist.")

if __name__ == "__main__":
    inspect_schema()
