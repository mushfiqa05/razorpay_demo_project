# Razorpay AI Revenue Recovery Control Tower (Hackathon MVP)

An AI-driven, guardrail-bounded revenue recovery control tower for Razorpay merchants to continuously map revenue-at-risk, diagnose root causes, prioritize recovery opportunities by expected value, execute permitted interventions, and maintain complete audit trails.

---

## Architecture Overview

```
React Frontend (Vite)
       ↓  HTTP JSON APIs (CORS Enabled)
FastAPI Backend
       ↓  Python Business Logic & Rule Engine
PostgreSQL / SQLite Database (SQLAlchemy ORM)
```

---

## Project Structure

```
Razorpay Buildathon/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point & routes
│   │   ├── config.py           # Application settings & environment vars
│   │   ├── database.py         # DB connection & session handling
│   │   ├── models.py           # Database tables/entities (SQLAlchemy)
│   │   ├── schemas.py          # Request/Response data shapes (Pydantic)
│   │   └── services/           # Business logic & scoring engine
│   ├── tests/
│   │   └── test_health.py      # Automated Pytest suite
│   ├── requirements.txt        # Backend dependencies
│   └── pytest.ini              # Pytest configuration
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── src/
│   │   ├── App.jsx             # React dashboard entry component
│   │   ├── main.jsx            # React DOM mounting
│   │   └── index.css           # Modern Razorpay dark fintech design system
│   └── vite.config.js
└── README.md
```

---

## How to Run Phase 1

### 1. Run Backend (FastAPI)

Navigate to the `backend` directory and run:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend server will launch at:
- **API URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Healthcheck**: `http://localhost:8000/api/health`

### 2. Run Backend Tests (Pytest)

```bash
cd backend
pytest
```

### 3. Run Frontend (React + Vite)

In a separate terminal window:

```bash
cd frontend
npm install
npm run dev
```

The frontend application will launch at: `http://localhost:5173`
