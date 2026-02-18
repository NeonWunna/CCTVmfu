
import logging
from sqlalchemy import text
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_blur_columns():
    db = SessionLocal()
    try:
        logger.info("Checking and adding blur columns to 'cameras' table...")
        
        # We use raw SQL to add columns safely (if not exists logic often requires more complex SQL blocks in Postgres, 
        # but simple ALTER TABLE ADD COLUMN IF NOT EXISTS is supported in newer Postgres)
        
        # 1. image_status
        try:
            db.execute(text("ALTER TABLE cameras ADD COLUMN IF NOT EXISTS image_status VARCHAR(20) DEFAULT 'normal' NOT NULL"))
            logger.info("Added 'image_status' column.")
        except Exception as e:
            logger.warning(f"Could not add 'image_status' (might exist): {e}")
            db.rollback()

        # 2. blur_score
        try:
            db.execute(text("ALTER TABLE cameras ADD COLUMN IF NOT EXISTS blur_score FLOAT"))
            logger.info("Added 'blur_score' column.")
        except Exception as e:
            logger.warning(f"Could not add 'blur_score' (might exist): {e}")
            db.rollback()

        # 3. last_blur_check
        try:
            db.execute(text("ALTER TABLE cameras ADD COLUMN IF NOT EXISTS last_blur_check VARCHAR(50)"))
            logger.info("Added 'last_blur_check' column.")
        except Exception as e:
            logger.warning(f"Could not add 'last_blur_check' (might exist): {e}")
            db.rollback()
            
        db.commit()
        logger.info("Migration completed successfully.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_blur_columns()
