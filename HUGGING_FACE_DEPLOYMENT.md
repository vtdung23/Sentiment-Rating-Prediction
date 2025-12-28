# 🚀 Rating Prediction System - Hugging Face Spaces Deployment

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready FastAPI application for predicting product ratings from Vietnamese comments using PhoBERT. This Space uses Docker SDK for deploying heavy ML models (>500MB) with 16GB RAM.

---

## 🎯 Features

- 🤖 **ML-Powered Predictions**: PhoBERT-based sentiment analysis
- 📊 **Interactive Dashboard**: Real-time visualizations with Chart.js
- 💬 **Batch Processing**: Upload CSV files for bulk predictions
- 🔐 **Secure Authentication**: JWT-based user management
- 📈 **Analytics**: Word clouds and rating distributions
- 🗄️ **External Database**: PostgreSQL support (Render/Neon)

---

## 🔧 Configuration Required

### Required Environment Variables

**CRITICAL:** Before deploying to Hugging Face Spaces, you MUST add these environment variables in the **Settings** tab:

#### 1. DATABASE_URL (REQUIRED)
```
DATABASE_URL=postgresql://username:password@host:port/database
```
**Real External Db url**
```
DATABASE_URL=postgresql://rating_prediction_user:2p3Xv9mKFt3DDFs9OVWDrw8ARHkevTSw@dpg-d4mfq13uibrs738i6jl0-a.singapore-postgres.render.com/rating_prediction
```
**Example from Render:**
```
DATABASE_URL=postgresql://user:pass@dpg-xxxxx.oregon-postgres.render.com/dbname
```

**Example from Neon:**
```
DATABASE_URL=postgresql://user:pass@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

⚠️ **Important Notes:**
- The URL MUST start with `postgresql://` (NOT `postgres://`)
- If your provider gives you `postgres://`, the app will auto-convert it
- Include `?sslmode=require` for secure connections (recommended)

#### 2. SECRET_KEY (REQUIRED)
```
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars
```

**Generate a secure key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Real SECRECT_KEY:**
nz0qzAJoIiRQ3v62SAq8g94JAFtfmf-GSU6dkluKtKA

⚠️ **Security:**
- NEVER commit this key to Git
- Use a cryptographically secure random string
- Minimum 32 characters recommended

---

## 📋 Deployment Steps

### Step 1: Create a New Space
1. Go to https://huggingface.co/new-space
2. Choose **Docker** as the SDK
3. Select **CPU Basic** (16GB RAM - Free)
4. Make the Space **Public** or **Private**

### Step 2: Configure Environment Variables
1. Go to your Space's **Settings** tab
2. Scroll to **Repository Secrets**
3. Add the following secrets:
   - `DATABASE_URL` → Your PostgreSQL connection string
   - `SECRET_KEY` → Your JWT secret key

### Step 3: Push Your Code
```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy your project files
cp -r /path/to/PredictRating/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Step 4: Wait for Build
- Hugging Face will automatically build your Docker image
- Build time: ~5-10 minutes (depending on model size)
- Check build logs in the **Logs** tab

### Step 5: Access Your App
- Your app will be available at: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
- The app runs on port **7860** (handled automatically)

---

## 🗄️ Database Setup

### Option A: Render PostgreSQL (Recommended)
1. Create a free PostgreSQL database on [Render](https://render.com)
2. Go to **Dashboard** → **New** → **PostgreSQL**
3. Copy the **External Database URL**
4. Add it as `DATABASE_URL` in HF Spaces Settings

### Option B: Neon PostgreSQL
1. Create a free database on [Neon](https://neon.tech)
2. Copy the connection string
3. Ensure it includes `?sslmode=require`
4. Add it as `DATABASE_URL` in HF Spaces Settings

### Database Initialization
The app automatically:
- Creates tables on first run
- Supports both SQLite (local dev) and PostgreSQL (production)
- No manual migrations needed

---

## 🐳 Docker Configuration

### Port Requirements
- **CRITICAL:** Hugging Face Spaces requires port **7860**
- The Dockerfile is pre-configured correctly
- DO NOT change the port in `CMD` instruction

### User Permissions
- Hugging Face runs containers as user ID **1000**
- The Dockerfile creates a `user` account
- All files are owned by this user

### Storage
- `/app/static/uploads/` is writable (for word clouds)
- `/app/database/` is writable (for local SQLite fallback)
- Consider using external storage (S3/Cloudinary) for production

---

## 🧪 Testing Locally Before Deployment

### Test with Docker
```bash
# Build the Docker image
docker build -t rating-prediction .

# Run with environment variables
docker run -p 7860:7860 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e SECRET_KEY="your-secret-key" \
  rating-prediction

# Access at http://localhost:7860
```

### Test Database Connection
```bash
# Inside container
docker exec -it <container_id> python -c "
from app.database import engine
print('✅ Database connected:', engine.url)
"
```

---

## 📊 Monitoring & Logs

### View Logs in Hugging Face
1. Go to your Space
2. Click the **Logs** tab
3. Monitor startup and runtime logs

### Expected Startup Messages
```
🚀 Production Mode: Using PostgreSQL
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:7860
```

---

## 🔒 Security Checklist

- ✅ `SECRET_KEY` stored as HF Secret (not in code)
- ✅ `DATABASE_URL` stored as HF Secret (not in code)
- ✅ PostgreSQL uses SSL (`sslmode=require`)
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens expire after 24 hours
- ✅ Docker runs as non-root user

---

## 🐛 Troubleshooting

### Issue: "Application startup failed"
**Solution:** Check logs for database connection errors. Verify `DATABASE_URL` is correct.

### Issue: "502 Bad Gateway"
**Solution:** App may be starting. Wait 2-3 minutes for heavy model loading.

### Issue: "Database connection refused"
**Solution:** Ensure your PostgreSQL database is accessible from external IPs. Check firewall rules.

### Issue: "No module named 'app'"
**Solution:** Ensure all files are copied correctly. Check Dockerfile `WORKDIR` is `/app`.

### Issue: "Port 7860 already in use"
**Solution:** Only relevant for local testing. Stop other containers on that port.

---

## 📚 API Documentation

Once deployed, access:
- **Swagger UI**: `https://your-space.hf.space/docs`
- **ReDoc**: `https://your-space.hf.space/redoc`

### Key Endpoints
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/predict/single` - Predict single comment
- `POST /api/predict/batch` - Upload CSV for batch predictions
- `GET /api/predict/history` - View prediction history

---

## 🆘 Support

If you encounter issues:
1. Check the **Logs** tab in your Space
2. Verify environment variables in **Settings**
3. Test database connection from your local machine
4. Review [FastAPI Docs](https://fastapi.tiangolo.com)
5. Check [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces-overview)

---

## 📄 License

This project is deployed under the terms specified in your Space settings.

---

**Built with ❤️ using FastAPI, PhoBERT, and Hugging Face Spaces**
