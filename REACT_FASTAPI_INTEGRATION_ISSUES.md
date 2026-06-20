# React-FastAPI Integration Issues & Fixes

## Project Overview

**Project:** HybridGuard - Security Incident Dashboard  
**Frontend:** React + Vite (`priviguard-dashboard/`)  
**Backend:** FastAPI (`backend/api.py`)  
**Database:** SQLite (`hybridguard.db`)

---

## Problem Analysis

### Current Integration Status
The React frontend was **not successfully connecting** to the FastAPI backend due to several integration issues identified during code review.

### Root Causes Identified

#### 1. **Hardcoded API URL in Frontend**
- **File:** `priviguard-dashboard/src/SecurityIncidentDashboard.jsx` (line 60)
- **Issue:** The fetch URL is hardcoded to `http://localhost:8000/`, which is not configurable and will break in production or when backend runs on a different port.
- **Impact:** Connection failures if backend port or host changes.

#### 2. **CORS Configuration May Be Insufficient**
- **File:** `backend/api.py` (lines 8-13)
- **Issue:** CORS is configured for specific origins (`localhost:5173`, `127.0.0.1:5173`, `5174` variants) but does not include `allow_credentials=True` or handle preflight requests robustly.
- **Impact:** Requests from React dev server may be blocked in certain browser/network configurations.

#### 3. **Backend Does Not Handle CORS Preflight (OPTIONS) Requests**
- **File:** `backend/api.py`
- **Issue:** No explicit OPTIONS route handler. While CORSMiddleware generally handles this, explicit handling is more reliable.
- **Impact:** Preflight failures can block POST/PUT requests.

#### 4. **Frontend Run Configuration Not Documented**
- **File:** `priviguard-dashboard/package.json`
- **Issue:** The Vite dev server runs on port 5173 by default, but there is no `server.proxy` configuration to proxy API requests during development.
- **Impact:** Developers must manually run both frontend and backend and ensure CORS is configured correctly.

#### 5. **No Environment Variable Configuration**
- Both frontend and backend lack `.env` files for configuration.
- **Impact:** Hardcoded values make deployment and environment switching error-prone.

---

## Changes Documented

### Backend Changes (`backend/api.py`)

| Change # | Description | Status |
|----------|-------------|--------|
| 1 | Added environment variable support for API host/port | Recommended |
| 2 | Enabled `allow_credentials=True` in CORS middleware | Recommended |
| 3 | Added `allow_origin_regex` for flexible origin matching | Recommended |
| 4 | Added explicit OPTIONS route handler | Recommended |

### Frontend Changes (`priviguard-dashboard/src/SecurityIncidentDashboard.jsx`)

| Change # | Description | Status |
|----------|-------------|--------|
| 1 | Replace hardcoded `http://localhost:8000/` with environment variable `VITE_API_URL` | Recommended |
| 2 | Add error boundary for failed API calls | Recommended |
| 3 | Add loading state while fetching incidents | Recommended |

### Configuration Changes

| File | Change | Status |
|------|--------|--------|
| `priviguard-dashboard/.env` | Create with `VITE_API_URL=http://localhost:8000` | Recommended |
| `priviguard-dashboard/.env.example` | Template for environment variables | Recommended |
| `backend/.env` | Create with `API_HOST=0.0.0.0`, `API_PORT=8000` | Recommended |
| `priviguard-dashboard/vite.config.js` | Add proxy configuration for development | Recommended |

---

## Recommended Fixes

### Fix 1: Update Backend CORS Configuration
```python
# backend/api.py
import os

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000)

myapp = FastAPI()

myapp.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Fix 2: Update Frontend to Use Environment Variables
```javascript
// priviguard-dashboard/src/SecurityIncidentDashboard.jsx
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

useEffect(() => {
  fetch(`${API_URL}/`)
    .then(res => res.json())
    .then(data => {
      // ... existing logic
    })
    .catch(err => console.error("Failed to fetch incidents:", err));
}, []);
```

### Fix 3: Add Vite Proxy Configuration (Alternative to CORS)
```javascript
// priviguard-dashboard/vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### Fix 4: Create Environment Files
Create `priviguard-dashboard/.env`:
```
VITE_API_URL=http://localhost:8000
```

Create `priviguard-dashboard/.env.example`:
```
# Backend API URL
VITE_API_URL=http://localhost:8000
```

---

## Testing Checklist

- [ ] Start FastAPI backend: `cd backend && python api.py` or `uvicorn api:myapp --reload`
- [ ] Start React dev server: `cd priviguard-dashboard && npm run dev`
- [ ] Verify browser console shows no CORS errors
- [ ] Verify incidents load from backend API
- [ ] Test filtering, searching, and status cycling
- [ ] Verify network tab shows successful API calls to correct URL

---

## Notes

- The backend `generate_security_incidents()` function must be importable from the backend directory (ensure Python path is set correctly when running `uvicorn`).
- SQLite database `hybridguard.db` must exist and be accessible from the backend directory.
- The current frontend code has mock data commented out (lines 24-37) which can be used for offline testing if API connection fails.

---

## Commands to Run

```bash
# Terminal 1 - Start Backend
cd backend
uvicorn api:myapp --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start Frontend
cd priviguard-dashboard
npm run dev
```

---

*Document created: 2026-06-20*  
*Project: HybridGuard Security Incident Dashboard*