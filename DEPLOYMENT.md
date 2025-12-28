# 🚀 Deployment Guide for Render.com

## Pre-Deployment Checklist

- [x] Updated `requirements.txt` with `psycopg2-binary` and `gunicorn`
- [x] Modified `database.py` for hybrid SQLite/PostgreSQL support
- [x] Updated `config.py` to read `SECRET_KEY` from environment
- [x] Auto-migration enabled in `main.py`
- [ ] Push code to GitHub repository
- [ ] Create Render account

---

## 📦 Step 1: Prepare Your Repository

1. **Commit all changes:**
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin master
```

2. **Ensure these files exist:**
- ✅ `requirements.txt` (with psycopg2-binary, gunicorn)
- ✅ `main.py` (with Base.metadata.create_all)
- ✅ `app/database.py` (hybrid support)
- ✅ `app/config.py` (environment variables)

---

## 🌐 Step 2: Deploy on Render

### A. Create New Web Service

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository: `Predict-Rating-Web-App`

### B. Configure Web Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `vietnamese-rating-prediction` (or your choice) |
| **Region** | Singapore / Oregon (closest to you) |
| **Branch** | `master` |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT` |
| **Instance Type** | `Free` |

### C. Add Environment Variables

Click **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | `your-super-secret-random-key-here-2024` | Generate with: `openssl rand -hex 32` |
| `PYTHON_VERSION` | `3.11.0` | Specify Python version |

**DO NOT set `DATABASE_URL` manually** - Render will auto-create it when you add PostgreSQL.

---

## 🗄️ Step 3: Add PostgreSQL Database

### A. Create Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `vietnamese-rating-db`
   - **Database:** `rating_prediction`
   - **User:** (auto-generated)
   - **Region:** Same as web service
   - **PostgreSQL Version:** `15`
   - **Instance Type:** `Free`

3. Click **"Create Database"**

### B. Link Database to Web Service

1. Go back to your **Web Service**
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Select **"Add from Database"**
5. Choose your `vietnamese-rating-db`
6. It will auto-populate `DATABASE_URL`

### C. Verify Connection

The `database.py` will automatically:
- Detect `DATABASE_URL` environment variable
- Replace `postgres://` with `postgresql://`
- Connect to PostgreSQL
- Create all tables automatically

---

## 🎯 Step 4: Deploy & Monitor

### A. Trigger Deployment

1. After adding database, click **"Manual Deploy"** → **"Deploy latest commit"**
2. Watch the build logs:
   - ✅ Installing dependencies
   - ✅ Creating database tables
   - ✅ Starting Gunicorn server

### B. Check Deployment Logs

Look for these success messages:
```
🚀 Running in PRODUCTION mode
🔄 Creating database tables...
✅ Database tables created successfully!
[INFO] Starting gunicorn
[INFO] Booting worker with pid: 123
```

### C. Access Your Application

Your app will be available at:
```
https://vietnamese-rating-prediction.onrender.com
```

**Important endpoints:**
- **Dashboard:** `https://your-app.onrender.com/dashboard`
- **API Docs (Swagger):** `https://your-app.onrender.com/docs`
- **Health Check:** `https://your-app.onrender.com/health`

---

## 🔍 Troubleshooting

### Issue 1: "Module not found" errors
**Solution:** Ensure all imports are in `requirements.txt`
```bash
pip freeze > requirements.txt
```

### Issue 2: "Connection refused" to database
**Solution:** 
- Verify `DATABASE_URL` is set in environment variables
- Check database status in Render dashboard
- Restart web service

### Issue 3: "Port binding" errors
**Solution:** Use `$PORT` environment variable:
```bash
gunicorn main:app --bind 0.0.0.0:$PORT
```

### Issue 4: ML model takes too long to load
**Solution:** Render Free Tier has limited RAM (512MB). Consider:
- Using a lighter model
- Lazy loading (load model on first request)
- Upgrading to Starter plan ($7/month)

### Issue 5: Static files not loading
**Solution:** Ensure `app/static/` directory exists and is committed to git

---

## ⚙️ Alternative Start Commands

### Option 1: Basic Uvicorn (Single Worker)
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Option 2: Gunicorn with Uvicorn Workers (Recommended)
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Option 3: Gunicorn with Auto-scaling Workers
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

---

## 📊 Performance Optimization

### 1. Reduce Model Loading Time
Edit `app/services/ml_service.py`:
```python
# Lazy load model on first request instead of on startup
class MLPredictionService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
    
    def _ensure_loaded(self):
        if self.model is None:
            # Load model here
            pass
```

### 2. Enable Connection Pooling
Already configured in `database.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 3. Use Caching for Predictions
Consider adding Redis (Render add-on) for caching frequent predictions.

---

## 🔒 Security Checklist

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Restrict CORS origins in production (edit `main.py`)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up database backups (Render PostgreSQL backups)
- [ ] Add rate limiting (consider using Render's DDoS protection)
- [ ] Review and sanitize all user inputs

---

## 💰 Cost Breakdown (Free Tier)

| Service | Cost | Limitations |
|---------|------|-------------|
| Web Service | FREE | 512MB RAM, Sleeps after 15min inactivity |
| PostgreSQL | FREE | 1GB storage, 97 connections |
| Bandwidth | FREE | 100GB/month |

**Upgrade Considerations:**
- If app sleeps: Upgrade to Starter ($7/month, always-on)
- If RAM issues: Upgrade to Standard ($25/month, 2GB RAM)
- If storage full: Upgrade database ($7/month, 10GB)

---

## 🎓 Post-Deployment Testing

### Test 1: Health Check
```bash
curl https://your-app.onrender.com/health
```
Expected: `{"status":"healthy","service":"rating-prediction","version":"1.0.0"}`

### Test 2: Swagger UI
Visit: `https://your-app.onrender.com/docs`
- Try registering a user
- Login to get JWT token
- Test prediction endpoints

### Test 3: Database Connection
Check logs for:
```
🚀 Production Mode: Using PostgreSQL
✅ Database tables created successfully!
```

---

## 📚 Additional Resources

- **Render Docs:** https://render.com/docs/deploy-fastapi
- **PostgreSQL Guide:** https://render.com/docs/databases
- **Environment Variables:** https://render.com/docs/environment-variables
- **Custom Domains:** https://render.com/docs/custom-domains

---

## 🆘 Support

If you encounter issues:
1. Check Render logs (Dashboard → Logs tab)
2. Review this guide carefully
3. Check Render community forum: https://community.render.com/
4. Contact Render support (for paid plans)

---

**Good luck with your deployment! 🚀**
