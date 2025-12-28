# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Login/     │  │   Dashboard  │  │   Register   │     │
│  │  Register    │  │   (Jinja2)   │  │    Page      │     │
│  │  (Jinja2)    │  │ + TailwindCSS│  │  (Jinja2)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                   JavaScript (Fetch API)                    │
│                     + Chart.js for viz                      │
└────────────────────────────│────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│  ┌───────────────────────────────────────────────────┐     │
│  │                  API ROUTERS                      │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │     │
│  │  │   Auth   │  │Prediction│  │Dashboard │       │     │
│  │  │  Router  │  │  Router  │  │  Router  │       │     │
│  │  │ /api/auth│  │/api/pred │  │  /pages  │       │     │
│  │  └──────────┘  └──────────┘  └──────────┘       │     │
│  └───────────────────────────────────────────────────┘     │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────┐     │
│  │                   SERVICES                        │     │
│  │  ┌──────────────┐  ┌──────────────┐             │     │
│  │  │     Auth     │  │      ML      │             │     │
│  │  │   Service    │  │   Service    │             │     │
│  │  │(JWT, bcrypt) │  │  (Model)     │             │     │
│  │  └──────────────┘  └──────────────┘             │     │
│  │  ┌──────────────────────────────────┐           │     │
│  │  │   Visualization Service          │           │     │
│  │  │  (WordCloud, Charts)             │           │     │
│  │  └──────────────────────────────────┘           │     │
│  └───────────────────────────────────────────────────┘     │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────┐     │
│  │              DATA LAYER                           │     │
│  │  ┌──────────┐         ┌──────────┐               │     │
│  │  │ SQLAlchemy│        │ Pydantic │               │     │
│  │  │  Models   │        │ Schemas  │               │     │
│  │  │(ORM Layer)│        │(Validation)              │     │
│  │  └──────────┘         └──────────┘               │     │
│  └───────────────────────────────────────────────────┘     │
└────────────────────────────│────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE                               │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │    Users Table       │  │ PredictionHistory    │        │
│  │  - id (PK)           │  │  - id (PK)           │        │
│  │  - username          │  │  - user_id (FK)      │        │
│  │  - email             │  │  - product_name      │        │
│  │  - hashed_password   │  │  - comment           │        │
│  │  - created_at        │  │  - predicted_rating  │        │
│  │                      │  │  - confidence_score  │        │
│  │                      │  │  - created_at        │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                SQLite Database                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Request Flow Examples

### 1️⃣ User Login Flow

```
User enters credentials
        │
        ▼
[Login.html]
        │
        ▼
POST /api/auth/login
        │
        ▼
[Auth Router]
        │
        ▼
[Auth Service] ──► Verify password (bcrypt)
        │          Generate JWT token
        ▼
[Database] ──► Query User table
        │
        ▼
Return JWT token to frontend
        │
        ▼
Store token in localStorage
        │
        ▼
Redirect to /dashboard
```

### 2️⃣ Single Prediction Flow

```
User enters comment
        │
        ▼
[Dashboard.html]
        │
        ▼
POST /api/predict/single
(with JWT token in header)
        │
        ▼
[Prediction Router]
        │
        ▼
[Auth Service] ──► Verify JWT token
        │
        ▼
[ML Service] ──► predict_single(comment)
        │         (DUMMY: return random rating)
        ▼
[Database] ──► Save to PredictionHistory
        │
        ▼
Return {rating, confidence}
        │
        ▼
Display result in UI
```

### 3️⃣ Batch CSV Prediction Flow

```
User uploads CSV file
        │
        ▼
[Dashboard.html]
        │
        ▼
POST /api/predict/batch
(multipart/form-data)
        │
        ▼
[Prediction Router]
        │
        ▼
Parse CSV ──► Extract comments
        │
        ▼
[ML Service] ──► predict_batch(comments)
        │         For each comment:
        │         predict_single()
        ▼
[Visualization Service]
        │
        ├──► generate_wordcloud()
        │    Save PNG to /static/uploads/
        │
        └──► calculate_rating_distribution()
             Count 1⭐, 2⭐, 3⭐, 4⭐, 5⭐
        │
        ▼
[Database] ──► Save all predictions
        │
        ▼
Return:
- wordcloud_url
- rating_distribution
- results array
        │
        ▼
[Dashboard.html]
        │
        ├──► Render Chart.js bar chart
        ├──► Display word cloud image
        ├──► Populate results table
        └──► Enable CSV download
```

