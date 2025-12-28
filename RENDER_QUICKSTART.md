# 🚀 QUICK DEPLOYMENT GUIDE

## ✅ Files Changed (Production-Ready)

1. ✅ **requirements.txt** - Added `psycopg2-binary`, `gunicorn`
2. ✅ **app/database.py** - Hybrid SQLite/PostgreSQL support with Render URL fix
3. ✅ **app/config.py** - Environment variable support for `SECRET_KEY`
4. ✅ **main.py** - Auto-migration, production settings

## 📋 Render Configuration

### Web Service Settings

```
Name: vietnamese-rating-prediction
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Environment Variables (Required)

```
SECRET_KEY = <generate-with-openssl-rand-hex-32>
PYTHON_VERSION = 3.11.0
```

### PostgreSQL Database

```
Name: vietnamese-rating-db
PostgreSQL Version: 15
Instance Type: Free
```

**Link database to web service** - `DATABASE_URL` will be auto-populated.

---

## 🎯 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render"
git push origin master
```

### 2. Create Render Web Service
- Go to https://dashboard.render.com/
- New → Web Service
- Connect GitHub repo
- Use settings above

### 3. Create PostgreSQL Database
- New → PostgreSQL
- Use free tier
- Link to web service

### 4. Deploy
- Click "Manual Deploy"
- Watch logs for success

### 5. Test
```
https://your-app.onrender.com/health
https://your-app.onrender.com/docs
https://your-app.onrender.com/dashboard
```

---

## 🔧 Local Testing Before Deploy

Test hybrid database locally:

```bash
# Test with SQLite (no DATABASE_URL)
python main.py

# Test with PostgreSQL (set DATABASE_URL)
export DATABASE_URL=postgresql://user:pass@localhost/dbname
python main.py
```

Expected output:
```
🔧 Development Mode: Using SQLite
# OR
🚀 Production Mode: Using PostgreSQL
🔄 Creating database tables...
✅ Database tables created successfully!
```

---

## ⚠️ Important Notes

1. **Render Free Tier Limitations:**
   - App sleeps after 15 minutes of inactivity (first request takes 30-60s)
   - 512MB RAM (may need optimization for ML model)
   - 1GB PostgreSQL storage

2. **ML Model Optimization:**
   - Consider lazy loading (load on first request)
   - Use CPU-optimized PyTorch
   - Cache predictions if possible

3. **Static Files:**
   - Uploads are ephemeral on Render Free Tier
   - WordClouds will be deleted on container restart
   - Use cloud storage (S3, Cloudinary) for production

4. **Database:**
   - SQLite NOT recommended for production (file locking issues)
   - PostgreSQL required for concurrent requests
   - Free tier: 1GB storage, 97 connections

---

## 🆘 Common Issues

### "Module not found"
→ Run `pip install -r requirements.txt` locally first

### "Port binding error"
→ Use `$PORT` in start command (auto-set by Render)

### "Database connection failed"
→ Check `DATABASE_URL` in environment variables

### "Model loading timeout"
→ Free tier has 512MB RAM limit, optimize model or upgrade

---

**Read DEPLOYMENT.md for detailed guide!**
