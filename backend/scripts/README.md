# Import CCTV Data Scripts

## Run Locally (SQLite or Local Postgres)
Ensure you are in the project root directory.
```bash
# Import Data
python backend/scripts/import_cctv.py

# Verify Import
python backend/scripts/verify_import.py
```

## Run in Docker (Production/Dev Container)
If you are running the stack with Docker Compose:
```bash
# Import Data
docker-compose exec backend python scripts/import_cctv.py

## Reviewing Changes in Docker
If you added new scripts or changed code, ensure they are synced to the container.
Since we added a volume mount, just restart if needed, or if you haven't applied the volume change yet:
```bash
docker-compose up -d backend
```

## Troubleshooting
If you encounter errors like `invalid input syntax for type integer: "Guardhouse-ANPR-01"`, it means your database schema is incorrect (e.g., `name` column has wrong type).
You can reset the database using the reset script (WARNING: Deletes all data):

```bash
# Reset Database (Docker)
docker-compose exec backend python scripts/reset_db.py
```

# Optional: Inspect Schema
To check the current database schema:
```bash
docker-compose exec backend python scripts/inspect_schema.py
```
