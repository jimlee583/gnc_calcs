# GNC Calculations

Professional-grade Guidance, Navigation, and Control (GNC) calculations for spacecraft engineering.

## Overview

This application provides modular, well-documented engineering calculations for spacecraft GNC systems. It is designed as an "aerospace engineer's digital scratchpad" — clean, modern, and built for real engineering work.

### Features

- **Attitude Dynamics**: Euler's equations for rigid-body rotational motion
- **Orbital Motion**: Two-body Keplerian orbital mechanics
- **Relative Motion**: Clohessy-Wiltshire equations for proximity operations

Each calculation includes:
- Clear input/output documentation with units
- Documented equations and assumptions
- TODO markers for physics fidelity improvements

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- Pydantic for validation
- NumPy for calculations

### Frontend
- React 18 + TypeScript
- Vite
- CSS Modules

### Infrastructure
- Docker + Docker Compose
- Single container for production

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Local Development with Docker

```bash
# Start all services
docker-compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

### Local Development without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Production Build

```bash
# Build the production image
docker build -t gnc-calcs .

# Run the container
docker run -p 8000:8000 gnc-calcs
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/gnc/attitude` | POST | Rigid-body attitude dynamics |
| `/api/gnc/orbit` | POST | Two-body orbital mechanics |
| `/api/gnc/relative` | POST | Clohessy-Wiltshire relative motion |
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |

## Project Structure

```
gnc_calcs/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── routers/
│   │   │   └── gnc.py        # GNC API routes
│   │   ├── services/
│   │   │   └── gnc/
│   │   │       ├── attitude_dynamics.py
│   │   │       ├── orbital_dynamics.py
│   │   │       └── relative_motion.py
│   │   ├── schemas/
│   │   │   └── gnc.py        # Pydantic models
│   │   └── core/
│   │       └── config.py     # App configuration
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── cards/        # Calculation card components
│   │   ├── pages/
│   │   │   └── Dashboard.tsx
│   │   ├── api/
│   │   │   └── gnc.ts        # API client
│   │   └── theme/
│   │       └── theme.ts
│   └── package.json
├── Dockerfile                 # Production multi-stage build
├── docker-compose.yml         # Local development
└── README.md
```

## Design Philosophy

The visual style is intentionally different from dark "space UI" themes:

- Light, muted technical palette (off-white, slate, muted blue)
- Card-based layout with generous spacing
- Subtle engineering-paper grid background
- Monospace fonts for numerical values
- Clean, professional aesthetic

## Future Enhancements

See TODO comments throughout the codebase for planned improvements:

- Quaternion attitude representation
- J2 perturbation corrections
- Eccentric orbit support (Yamanaka-Ankersen)
- Trajectory visualization
- Additional GNC modules (state estimation, control design)

## License

MIT
