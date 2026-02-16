# Tech Polarity — Headless Tech News CMS Backend

**Tech Polarity** is a production-grade, headless CMS backend for a modern tech news platform.  
It powers dynamic domains (AI, Gaming, Software, etc.), trending analytics, admin-managed articles, and frontend-friendly APIs.

The backend is built with **FastAPI**, **MongoDB**, **JWT authentication**, **rate limiting**, and is **Dockerized for cloud deployment**.

---

## ✨ Features

### 📰 Content Management
- Dynamic article domains (fully editable by admin)
- Create, update, delete, list articles
- Draft / Published lifecycle
- Trending articles by domain
- Home page aggregations (main article, related, trending)

### 🛠️ Admin Capabilities
- JWT-secured admin APIs
- Rate-limited write operations
- Admin article listing with filters & pagination
- Admin analytics (article counts by status)

### 📬 Contact System
- Contact form API
- MongoDB persistence
- Email notifications via **HTTP Email API** (no SMTP / Gmail)

### ⚙️ Platform & Ops
- MongoDB Atlas integration
- Async I/O with Motor
- Dockerized deployment
- Environment-based configuration
- Swagger enabled in dev / staging only
- Health check endpoint

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Database | MongoDB (Atlas) |
| Auth | JWT (python-jose) |
| Rate Limiting | SlowAPI |
| Email | Resend API (HTTP-based) |
| Containerization | Docker |
| Runtime | Python 3.12 |
| Hosting | Render |

---

## 📁 Project Structure

```text
app/
├── api/
│   └── v1/
│       ├── articles_public.py
│       ├── articles_admin.py
│       ├── auth.py
│       ├── contact.py
│       ├── home.py
│       ├── navigation.py
│       └── health.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── rate_limit.py
│
├── db/
│   └── mongo.py
│
├── models/
├── schemas/
├── services/
├── utils/
│
├── main.py
│
Dockerfile
requirements.txt

```

---

## 🔐 Authentication

Admin APIs are protected using JWT Bearer tokens.

### Login
```http
POST /api/v1/auth/login
```

```json
{
  "email": "fontdrip007@gmail.com",
  "password": "********"
}
```

**Response**
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Use the token in headers:
```text
Authorization: Bearer <JWT>
```

---

## 📊 Admin Analytics

Admin dashboard stats are generated using MongoDB aggregation:

$$\text{Article Stats} = \sum{count(status)}$$

**Endpoint**
```http
GET /api/v1/articles/admin/stats
```
---

## 🚑 Health Check

Used for deployment readiness and monitoring.

```http
GET /health
```

**Response**
```json
{
  "status": "ok",
  "database": "connected"
}
```

## 🐳 Docker Setup

**BUild Image**
```bash
docker build -t tech-polarity-api .

```

**Run Container**
```bash
docker run -p 8000:8000 --env-file .env tech-polarity-api

```

---

## 🌍 Environment Variables

```env
ENVIRONMENT=production

MONGO_URI=mongodb+srv://...
MONGO_DB_NAME=tech_polarity

SECRET_KEY=super-secret-key

ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=strong-password

RESEND_API_KEY=re_xxxxxxxxx
CONTACT_TO_EMAIL=fontdrip007@gmail.com

```

---

## 📘 API Documentation

- **Development / Staging**
```bash
/docs
```

- **OpenAPI Spec**
```bash
/openapi.json
```

Swagger is disabled in production for security.


---


## 🚀 Deployment

- Dockerized backend
- Deployed on Render
- MongoDB Atlas as managed database
- Environment-based configuration
- Stateless & horizontally scalable


---


## 🧠 Design Principles

Separation of concerns (API / Services / Schemas)

- Headless CMS architecture
- Contract-first API design (OpenAPI)
- Secure by default
- Production-ready error handling
- Async-first I/O

---

## 📌 Status

- **Version**: v1
- **State**: Production-ready

---

## Author 

| Shvendu Kumar | Machine Learning Engineer | 

---

## 📄 License

MIT License