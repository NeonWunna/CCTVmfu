import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'CCTV Monitoring API is running' });
});

// CCTV endpoints
app.get('/api/cctvs', (req, res) => {
  // Mock data - replace with actual database query
  const cctvs = [
    { 
      id: 1,
      name: "Main Gate CCTV", 
      lat: 20.0450, 
      lng: 99.8925, 
      status: "up",
      location: "Main Entrance",
      lastUpdate: "2 min ago"
    },
    { 
      id: 2,
      name: "Library CCTV", 
      lat: 20.0442, 
      lng: 99.8945, 
      status: "up",
      location: "Central Library",
      lastUpdate: "1 min ago"
    },
    { 
      id: 3,
      name: "Dormitory CCTV", 
      lat: 20.0435, 
      lng: 99.8952, 
      status: "down",
      location: "Student Housing",
      lastUpdate: "15 min ago"
    },
    { 
      id: 4,
      name: "Parking Lot CCTV", 
      lat: 20.0455, 
      lng: 99.8935, 
      status: "up",
      location: "Parking Area A",
      lastUpdate: "Just now"
    },
    { 
      id: 5,
      name: "Sports Complex CCTV", 
      lat: 20.0438, 
      lng: 99.8920, 
      status: "up",
      location: "Athletic Center",
      lastUpdate: "3 min ago"
    }
  ];
  
  res.json(cctvs);
});

app.get('/api/cctvs/:id', (req, res) => {
  const { id } = req.params;
  // Mock data - replace with actual database query
  res.json({ 
    id: parseInt(id),
    name: "Main Gate CCTV", 
    lat: 20.0450, 
    lng: 99.8925, 
    status: "up",
    location: "Main Entrance",
    lastUpdate: "2 min ago"
  });
});

// Auth endpoints
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  // Mock authentication - replace with actual auth logic
  if (username && password) {
    res.json({ 
      success: true, 
      token: 'mock-jwt-token',
      user: {
        name: "Admin User",
        role: "Security Administrator"
      }
    });
  } else {
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

app.post('/api/auth/logout', (req, res) => {
  res.json({ success: true, message: 'Logged out successfully' });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 Backend server running on http://localhost:${PORT}`);
  console.log(`📡 API endpoints available at http://localhost:${PORT}/api`);
});
