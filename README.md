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
docker-compose up -d --build
```

### Troubleshooting

#### KeyError: 'ContainerConfig'

If you encounter the following error during `docker-compose up`:

```
KeyError: 'ContainerConfig'
```

This is caused by an incompatibility between `docker-compose` version 1.29.2 (or older) and images built with Docker BuildKit.

**Solution 1: Disable BuildKit (Recommended for older Compose)**

Run the command with `DOCKER_BUILDKIT=0`:

```bash
DOCKER_BUILDKIT=0 docker-compose up -d --build
```

**Solution 2: Upgrade Docker Compose**

Upgrade to Docker Compose V2.

```bash
# Example for Linux
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Database Schema Issues

If you see errors related to database schema mismatches, you may need to reset the database (WARNING: Data loss):

```bash
docker-compose exec backend python scripts/reset_db.py
```
