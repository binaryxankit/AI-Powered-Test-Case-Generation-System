# AI-Powered Test Case Generation System

> A modern, full-stack MVP that converts natural-language requirements into structured, professional software test cases using Google Gemini.

[![Stack](https://img.shields.io/badge/Frontend-Next.js%2015-black)]()
[![Stack](https://img.shields.io/badge/Backend-FastAPI-009688)]()
[![Stack](https://img.shields.io/badge/Database-PostgreSQL-336791)]()
[![Stack](https://img.shields.io/badge/AI-Gemini-4285F4)]()

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Database (PostgreSQL)](#1-database-postgresql)
  - [2. Backend (FastAPI)](#2-backend-fastapi)
  - [3. Frontend (Next.js)](#3-frontend-nextjs)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

QA engineers, developers, and product managers often need to translate plain-English requirements into a complete set of structured test cases. This MVP removes the busywork: type the requirement, and the system returns **3–5 professionally written test cases** with steps, expected results, priority levels, and edge cases — all in seconds.

## Features

- **Home Page** — Modern SaaS-style landing page with hero, features, and "How it works" sections.
- **Test Case Generator** — Single-textarea interface with loading spinner and error handling.
- **AI-Powered Generation** — Uses Google's Gemini model via a strict JSON-only system prompt.
- **Structured Results** — Each test case is rendered in a professional card with priority badges, numbered steps, expected result, and edge case list.
- **History** — Every generation is persisted to PostgreSQL; users can browse and re-open previous generations.
- **PDF Export** — One-click "Download Report" produces a polished, print-ready PDF.
- **Dark Mode** — Fully supported, including Tailwind's `class` strategy.
- **Responsive UI** — Mobile, tablet, and desktop layouts using Shadcn UI primitives.
- **Empty States & Errors** — Friendly empty states for History and graceful error boundaries.

## Tech Stack

| Layer       | Technology                                            |
|-------------|-------------------------------------------------------|
| Frontend    | Next.js 15 (App Router), TypeScript, Tailwind CSS, Shadcn UI |
| Backend     | FastAPI, Python 3.11+, Uvicorn                         |
| Database    | PostgreSQL 14+ (SQLAlchemy 2.x ORM)                   |
| AI          | Google Gemini API (`google-genai` SDK)                |
| PDF         | ReportLab                                             |

## Project Structure

```
.
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # FastAPI endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py           # Engine, SessionLocal, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   └── test_generation.py   # SQLAlchemy ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── test_case.py         # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py    # Gemini integration
│   │   ├── pdf_service.py       # ReportLab PDF generator
│   │   └── test_case_service.py # Orchestration / persistence
│   ├── .env.example
│   ├── main.py                  # FastAPI app entry
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Home
│   │   ├── globals.css
│   │   ├── generate/
│   │   │   └── page.tsx         # Generator
│   │   ├── results/
│   │   │   └── page.tsx         # Results view
│   │   └── history/
│   │       ├── page.tsx
│   │       └── [id]/page.tsx
│   ├── components/
│   │   ├── ui/                  # Shadcn UI primitives
│   │   ├── theme-provider.tsx
│   │   ├── site-header.tsx
│   │   ├── site-footer.tsx
│   │   ├── hero-section.tsx
│   │   ├── features-section.tsx
│   │   ├── how-it-works-section.tsx
│   │   ├── test-case-card.tsx
│   │   └── empty-state.tsx
│   ├── lib/
│   │   ├── utils.ts
│   │   └── types.ts
│   ├── services/
│   │   └── api.ts               # Frontend API client
│   ├── .env.example
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── docs/
│   └── screenshots/             # Reference images
├── .gitignore
└── README.md
```

## Prerequisites

- **Node.js** ≥ 18.18
- **npm** ≥ 9
- **Python** ≥ 3.11
- **PostgreSQL** ≥ 14
- **Google Gemini API key** — [Get one free](https://aistudio.google.com/app/apikey)

## Setup Instructions

### 1. Database (PostgreSQL)

Create a local database and user:

```sql
CREATE DATABASE testcase_ai;
CREATE USER testcase_user WITH PASSWORD 'testcase_pass';
GRANT ALL PRIVILEGES ON DATABASE testcase_ai TO testcase_user;
```

### 2. Backend (FastAPI)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy environment template and fill in your values:

```powershell
Copy-Item .env.example .env
```

`.env` contents (example):

```
DATABASE_URL=postgresql+psycopg2://testcase_user:testcase_pass@localhost:5432/testcase_ai
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
CORS_ORIGINS=http://localhost:3000
```

Start the API:

```powershell
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at `/docs`.

### 3. Frontend (Next.js)

```powershell
cd frontend
npm install
```

Copy environment template:

```powershell
Copy-Item .env.example .env.local
```

`.env.local` contents:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Start the dev server:

```powershell
npm run dev
```

Open **http://localhost:3000**.

## Running the Application

You need **two terminals** — one for the backend, one for the frontend.

| Terminal | Command                       | URL                   |
|----------|-------------------------------|-----------------------|
| Backend  | `uvicorn main:app --reload`   | http://localhost:8000 |
| Frontend | `npm run dev`                 | http://localhost:3000 |

## API Endpoints

| Method | Endpoint              | Description                              |
|--------|-----------------------|------------------------------------------|
| POST   | `/api/generate`       | Generate test cases from a requirement   |
| GET    | `/api/history`        | List all past generations                |
| GET    | `/api/history/{id}`   | Retrieve one generation                  |
| GET    | `/api/history/{id}/pdf` | Download PDF report for a generation    |
| GET    | `/api/health`         | Health check                             |

### Example: `POST /api/generate`

Request:

```json
{ "requirement": "Verify login functionality and dashboard access" }
```

Response:

```json
{
  "id": 1,
  "requirement": "Verify login functionality and dashboard access",
  "test_cases": [
    {
      "test_case_id": "TC001",
      "title": "Verify successful login with valid credentials",
      "priority": "High",
      "steps": ["Open login page", "Enter valid username", "Enter valid password", "Click Login"],
      "expected_result": "User is redirected to the dashboard.",
      "edge_cases": ["Empty username", "Empty password", "Invalid credentials"]
    }
  ],
  "created_at": "2026-06-03T10:21:33.000Z"
}
```

## Environment Variables

### Backend (`backend/.env`)

| Variable          | Description                                         |
|-------------------|-----------------------------------------------------|
| `DATABASE_URL`    | SQLAlchemy-compatible PostgreSQL URL               |
| `GEMINI_API_KEY`  | Google Gemini API key                               |
| `GEMINI_MODEL`    | Gemini model name (default `gemini-1.5-flash`)     |
| `CORS_ORIGINS`    | Comma-separated allowed origins                     |

### Frontend (`frontend/.env.local`)

| Variable                  | Description                       |
|---------------------------|-----------------------------------|
| `NEXT_PUBLIC_API_BASE_URL`| Base URL of the FastAPI backend   |

## Screenshots

Place reference screenshots in `docs/screenshots/`. They are not generated by the application but are useful for documentation and submissions.

## Roadmap

- [ ] Authentication (per-user history)
- [ ] Export to CSV / XLSX
- [ ] Inline editing of generated test cases
- [ ] Test suite grouping and tagging
- [ ] CI/CD integration helpers (Jira export, TestRail import)

## License

MIT
