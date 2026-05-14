# Testimony Project - Production Deployment Guide

## Project Structure
```
testimony_project/
├── backend/              → FastAPI REST API
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── frontend/             → React + Vite SPA
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.production
│   └── ...
└── render.yaml           → Deployment configuration
```

## Deployment Architecture

### Backend Service
- **Service Name:** `testimony-backend-api`
- **Runtime:** Python 3.11
- **Framework:** FastAPI + Uvicorn
- **URL:** `https://testimony-backend-api.onrender.com`
- **Root Directory:** `testimony_project/backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Service
- **Service Type:** Static Site
- **Service Name:** `testimony-frontend`
- **Framework:** React 19 + Vite
- **URL:** `https://testimony-frontend.onrender.com`
- **Build Command:** `cd testimony_project/frontend && npm install && npm run build`
- **Publish Directory:** `testimony_project/frontend/dist`
- **Routing:** Client-side (SPA) via `_redirects`

## STEP-BY-STEP DEPLOYMENT

### 1. Configure Backend Environment Variables

On Render Dashboard → testimony-backend-api → Environment:

```
SUPABASE_URL=https://fjkxitbfkhgrdcsyepsw.supabase.co
SUPABASE_SERVICE_KEY=<your-key>
OPENAI_API_KEY=<your-key>
GEMINI_API_KEY=<your-key>
```

**DO NOT put secrets in render.yaml file!**

### 2. Configure Frontend Environment Variables

On Render Dashboard → testimony-frontend → Environment Variables:
```
VITE_API_URL=https://testimony-backend-api.onrender.com
```

### 3. Deploy Backend First

Push changes to GitHub:
```bash
git add .
git commit -m "Deploy: Configure backend for production"
git push origin main
```

Render will auto-deploy the backend web service.

### 4. Deploy Frontend

After backend is live, the frontend will auto-deploy and automatically connect to the backend via the environment variable.

### 5. Verify Deployment

**Backend Health Check:**
```
https://testimony-backend-api.onrender.com/health
```

**Frontend Access:**
```
https://testimony-frontend.onrender.com
```

## Key Configuration Files

### frontend/.env.production
```
VITE_API_URL=https://testimony-backend-api.onrender.com
VITE_APP_NAME=Testimony Project
```

### frontend/.env.local (Development)
```
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=Testimony Project (Local Dev)
```

### backend/main.py (CORS)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://testimony-frontend.onrender.com",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### render.yaml
```yaml
services:
  - type: web
    name: testimony-backend-api
    runtime: python
    pythonVersion: 3.11
    rootDir: testimony_project/backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    
  - type: static_site
    name: testimony-frontend
    buildCommand: cd testimony_project/frontend && npm install && npm run build
    staticPublishPath: testimony_project/frontend/dist
```

## Local Development

### Backend
```bash
cd testimony_project/backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000
```

### Frontend
```bash
cd testimony_project/frontend
npm install
npm run dev
# Runs on http://localhost:5173
# Connects to http://localhost:8000 (backend)
```

## Production API Calls

The frontend automatically uses the correct API URL based on environment:

```javascript
// In frontend code:
import.meta.env.VITE_API_URL  // Automatically set by .env.production

// Example:
const API_BASE = import.meta.env.VITE_API_URL;
const response = await fetch(`${API_BASE}/upload_and_assess`);
```

## Common Issues & Solutions

### Frontend Shows "Cannot Connect to API"
- ✅ Verify backend URL in `.env.production`
- ✅ Check CORS settings in `backend/main.py`
- ✅ Ensure backend service is running (`/health` endpoint)

### Frontend Routes Return 404
- ✅ Verify `_redirects` file exists in `frontend/public/`
- ✅ Verify `render.json` is in `frontend/public/`
- ✅ Check `vite.config.js` build configuration

### Backend Service Crashes
- ✅ Check environment variables are set on Render
- ✅ Check logs: Dashboard → Service → Logs
- ✅ Verify `requirements.txt` has all dependencies

## Production Checklist

- [ ] All API keys set in Render dashboard (not in render.yaml)
- [ ] Backend `/health` endpoint responds successfully
- [ ] Frontend `.env.production` has correct backend URL
- [ ] `_redirects` file in `frontend/public/`
- [ ] CORS configured to accept frontend domain
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Both services deployed and running
- [ ] API calls work from frontend to backend
- [ ] Client-side routing works (refresh pages don't 404)

## Useful Render Commands

### View Logs
```bash
# Backend logs
curl https://api.render.com/v1/services/<SERVICE_ID>/logs

# Frontend logs
curl https://api.render.com/v1/services/<SERVICE_ID>/logs
```

### Manual Redeploy
On Render Dashboard → Service → Manual Deploy → Latest Commit

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│        User's Browser                       │
│  https://testimony-frontend.onrender.com    │
└────────────────────┬────────────────────────┘
                     │
                     │ API Calls
                     │
┌────────────────────▼────────────────────────┐
│   React SPA (Vite)                          │
│   - Client-side routing                     │
│   - Dynamic UI                              │
│   - Axios HTTP client                       │
└────────────────────┬────────────────────────┘
                     │
                     │ CORS-enabled HTTP
                     │
┌────────────────────▼────────────────────────┐
│   FastAPI Backend                           │
│   https://testimony-backend-api.onrender.com│
│   - REST API endpoints                      │
│   - Database integration (Supabase)         │
│   - AI/ML processing                        │
└─────────────────────────────────────────────┘
```

---

**Last Updated:** May 14, 2026
**Status:** Production Ready ✅
