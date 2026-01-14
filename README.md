# CCTV Monitoring System - MFU

ระบบ monitoring CCTV สำหรับมหาวิทยาลัยแม่ฟ้าหลวง (Mae Fah Luang University)

## โครงสร้างโปรเจกต์

โปรเจกต์นี้แยกเป็น 2 ส่วน:

- **Frontend** (`frontend/`) - Vue 3 + Vite application
- **Backend** (`backend/`) - Express.js API server

## การติดตั้ง

### ติดตั้งทั้งหมด (แนะนำ)
```bash
npm run install:all
```

### ติดตั้งแยกส่วน

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd backend
npm install
```

## การรัน

### รันทั้ง Frontend และ Backend พร้อมกัน
```bash
npm run dev
```

### รันแยกส่วน

**Frontend only:**
```bash
npm run dev:frontend
# หรือ
cd frontend && npm run dev
```

**Backend only:**
```bash
npm run dev:backend
# หรือ
cd backend && npm run dev
```

## Ports

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:3000`

## Build

```bash
npm run build
```

ไฟล์ build จะอยู่ใน `frontend/dist/`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/cctvs` - Get all CCTV cameras
- `GET /api/cctvs/:id` - Get specific CCTV camera
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

## เทคโนโลยีที่ใช้

### Frontend
- Vue 3
- Vue Router
- Vite
- Leaflet (Map)

### Backend
- Express.js
- CORS
- dotenv