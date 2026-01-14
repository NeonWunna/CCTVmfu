# CCTV Monitoring Backend API

Backend API server for CCTV Monitoring System - MFU

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Run development server:
```bash
npm run dev
```

4. Run production server:
```bash
npm start
```

## API Endpoints

### Health Check
- `GET /api/health` - Check API status

### CCTV
- `GET /api/cctvs` - Get all CCTV cameras
- `GET /api/cctvs/:id` - Get specific CCTV camera

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

## Port

Default port: `3000` (configurable via `.env`)
