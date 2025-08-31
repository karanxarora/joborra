# Joborra - Australian Job Scraping API

A scalable backend service that scrapes genuine job sources in Australia, filters visa-friendly positions for international students, and stores them in a relational database.

## Features

- **Multi-source scraping**: Scrapes jobs from Seek.com.au and Indeed Australia
- **Visa-friendly detection**: AI-powered analysis to identify jobs likely to sponsor visas
- **Student-friendly filtering**: Identifies positions suitable for international students
- **Scalable architecture**: Built with FastAPI, PostgreSQL, and background task processing
- **RESTful API**: Complete API for job search, filtering, and management
- **Duplicate detection**: Prevents duplicate job entries
- **Automated cleanup**: Removes old job listings automatically

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: SQLite with SQLAlchemy ORM (production-optimized with WAL mode)
- **File Storage**: Local filesystem storage with organized directory structure
- **Scraping**: Selenium, BeautifulSoup4, Requests
- **Task Queue**: Celery with Redis (for background scraping)
- **Migration**: Alembic
- **Testing**: Pytest

## Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to project
cd /home/karan/startup/joborra

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Create .env file from example (optional for SQLite)
cp .env.example .env

# SQLite database will be created automatically at ./joborra.db
# No additional database setup required

# Run migrations (optional, schema is created automatically)
alembic upgrade head
```

### 3. Run the API

```bash
# Start the server
python main.py

# Or with uvicorn directly
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Job Search & Filtering

- `GET /jobs/search` - Search jobs with comprehensive filters
- `GET /jobs/{job_id}` - Get specific job details
- `GET /jobs/visa-friendly` - Get visa sponsorship jobs
- `GET /jobs/student-friendly` - Get student-friendly positions
- `GET /jobs/stats` - Get job statistics

### Scraping Management

- `POST /scraping/start` - Start background scraping
- `POST /scraping/run-sync` - Run scraping synchronously
- `POST /scraping/cleanup` - Clean up old jobs

### Visa Keywords Management

- `GET /visa-keywords` - Get visa detection keywords
- `POST /visa-keywords` - Add new visa keywords

## Usage Examples

### Search Jobs
```bash
# Basic search
curl "http://localhost:8000/jobs/search?title=software%20engineer&location=Sydney"

# Visa-friendly jobs
curl "http://localhost:8000/jobs/search?visa_sponsorship=true&experience_level=entry"

# Student-friendly positions
curl "http://localhost:8000/jobs/search?international_student_friendly=true&employment_type=full-time"
```

### Start Scraping
```bash
# Scrape jobs for specific terms
curl -X POST "http://localhost:8000/scraping/start?search_terms=software%20engineer&search_terms=data%20analyst&location=Australia"
```

## Key Features Explained

### Visa-Friendly Detection
The system analyzes job descriptions for:
- Explicit visa sponsorship mentions
- Company history of sponsoring visas
- Keywords indicating openness to international candidates
- Confidence scoring (0-1) for sponsorship likelihood

### Student-Friendly Analysis
Identifies jobs suitable for international students by detecting:
- Graduate programs and entry-level positions
- Companies with structured training programs
- Positions requiring minimal experience
- Internship and trainee opportunities

### Duplicate Prevention
- Uses source URL as unique identifier
- Prevents duplicate entries from multiple scraping runs
- Maintains data integrity across sources

## Database Schema

### Core Tables
- **companies**: Company information and visa sponsorship history
- **jobs**: Job listings with visa analysis results
- **visa_keywords**: Configurable keywords for visa detection
- **scraping_logs**: Audit trail of scraping activities

## Configuration

### Environment Variables
- `DATABASE_URL`: SQLite connection string (defaults to sqlite:///./joborra.db)
- `LOCAL_STORAGE_PATH`: Local file storage directory (defaults to ./data)
- `REDIS_URL`: Redis connection for background tasks
- `SCRAPER_DELAY`: Delay between requests (seconds)
- `MAX_CONCURRENT_SCRAPERS`: Maximum concurrent scraping processes

### Visa Keywords
The system uses configurable keywords to detect visa-friendly jobs:
- **Positive indicators**: "visa sponsorship", "482 visa", "international candidates"
- **Negative indicators**: "citizens only", "PR holders only"
- **Student-friendly**: "graduate program", "entry level", "internship"

## Scaling Considerations

- **Database indexing**: Key fields are indexed for fast queries
- **Background processing**: Scraping runs asynchronously
- **Rate limiting**: Built-in delays prevent site blocking
- **Error handling**: Comprehensive error logging and recovery
- **Data cleanup**: Automated removal of old listings

## Development

### Adding New Job Sources
1. Create new scraper class inheriting from `BaseScraper`
2. Implement `scrape_jobs()` and `parse_job_details()` methods
3. Add to `ScrapingService.scrapers` dictionary
4. Test with small dataset first

### Extending Visa Analysis
1. Add new keywords via API or database
2. Modify `VisaFriendlyAnalyzer` for custom logic
3. Update confidence scoring algorithm
4. Test with known visa-friendly companies

## Monitoring & Maintenance

- Monitor scraping logs for errors
- Regular cleanup of old job listings
- Update visa keywords based on market trends
- Monitor API performance and database growth

## Future Enhancements

- LinkedIn Jobs scraper
- Machine learning for better visa prediction
- Company rating system
- Email alerts for new visa-friendly jobs
- Advanced analytics dashboard
