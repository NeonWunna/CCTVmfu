# CCTV MFU Project

This project contains a backend API and frontend for the MFU CCTV system.

## Project Structure

- `backend/`: FastAPI backend
- `frontend/`: Vue.js frontend
- `nginx/`: Nginx configuration
- `docker-compose.yml`: Docker Compose configuration

## Deployment

### Prerequisites

- Docker
- Docker Compose

### Running with Docker Compose

To start the application:

```bash
docker compose up -d --build
```

### Troubleshooting

#### KeyError: 'ContainerConfig'

If you encounter `KeyError: 'ContainerConfig'` during `docker-compose up`, this is due to an incompatibility between legacy `docker-compose` (v1) and modern Docker Engine.

**Solution 1: Use `docker compose` (v2) (Recommended)**

Instead of `docker-compose`, use the modern command:

```bash
docker compose up -d --build
```

**Solution 2: Disable BuildKit (Workaround for v1)**

If you must use v1, disable BuildKit:

```bash
DOCKER_BUILDKIT=0 docker-compose up -d --build
```

#### Database Schema Issues

If you see errors related to database schema mismatches, you may need to reset the database (WARNING: Data loss):

```bash
docker compose exec backend python scripts/reset_db.py
```
