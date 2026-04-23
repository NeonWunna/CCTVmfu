# 🎥 CCTV MFU — ระบบบริหารจัดการกล้องวงจรปิด มหาวิทยาลัยแม่ฟ้าหลวง

ระบบ Web Application สำหรับตรวจสอบ บริหารจัดการ และ Streaming กล้อง CCTV ภายในมหาวิทยาลัยแม่ฟ้าหลวง (MFU) รองรับกล้องหลายร้อยตัว พร้อมระบบตรวจสอบสถานะอัตโนมัติ, ตรวจจับภาพเบลอ, และ AI Assistant ผ่าน MCP Protocol

---

## 📋 สารบัญ

- [ภาพรวมระบบ](#-ภาพรวมระบบ)
- [Technology Stack](#-technology-stack)
- [สถาปัตยกรรมระบบ](#-สถาปัตยกรรมระบบ)
- [โครงสร้างโปรเจกต์](#-โครงสร้างโปรเจกต์)
- [การทำงานของระบบ](#-การทำงานของระบบ)
- [ระบบ Authentication](#-ระบบ-authentication)
- [API Endpoints](#-api-endpoints)
- [Background Workers](#-background-workers)
- [การ Streaming วิดีโอ](#-การ-streaming-วิดีโอ)
- [MCP Server (AI Integration)](#-mcp-server-ai-integration)
- [Database Schema](#-database-schema)
- [สิทธิ์การใช้งาน (Roles)](#-สิทธิ์การใช้งาน-roles)
- [การติดตั้งและรัน](#-การติดตั้งและรัน)
- [Environment Variables](#-environment-variables)

---

## 🔭 ภาพรวมระบบ

```
ผู้ใช้งาน (Browser)
      │
      ▼
  ┌─────────┐
  │  Nginx  │  ← Reverse Proxy (Port 80/443)
  └────┬────┘
       │
  ┌────┴────────────────────────────┐
  │                                 │
  ▼                                 ▼
┌──────────┐                  ┌──────────┐
│ Frontend │                  │ Backend  │
│ Vue 3    │                  │ FastAPI  │
│ Port 8010│                  │ Port 8020│
└──────────┘                  └─────┬────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                   ┌──────────┐          ┌──────────┐
                   │PostgreSQL│          │ go2rtc   │
                   │   DB     │          │ Streaming│
                   └──────────┘          │ Port 1984│
                                         └──────────┘
```

**ฟีเจอร์หลัก:**
- 🗺️ แสดงแผนที่กล้องทั้งหมดบน Interactive Map (Leaflet.js)
- 📡 ตรวจสอบสถานะกล้องแบบ Real-time (Online / Offline / No Signal / Blurry)
- 🎬 ดูภาพ Live Stream ผ่าน WebRTC / MSE โดย go2rtc
- 🔍 ตรวจจับภาพเบลออัตโนมัติด้วย OpenCV (Laplacian Variance)
- 👤 Login ด้วย Google OAuth 2.0
- 🤖 AI Assistant ผ่าน MCP Protocol (WebSocket)
- 🔐 ระบบสิทธิ์ 3 ระดับ: User / Admin / SuperAdmin

---

## 🛠️ Technology Stack

### Backend
| เทคโนโลยี | เวอร์ชัน | หน้าที่ |
|---|---|---|
| **Python** | 3.11+ | ภาษาหลัก |
| **FastAPI** | Latest | Web Framework, REST API |
| **SQLAlchemy** | Latest | ORM |
| **PostgreSQL** | 15 | ฐานข้อมูลหลัก (Production) |
| **SQLite** | Built-in | ฐานข้อมูล (Development) |
| **Uvicorn** | Latest | ASGI Server |
| **OpenCV** | Headless | ตรวจจับภาพเบลอ |
| **Authlib** | Latest | Google OAuth 2.0 |
| **python-jose** | Latest | JWT Token |
| **Pydantic** | v2 | Data Validation |

### Frontend
| เทคโนโลยี | เวอร์ชัน | หน้าที่ |
|---|---|---|
| **Vue.js** | 3.4 | UI Framework |
| **Vite** | 5 | Build Tool |
| **Pinia** | 2 | State Management |
| **Vue Router** | 4 | Client-side Routing |
| **Leaflet.js** | 1.9 | Interactive Map |
| **Axios** | 1.6 | HTTP Client |
| **jwt-decode** | 4 | JWT Parsing |

### Infrastructure
| เทคโนโลยี | หน้าที่ |
|---|---|
| **Docker + Docker Compose** | Container Orchestration |
| **Nginx** | Reverse Proxy, Load Balancer |
| **go2rtc** | RTSP → WebRTC/MSE Streaming |

---

## 🏗️ สถาปัตยกรรมระบบ

### Container ใน Docker Compose

| Container | Image | Port | หน้าที่ |
|---|---|---|---|
| `cctv_nginx` | Custom Nginx | 80, 443 | Entry point หลัก, Reverse Proxy |
| `cctv_frontend` | Vue + Nginx | 8010 | Serve SPA |
| `cctv_backend` | Python + FastAPI | 8020 | REST API + Background Workers |
| `cctv_db` | postgres:15 | 5432 | ฐานข้อมูล |
| `cctv_go2rtc` | alexxit/go2rtc:1.9.14 | 1984, 8554, 8555 | Video Streaming |

### Nginx Routing

| Path | Proxy ไปยัง | หมายเหตุ |
|---|---|---|
| `/` | `frontend:80` | Vue SPA |
| `/api/` | `backend:8020` | REST API |
| `/mcp/` | `backend:8020/mcp/` | MCP WebSocket |
| `/stream/` | `go2rtc:1984/` | Video Stream |
| `/docs` | `backend:8020/docs` | FastAPI Swagger UI |

---

## 📂 โครงสร้างโปรเจกต์

```
CCTVmfu/
├── docker-compose.yml        # ← ประกอบ Services ทั้งหมด
├── .env.example              # ← ตัวอย่าง Environment Variables
├── nginx/
│   ├── nginx.conf            # ← Reverse Proxy Config
│   └── Dockerfile
├── go2rtc/
│   └── go2rtc.yaml           # ← Config สำหรับ Streaming
│
├── backend/                  # ← FastAPI Application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # ← Entry point, lifespan, middleware
│       ├── core/
│       │   └── config.py     # ← Settings (Pydantic BaseSettings)
│       ├── db/
│       │   ├── base.py       # ← SQLAlchemy Base
│       │   └── session.py    # ← DB Engine & Session
│       ├── models/
│       │   ├── camera.py     # ← Camera Table
│       │   └── user.py       # ← User Table
│       ├── schemas/          # ← Pydantic Schemas (Request/Response)
│       ├── routers/
│       │   ├── auth.py       # ← /api/auth/* (Google OAuth, JWT)
│       │   ├── cameras.py    # ← /api/cameras/* (CRUD + Stream)
│       │   ├── users.py      # ← /api/users/*
│       │   ├── mcp.py        # ← /mcp/ws (WebSocket MCP Server)
│       │   └── health.py     # ← /api/health
│       ├── services/
│       │   ├── camera.py     # ← Business Logic กล้อง
│       │   ├── auth.py       # ← OAuth + JWT Logic
│       │   ├── ping_worker.py    # ← Background: ตรวจสอบสถานะ
│       │   ├── blur_worker.py    # ← Background: ตรวจจับเบลอ
│       │   └── mcp_service.py   # ← MCP Tool Handlers
│       └── utils/
│           └── network.py    # ← ping_ip, check_port
│
└── frontend/                 # ← Vue 3 Application
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js           # ← App bootstrap, Pinia, Router
        ├── App.vue           # ← Root component
        ├── router/
        │   └── index.js      # ← Route definitions + Auth Guard
        ├── stores/
        │   └── auth.js       # ← Pinia Auth Store
        ├── views/
        │   ├── Login.vue     # ← หน้า Login Google
        │   ├── Home.vue      # ← หน้าแผนที่ + Dashboard
        │   ├── CameraSettings.vue  # ← จัดการกล้อง (Admin)
        │   ├── CameraView.vue      # ← ดู Live Stream
        │   └── AdminPanel.vue      # ← จัดการ Users (SuperAdmin)
        ├── services/         # ← Axios API Calls
        └── utils/
            └── jwt.js        # ← Token decode/validation
```

---

## ⚙️ การทำงานของระบบ

### 1. Startup Sequence

เมื่อ Backend เริ่มทำงาน (`lifespan` ใน `main.py`):

```
FastAPI เริ่มต้น
    │
    ├─► สร้าง Database Tables (SQLAlchemy auto-create)
    │
    ├─► เริ่ม PingWorker (Background Task)
    │     └─ วนตรวจสถานะกล้องทุก 30 วินาที
    │
    └─► เริ่ม BlurWorker (Background Task)
          └─ วนตรวจภาพเบลอทุก 6 ชั่วโมง (21600s)
```

### 2. การแสดงผลหน้าแผนที่ (Home.vue)

```
โหลดหน้า Home
    │
    ├─► ดึงข้อมูลกล้องทั้งหมด GET /api/cameras
    │
    ├─► แสดง Marker บน Leaflet Map (coordinates จาก DB)
    │
    ├─► แสดง Status Badge (online/offline/no_signal/blurry)
    │
    └─► Polling ทุก X วินาที เพื่ออัปเดตสถานะ
```

### 3. การตรวจสอบสถานะกล้อง (PingWorker)

```
ทุก 30 วินาที:
    │
    ├─► ดึงกล้องทั้งหมดจาก DB
    │
    └─► ตรวจสอบพร้อมกัน (Semaphore: 200 concurrent)
          │
          ├─► Port 80 ปิด → status = "offline"
          │
          ├─► Port 80 เปิด + ไม่มี RTSP URL → status = "no_signal"
          │
          ├─► Port 80 เปิด + RTSP URL มี + Port 554 ปิด → status = "no_signal"
          │
          ├─► Port 80 เปิด + Port 554 เปิด + เคย blurry → คง "blurry"
          │
          └─► Port 80 เปิด + Port 554 เปิด → status = "online"
```

### 4. การตรวจจับภาพเบลอ (BlurWorker)

```
ทุก 6 ชั่วโมง:
    │
    ├─► ดึงกล้องที่ status = "online" หรือ "blurry" เท่านั้น
    │
    └─► ประมวลผลเป็น Batch (50 ตัว/รอบ), Concurrent: 5
          │
          ├─► ขอ Frame JPEG จาก go2rtc API
          │     └─ GET http://cctv_go2rtc:1984/api/frame.jpeg?src={rtsp_url}
          │
          ├─► แปลงเป็น Grayscale + Downscale → 480px
          │
          ├─► คำนวณ Laplacian Variance
          │     ├─ variance < 50 → "blur" (เบลอ)
          │     └─ variance ≥ 50 → "normal" (ชัด)
          │
          └─► อัปเดต DB:
                ├─ image_status, sharpness_value, last_image_check
                └─ status = "blurry" / "online"
```

---

## 🔐 ระบบ Authentication

ใช้ **Google OAuth 2.0** + **JWT Token**

### ขั้นตอน Login

```
1. ผู้ใช้กด "Login with Google"
       │
2. Redirect → GET /api/auth/google
       │
3. Redirect → Google Consent Screen
       │
4. Google Callback → GET /api/auth/google/callback
       │
5. Backend: สร้าง/อัปเดต User ใน DB
       │
6. สร้าง JWT Token (expire: 7 วัน)
       │
7. Redirect → Frontend /login?token=<JWT>
       │
8. Frontend เก็บ Token ใน localStorage
       │
9. ทุก API Request ส่ง: Authorization: Bearer <JWT>
```

### JWT Payload

```json
{
  "sub": "user_id",
  "email": "user@mfu.ac.th",
  "role": "admin",
  "exp": 1234567890
}
```

### Route Guard (Vue Router)

| Route | ต้องการ |
|---|---|
| `/login` | Public |
| `/` (แผนที่) | Login แล้ว |
| `/camera-settings` | Admin หรือ SuperAdmin |
| `/camera/:id` | Admin หรือ SuperAdmin |
| `/admin` | SuperAdmin เท่านั้น |

---

## 📡 API Endpoints

### Authentication

| Method | Path | หน้าที่ |
|---|---|---|
| GET | `/api/auth/google` | เริ่ม OAuth Flow |
| GET | `/api/auth/google/callback` | รับ callback จาก Google |
| GET | `/api/auth/me` | ข้อมูล User ปัจจุบัน |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/status` | ตรวจสอบ Config OAuth |

### Cameras

| Method | Path | หน้าที่ | สิทธิ์ |
|---|---|---|---|
| GET | `/api/cameras` | ดึงกล้องทั้งหมด | ทุกคน |
| POST | `/api/cameras` | เพิ่มกล้อง | Admin+ |
| GET | `/api/cameras/{id}` | ดึงข้อมูลกล้อง 1 ตัว | ทุกคน |
| PUT | `/api/cameras/{id}` | แก้ไขข้อมูลกล้อง | Admin+ |
| DELETE | `/api/cameras/{id}` | ลบกล้อง | Admin+ |
| POST | `/api/cameras/{id}/check` | ตรวจสถานะกล้อง (manual) | Admin+ |
| POST | `/api/cameras/{id}/check-blur` | ตรวจภาพเบลอ (manual) | Admin+ |
| GET | `/api/cameras/{id}/stream` | Redirect ไป go2rtc stream | Admin+ |

### Health

| Method | Path | หน้าที่ |
|---|---|---|
| GET | `/api/health` | ตรวจสอบว่า API ทำงานปกติ |

---

## 🔄 Background Workers

### PingWorker

```python
class PingWorker:
    concurrent_limit = 200  # ตรวจพร้อมกันสูงสุด 200 ตัว
    interval = 30           # วินาที
```

- ใช้ `asyncio.Semaphore` ควบคุม Concurrency
- ตรวจ Port 80 (Web Interface) และ 554 (RTSP)
- อัปเดต `status` และ `last_update` ใน DB

### BlurWorker

```python
class BlurWorker:
    check_interval = 21600  # 6 ชั่วโมง
    threshold = 50.0        # Laplacian Variance threshold
    concurrent = 5          # ตรวจพร้อมกัน 5 ตัว
    batch_size = 50         # 50 ตัว/รอบ
    processing_width = 480  # ลด Resolution ก่อนประมวลผล
    per_camera_timeout = 15 # วินาที (hard timeout)
```

- ใช้ `asyncio.to_thread()` รัน OpenCV ใน Thread Pool
- Commit DB ทุก Batch เพื่อลดการใช้ RAM
- Force `gc.collect()` ระหว่าง Batch

---

## 🎬 การ Streaming วิดีโอ

ใช้ **go2rtc** เป็น Media Server

```
กล้อง CCTV
    │ (RTSP rtsp://ip:554/stream)
    ▼
go2rtc (Port 1984)
    │
    ├─► WebRTC  ← Browser สมัยใหม่ (latency ต่ำ)
    └─► MSE     ← Fallback สำหรับ Cross-subnet
```

### การเล่นวิดีโอใน Frontend

1. Backend คำนวณ RTSP URL ของกล้อง
2. Encode URL → Redirect ไป `/stream/webrtc.html?src={encoded_rtsp_url}`
3. Nginx Proxy `/stream/` ไปยัง `go2rtc:1984/`
4. go2rtc รับ RTSP → แปลงเป็น WebRTC/MSE ส่งกลับ Browser

---

## 🤖 MCP Server (AI Integration)

ระบบรองรับ **Model Context Protocol (MCP)** ผ่าน WebSocket ที่ `/mcp/ws`

ทำให้ AI Assistant (เช่น Claude) สามารถ Query ข้อมูลกล้องได้โดยตรง

### MCP Tools

#### `check_camera_status`
ตรวจสอบสถานะกล้อง Real-time โดย Ping IP
```json
{
  "name": "check_camera_status",
  "arguments": { "location": "ประตูหน้า" }
}
```

#### `find_cameras_by_location`
ค้นหากล้องจาก DB (ไม่ Ping)
```json
{
  "name": "find_cameras_by_location",
  "arguments": { "location": "อาคาร E" }
}
```

### MCP Protocol Flow

```
AI Client → WebSocket Connect → /mcp/ws
    │
    ├─► Send: {"method": "initialize", ...}
    ├─► Recv: {"protocolVersion": "2024-11-05", ...}
    │
    ├─► Send: {"method": "tools/list"}
    ├─► Recv: [check_camera_status, find_cameras_by_location]
    │
    ├─► Send: {"method": "tools/call", "params": {...}}
    └─► Recv: {"result": {"content": [{"type": "text", "text": "..."}]}}
```

---

## 🗄️ Database Schema

### ตาราง `cameras`

| Column | Type | หมายเหตุ |
|---|---|---|
| `id` | Integer (PK) | Auto increment |
| `name` | String(255) | ชื่อกล้อง |
| `location` | String(255) | สถานที่ติดตั้ง |
| `ip_address` | String(45) | IP (Unique, รองรับ IPv6) |
| `coordinates` | String(100) | `"lat, long"` |
| `brand` | String(100) | ยี่ห้อกล้อง |
| `status` | String(20) | `online/offline/no_signal/blurry` |
| `rtsp_url` | String(500) | RTSP Stream URL |
| `version` | String(500) | Firmware Version |
| `last_update` | String(50) | เวลาอัปเดตสถานะล่าสุด |
| `image_status` | String(20) | `normal/blur` |
| `last_image_check` | String(50) | เวลาตรวจเบลอล่าสุด |
| `sharpness_value` | Float | ค่า Laplacian Variance |
| `created_at` | DateTime | วันที่สร้าง |
| `updated_at` | DateTime | วันที่แก้ไขล่าสุด |

### ตาราง `users`

| Column | Type | หมายเหตุ |
|---|---|---|
| `id` | Integer (PK) | Auto increment |
| `email` | String(255) | อีเมล (Unique) |
| `google_id` | String(255) | Google Account ID (Unique) |
| `name` | String(255) | ชื่อแสดง |
| `picture` | String(500) | URL รูปโปรไฟล์ |
| `role` | String(50) | `user / admin / superadmin` |
| `created_at` | DateTime | วันที่สร้าง |
| `updated_at` | DateTime | วันที่แก้ไขล่าสุด |

---

## 👥 สิทธิ์การใช้งาน (Roles)

| Role | ดูแผนที่ | ดู Stream | จัดการกล้อง | จัดการ Users |
|---|---|---|---|---|
| **user** | ✅ | ❌ | ❌ | ❌ |
| **admin** | ✅ | ✅ | ✅ | ❌ |
| **superadmin** | ✅ | ✅ | ✅ | ✅ |

> SuperAdmin กำหนดโดย Environment Variable `SUPERADMIN_EMAILS` (comma-separated)

---

## 🚀 การติดตั้งและรัน

### Prerequisites
- Docker + Docker Compose
- Google Cloud Console Project (สำหรับ OAuth)

## SERVER SMART CCTV
Server Smart CCTV
OS : ubuntu240.4
IP : 192.168.11.67
user : scctv
password : d]hv';'0ixbF@@fvy0ibPt008
โดยที่ user scctv สามารถ sudo su - เป็น root ได้

### ขั้นตอน

```bash
# 1. Clone Repository
git clone <repo-url>
cd CCTVmfu

# 2. ตั้งค่า Environment Variables
cp .env.example .env
# แก้ไข .env ใส่ค่าจริง

# 3. รันด้วย Docker Compose
docker-compose up -d

# 4. ตรวจสอบ
docker-compose ps
docker-compose logs -f backend
```

### Development Mode (ไม่ใช้ Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8020

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🔧 Environment Variables

| Variable | ค่าตัวอย่าง | หมายเหตุ |
|---|---|---|
| `GOOGLE_CLIENT_ID` | `xxx.apps.googleusercontent.com` | จาก Google Console |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-xxx` | จาก Google Console |
| `GOOGLE_REDIRECT_URI` | `http://your-domain/api/auth/google/callback` | ต้องตรงกับใน Console |
| `FRONTEND_URL` | `http://your-domain` | URL ของ Frontend |
| `JWT_SECRET_KEY` | `random-hex-string` | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | 7 วัน |
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/cctv_db` | Production |
| `SUPERADMIN_EMAILS` | `admin@mfu.ac.th,it@mfu.ac.th` | คั่นด้วย comma |

---

## 📜 Scripts ช่วยงาน

### นำเข้าข้อมูลกล้องจาก JSON

```bash
cd backend/scripts
python import_cctv.py
```

ไฟล์ JSON ที่รองรับ: `RTSP กล้องเก่ามอ.json` — ใช้สำหรับ Import ข้อมูลกล้องเก่าเข้าสู่ระบบ

---

## 🧪 การทดสอบ

```bash
cd backend
pytest tests/ -v
```

---

*เอกสารนี้จัดทำโดยอัตโนมัติจากการวิเคราะห์ Source Code — อัปเดตล่าสุด เมษายน 2026*