---

## Technology Stack Details

### Backend
```
FastAPI (0.104.1)
├── Auto-generates Swagger UI (/docs)
├── Automatic data validation (Pydantic)
├── Async support
└── Built-in dependency injection

SQLAlchemy (2.0.23)
├── ORM for database operations
├── Models: User, PredictionHistory
└── Automatic table creation

JWT Authentication
├── python-jose for token generation
├── passlib[bcrypt] for password hashing
└── OAuth2PasswordBearer for token validation
```

### Frontend
```
Jinja2 Templates
├── Server-side rendering
├── Template inheritance (base.html)
└── Context variables from backend

TailwindCSS (CDN)
├── Utility-first CSS framework
├── Responsive design
└── Custom animations

Chart.js (CDN)
├── Interactive bar charts
└── Rating distribution visualization

JavaScript (Vanilla)
├── Fetch API for HTTP requests
├── LocalStorage for JWT token
└── Dynamic DOM manipulation
```

### Visualization
```
WordCloud (1.9.3)
├── Generate word cloud images
├── Vietnamese stopwords support
└── Save to PNG files

Matplotlib (3.8.2)
├── Render word cloud to image
└── Non-GUI backend (Agg)
```

---

## File Responsibilities

### Backend Files
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, router inclusion |
| `config.py` | Configuration (SECRET_KEY, products list) |
| `database.py` | SQLAlchemy engine, session management |
| `models.py` | Database table definitions (User, PredictionHistory) |
| `schemas.py` | Pydantic models for request/response validation |

### Router Files
| File | Purpose |
|------|---------|
| `routers/auth.py` | Register, login, get current user |
| `routers/prediction.py` | Single/batch prediction, history |
| `routers/dashboard.py` | Serve HTML pages (login, register, dashboard) |

### Service Files
| File | Purpose |
|------|---------|
| `services/auth_service.py` | JWT generation, password hashing, token validation |
| `services/ml_service.py` | ML model wrapper, prediction logic (DUMMY) |
| `services/visualization_service.py` | WordCloud generation, chart data |

### Frontend Files
| File | Purpose |
|------|---------|
| `templates/base.html` | Base layout with navigation, CDN imports |
| `templates/login.html` | Login form with JWT handling |
| `templates/register.html` | Registration form |
| `templates/dashboard.html` | Main interface (product select, predictions, viz) |

---

## Security Features

1. **Password Hashing:** bcrypt with salt
2. **JWT Tokens:** Signed with SECRET_KEY (HS256)
3. **Token Expiration:** 24 hours
4. **Protected Routes:** Dependency injection (`get_current_user`)
5. **CORS:** Configured for security
6. **Input Validation:** Pydantic schemas

---

## Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PredictionHistory Table
CREATE TABLE prediction_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    comment TEXT NOT NULL,
    predicted_rating INTEGER NOT NULL,
    confidence_score FLOAT,
    prediction_type VARCHAR(20) DEFAULT 'single',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API Response Examples

### POST /api/auth/login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /api/predict/single
```json
{
  "predicted_rating": 5,
  "confidence_score": 0.92,
  "comment": "Sản phẩm rất tốt..."
}
```

### POST /api/predict/batch
```json
{
  "total_predictions": 20,
  "rating_distribution": {
    "1": 2,
    "2": 3,
    "3": 5,
    "4": 6,
    "5": 4
  },
  "wordcloud_url": "/static/uploads/wordclouds/wordcloud_20241125_143022.png",
  "results": [
    {
      "Comment": "Sản phẩm tốt",
      "Predicted_Rating": 5,
      "Confidence": 0.95
    }
  ],
  "csv_download_url": "/api/predict/download/1/1700924622.123"
}
```

---

## Deployment Checklist

Before production:
- [ ] Change `SECRET_KEY` in config.py
- [ ] Set `reload=False` in uvicorn
- [ ] Configure CORS properly
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add environment variables (.env file)
- [ ] Set up HTTPS
- [ ] Add rate limiting
- [ ] Configure logging
- [ ] Add error monitoring
- [ ] Set up backup strategy

---

This architecture provides:
✅ **Separation of Concerns**
✅ **Scalability** (easy to add features)
✅ **Maintainability** (clear file structure)
✅ **Security** (JWT, password hashing)
✅ **Documentation** (auto-generated Swagger)
✅ **Testing** (clear API endpoints)
