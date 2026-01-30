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

# Verify Import
docker-compose exec backend python scripts/verify_import.py
```
