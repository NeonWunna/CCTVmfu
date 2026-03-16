# 🔐 Google OAuth Setup Guide for Production

## ขั้นตอนการตั้งค่า Google OAuth สำหรับ Production Server

### 1. สร้าง Google OAuth Credentials

1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
2. เลือกหรือสร้างโปรเจค: **"CCTV MFU"**
3. ไปที่ **APIs & Services** → **Credentials**
4. คลิก **Create Credentials** → **OAuth client ID**
5. เลือก **Application type**: Web application
6. ตั้งชื่อ: **"CCTV MFU Production"**

### 2. เพิ่ม Authorized Redirect URIs

ใน **Authorized redirect URIs** ให้เพิ่ม:

**สำหรับ HTTP (ถ้าไม่มี SSL):**
```
http://your-server-domain.com/api/auth/google/callback
http://your-server-ip/api/auth/google/callback
```

**สำหรับ HTTPS (ถ้ามี SSL - แนะนำ):**
```
https://your-server-domain.com/api/auth/google/callback
https://your-server-ip/api/auth/google/callback
```

**ตัวอย่าง:**
- `http://cctv.mfu.ac.th/api/auth/google/callback`
- `http://192.168.1.100/api/auth/google/callback`
- `https://cctv.mfu.ac.th/api/auth/google/callback`

### 3. คัดลอก Credentials

1. คัดลอก **Client ID**
2. คัดลอก **Client Secret**

### 4. อัพเดทไฟล์ Environment บน Server

SSH เข้า server แล้วไปที่โฟลเดอร์โปรเจค:

```bash
cd /path/to/CCTVmfu
```

สร้างไฟล์ `.env` ใน root directory:

```bash
nano .env
```

เพิ่มเนื้อหาดังนี้:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# IMPORTANT: Change to your actual server URL!
GOOGLE_REDIRECT_URI=http://YOUR-SERVER-DOMAIN/api/auth/google/callback

# JWT Secret (you can keep this or generate new one)
JWT_SECRET_KEY=f0db8a2984d6777d5e5f2048ed560f257b9b0b98bee58b8914aecc6dc2a53164
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

**ตัวอย่างที่กรอกข้อมูลจริง:**
```env
GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnop
GOOGLE_REDIRECT_URI=http://cctv.mfu.ac.th/api/auth/google/callback
JWT_SECRET_KEY=f0db8a2984d6777d5e5f2048ed560f257b9b0b98bee58b8914aecc6dc2a53164
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

บันทึกไฟล์ (Ctrl+O, Enter, Ctrl+X)

### 5. Restart Docker Containers

```bash
# Stop containers
docker-compose down

# Start containers with new environment variables
docker-compose up -d

# Check logs to ensure everything is working
docker-compose logs -f backend
```

### 6. ตรวจสอบการตั้งค่า

เปิดเบราว์เซอร์ไปที่:
```
http://your-server-domain/api/auth/status
```

ควรได้ response:
```json
{
  "google_oauth_configured": true,
  "jwt_configured": true,
  "ready": true,
  "redirect_uri": "http://your-server-domain/api/auth/google/callback"
}
```

ถ้า `"ready": false` แสดงว่ายังตั้งค่าไม่ครบ ให้ตรวจสอบ `.env` อีกครั้ง

### 7. ทดสอบ Google Login

1. เปิด `http://your-server-domain/login`
2. คลิก **"Sign in with Google"**
3. ควรถูก redirect ไป Google login page
4. หลัง login สำเร็จจะกลับมาที่ dashboard

---

## สำคัญ! OAuth Consent Screen

ถ้าคุณใช้ Google Workspace (MFU email):
- User type: **Internal** (เฉพาะคนใน organization)
- ไม่ต้อง verify app

ถ้าคุณใช้ Google account ทั่วไป:
- User type: **External**
- ต้อง configure OAuth consent screen
- เพิ่ม test users (หรือ publish app)

---

## Troubleshooting

### ปัญหา: "redirect_uri_mismatch"
**วิธีแก้:**
- ตรวจสอบว่า redirect URI ใน Google Cloud Console ตรงกับ `.env` หรือไม่
- ตรวจสอบว่าใช้ http หรือ https ให้ตรงกัน
- ลองใช้ทั้ง domain name และ IP address

### ปัญหา: "Could not validate credentials"
**วิธีแก้:**
- ตรวจสอบว่า JWT_SECRET_KEY ถูกต้อง
- Restart backend container: `docker-compose restart backend`

### ปัญหา: API endpoints ไม่ต้อง authentication
**วิธีแก้:**
- ตรวจสอบว่า backend มี token ใน Authorization header
- เปิด DevTools → Network → ดู request headers

---

## Next Steps

หลังจากตั้งค่าเสร็จแล้ว:

1. ✅ ทดสอบ login ด้วย Google account
2. ✅ ทดสอบ access camera endpoints
3. ✅ ตรวจสอบว่า logout ทำงาน
4. 🔒 พิจารณาใช้ HTTPS (SSL/TLS) สำหรับความปลอดภัย
5. 🔐 พิจารณา restrict OAuth consent screen ให้เฉพาะ MFU domain

---

## Security Recommendations

### Production Security Checklist:
- [ ] ใช้ HTTPS (SSL/TLS certificate)
- [ ] เปลี่ยน JWT_SECRET_KEY เป็นค่าใหม่ที่ unique
- [ ] Set OAuth consent screen เป็น Internal (ถ้าใช้ Google Workspace)
- [ ] จำกัด CORS origins ใน backend/app/main.py
- [ ] Enable firewall บน server
- [ ] Regular backup database
- [ ] Monitor authentication logs

---

**หมายเหตุ:** ไฟล์ `.env` ไม่ควร commit ลง Git เพราะมี sensitive data
