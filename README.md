# StreamBldr

AI Stream Scene Builder - A web-based design platform for creating professional streaming layouts.

## Features

- **AI-Powered Generation**: Create scenes from natural language prompts
- **Drag-and-Drop Editor**: Intuitive visual editor with 1920x1080 canvas
- **Template Library**: Pre-built scene packs and individual templates
- **Theme System**: Customizable colors, fonts, and styling
- **Export**: PNG images and OBS Studio-compatible JSON

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Backend**: FastAPI + SQLModel + PostgreSQL
- **AI**: OpenAI GPT-4 integration

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. Start Infrastructure

```bash
docker-compose up -d
```

This starts PostgreSQL and Redis.

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
python -c "from app.db.database import init_db; init_db()"

# Start server
uvicorn app.main:app --reload --port 8000
```

### 3. Setup Frontend

```bash
cd frontend
npm install

# Copy environment file
cp .env.example .env

# Start dev server
npm run dev
```

### 4. Open App

Navigate to `http://localhost:3000`

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
streambldr/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Security, config
│   │   ├── db/       # Database
│   │   ├── models/   # SQLModel models
│   │   └── main.py   # App entry point
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   └── utils/
│   └── package.json
├── docs/             # PRD, specs, wireframes
└── docker-compose.yml
```

## Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/streambldr` |
| `SECRET_KEY` | JWT signing key | - |
| `OPENAI_API_KEY` | For AI generation (optional) | - |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## Scripts

### Backend

```bash
# Run dev server
uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations
alembic revision --autogenerate -m "message"
alembic upgrade head
```

### Frontend

```bash
# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview
```

## License

MIT
