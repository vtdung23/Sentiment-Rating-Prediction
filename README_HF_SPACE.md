---
title: Product Rating Prediction System
emoji: ⭐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# ⭐ Product Rating Prediction System

A production-ready AI-powered system for predicting product ratings from Vietnamese customer comments using PhoBERT.

## 🎯 Features

- 🤖 **Deep Learning Model**: PhoBERT-based sentiment analysis
- 💬 **Single & Batch Predictions**: Process one comment or thousands via CSV
- 📊 **Visual Analytics**: Word clouds and rating distribution charts
- 🔐 **Secure Authentication**: JWT-based user management
- 🌐 **Full-Stack Web App**: FastAPI backend + Jinja2 frontend
- 🗄️ **External Database**: PostgreSQL support for scalability

## 🚀 Quick Start

### For Users
1. Click the link above to access the live application
2. Register a new account
3. Upload a CSV file with comments or enter a single comment
4. View predictions, visualizations, and download results

### For Developers
This Space requires environment variables to connect to an external PostgreSQL database. See [HUGGING_FACE_DEPLOYMENT.md](HUGGING_FACE_DEPLOYMENT.md) for setup instructions.

## 📚 API Documentation

Once the app is running, access:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 🔧 Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Uvicorn
- **ML/NLP**: PyTorch, Transformers, PhoBERT
- **Frontend**: Jinja2, TailwindCSS, Chart.js
- **Database**: PostgreSQL (external)
- **Security**: JWT, bcrypt

## 📖 Documentation

- [Deployment Guide](HUGGING_FACE_DEPLOYMENT.md)
- [Environment Variables](HF_ENV_VARIABLES.md)
- [Architecture](ARCHITECTURE.md)

## 🐳 Docker

This Space uses the Docker SDK to support heavy ML models (>500MB). The container runs on port 7860 as required by Hugging Face Spaces.

## 🔒 Privacy & Security

- All passwords are hashed with bcrypt
- JWT tokens for secure authentication
- External PostgreSQL database with SSL
- No data stored in the container (stateless)

## 📊 Model Information

- **Base Model**: PhoBERT (Vietnamese BERT)
- **Task**: Sentiment Analysis → Rating Prediction (1-5 stars)
- **Language**: Vietnamese
- **Model Size**: ~500MB

## 🆘 Support

For issues or questions:
1. Check the logs tab above
2. Review [HUGGING_FACE_DEPLOYMENT.md](HUGGING_FACE_DEPLOYMENT.md)
3. Open an issue in the repository

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using FastAPI, PhoBERT, and Hugging Face Spaces**
