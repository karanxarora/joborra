# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Joborra is an Australian job scraping platform with AI-powered visa sponsorship detection, designed for international students. It consists of a Python FastAPI backend, React TypeScript frontend, and automated job scraping system.

## Essential Development Commands

### Backend Development
```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows

# Install dependencies
pip install -r requirements.txt

# Setup database (PostgreSQL/SQLite)
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head

# Run API server
python main.py
# Or with uvicorn directly:
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/
pytest tests/test_api.py -v  # Run specific test file
pytest tests/test_api.py::test_job_search_basic -v  # Run single test

# Run job scraper manually
python scheduler.py  # Automated scheduler
python init_data.py  # Initialize test data
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm ci

# Development server
npm start  # Runs on http://localhost:3000

# Build for production
npm run build

# Run tests
npm test

# Build Tailwind CSS
npm run tailwind:dev  # Development mode with watch
npm run tailwind:build  # Production build
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database (careful - deletes all data)
python reset_database.py
```

### Docker Development
```bash
# Build and run all services
docker-compose up --build

# Run only API
docker-compose up api

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
```

## Code Architecture

### Backend Structure (`app/`)
- **api.py**: Main FastAPI router with job search endpoints
- **auth.py** & **auth_models.py**: Authentication system with Google OAuth support
- **models.py**: Core SQLAlchemy models (Job, Company, VisaKeyword, ScrapingLog)
- **services.py**: Business logic layer (JobService with visa analysis)
- **visa_analyzer.py**: AI-powered visa sponsorship detection system
- **database.py**: Database configuration (supports SQLite and PostgreSQL)

### Scraping System (`app/scrapers/`)
- **base_scraper.py**: Abstract base class for all scrapers
- **orchestrator.py**: Coordinates multiple scraping sources
- **adzuna_scraper.py**: Adzuna API integration
- **ats_scraper.py**: Applicant Tracking System scraper (Greenhouse, etc.)

### Frontend Structure (`frontend/src/`)
- **pages/**: Route components (JobSearch, Profile, Dashboard)
- **components/**: Reusable UI components organized by domain
- **contexts/**: React contexts (AuthContext, FavoritesContext, ToastContext)
- **constants/**: Static data (universities, degrees)

### Key Features Architecture

#### Visa Sponsorship Detection
- Uses configurable keyword system in `visa_keywords` table
- Confidence scoring algorithm in `VisaFriendlyAnalyzer`
- Supports positive/negative keywords with weighted scoring
- Company-specific sponsorship history tracking

#### User Authentication
- Role-based system: STUDENT, EMPLOYER, ADMIN
- Google OAuth integration for seamless login
- Session management with device fingerprinting
- Supabase integration for file storage (resumes, logos)

#### Job Scraping Pipeline
1. **orchestrator.py** coordinates multiple scrapers
2. **base_scraper.py** provides common functionality (rate limiting, duplicate detection)
3. **services.py** processes scraped data with visa analysis
4. **scheduler.py** runs automated scraping every 2 days

#### Database Design
- **jobs**: Core job listings with visa analysis results
- **companies**: Company info with accredited sponsor tracking
- **users**: Multi-role users (students/employers) with OAuth
- **visa_keywords**: Configurable keywords for AI analysis
- **job_favorites**, **job_applications**: User interaction tracking

## Environment Configuration

The application supports both SQLite (development) and PostgreSQL (production):
- SQLite: Used when `DATABASE_URL` not set or starts with `sqlite://`
- PostgreSQL: Used for production (Supabase integration)
- Redis: Required for background task processing with Celery

Critical environment variables:
- `DATABASE_URL`: Database connection string
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: OAuth credentials
- `GOOGLE_GENAI_API_KEY`: For AI job description analysis
- `SUPABASE_URL` & `SUPABASE_SERVICE_ROLE`: File storage

## Database Schema Compatibility

The application includes dynamic schema compatibility in `main.py` that:
- Automatically adds missing columns for SQLite and PostgreSQL
- Creates indexes for performance optimization
- Handles schema evolution without breaking existing deployments

## Testing Strategy

- **Backend**: Pytest with SQLite test database isolation
- **Frontend**: Jest/React Testing Library (standard Create React App setup)
- **Integration**: API tests with TestClient and temporary databases
- **Scrapers**: Mocked tests to avoid hitting real job sites

Key test files:
- `tests/test_api.py`: API endpoint testing
- `tests/test_scrapers.py`: Scraper functionality (mocked)
- `tests/test_visa_analyzer.py`: Visa detection algorithm testing

## Development Patterns

### Adding New Job Sources
1. Inherit from `BaseScraper` in `app/scrapers/`
2. Implement `scrape_jobs()` and `parse_job_details()` methods
3. Add to `ALLOWED_SOURCES` in `app/services.py`
4. Update `orchestrator.py` scrapers dictionary

### Extending Visa Analysis
1. Add keywords via API: `POST /visa-keywords`
2. Modify `VisaFriendlyAnalyzer` scoring algorithm
3. Update confidence calculation in `analyze_job()` method

### Frontend Component Development
- Use TypeScript for all new components
- Follow existing patterns: functional components with hooks
- Use Tailwind CSS for styling (configured with `tailwind.config.js`)
- Maintain context providers for global state (Auth, Favorites, Toast)

## Deployment Architecture

Production deployment uses Docker Compose with:
- **API container**: FastAPI backend with PostgreSQL
- **Frontend container**: Built React app served by Nginx
- **Caddy**: Reverse proxy with automatic HTTPS
- **GitHub Actions**: CI/CD pipeline with Linode deployment

The scheduler runs as a separate systemd service (`joborra-scheduler.service`) for automated job scraping.
