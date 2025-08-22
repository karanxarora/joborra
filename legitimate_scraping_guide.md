# Legitimate Job Scraping with ATS APIs - Implementation Guide

## Overview

This implementation replaces web scraping with legitimate ATS APIs and official job sources, following your requirements for compliance, stability, and visa-friendly targeting.

## Key Components Implemented

### 1. ATS API Scrapers (`app/scrapers/ats_scraper.py`)
- **Greenhouse Job Board API**: Public JSON endpoints for company job boards
- **Lever Postings API**: Simple JSON API for startup/scaleup jobs  
- **Workable Jobs API**: Public and authenticated endpoints
- **SmartRecruiters Jobs API**: Enterprise job postings

### 2. Aggregator Integration (`app/scrapers/adzuna_scraper.py`)
- **Adzuna Jobs API**: Legitimate aggregator with Australia country filter
- Visa-friendly keyword searches
- Salary and metadata extraction

### 3. Visa Keyword Analysis (`app/visa_keywords.py`)
- **Positive keywords**: International students, visa sponsorship, graduate programs
- **Negative keywords**: Citizenship requirements, security clearance
- Confidence scoring (0-1) based on keyword matches

### 4. Accredited Sponsor Integration (`app/accredited_sponsors.py`)
- Department of Home Affairs sponsor list integration
- Company name normalization and fuzzy matching
- Sponsor status prioritization

### 5. Orchestrated Scraping (`app/scrapers/orchestrator.py`)
- Coordinates all ATS sources
- Duplicate prevention
- Enhanced visa analysis
- Sponsor status checking

## Configuration

### Environment Variables
```bash
# Adzuna API (required)
export ADZUNA_APP_ID="your_app_id"
export ADZUNA_APP_KEY="your_app_key"

# Workable API (optional, for authenticated access)
export WORKABLE_API_TOKEN="your_token"
```

### Target Companies (`config/ats_config.py`)
```python
TARGET_COMPANIES = {
    'greenhouse': ['atlassian', 'canva', 'shopify', 'stripe'],
    'lever': ['netflix', 'uber', 'spotify', 'github'],
    'workable': ['company-subdomain'],
    'smartrecruiters': ['company-id']
}
```

## Usage Examples

### Basic Scraping
```python
from app.scrapers import run_full_scraping_cycle

# Run complete scraping cycle
results = run_full_scraping_cycle(location="Australia")
print(f"Total jobs: {results['total_jobs']}")
print(f"Visa-friendly: {results['visa_friendly_jobs']}")
```

### Individual ATS Scraping
```python
from app.scrapers import GreenhouseScraper, AdzunaScraper

# Greenhouse scraping
greenhouse = GreenhouseScraper()
jobs = greenhouse.get_company_jobs('atlassian')

# Adzuna visa-friendly search
adzuna = AdzunaScraper(app_id, app_key)
visa_jobs = adzuna.search_visa_friendly_jobs()
```

### Sponsor Status Checking
```python
from app.accredited_sponsors import check_company_sponsor_status

status = check_company_sponsor_status("Atlassian")
print(f"Accredited sponsor: {status['is_accredited_sponsor']}")
```

## Database Updates

### New Company Fields
- `is_accredited_sponsor`: Boolean flag for sponsor status
- `sponsor_confidence`: Confidence score (0-1) for sponsor matching
- `ats_type`: Which ATS the company uses
- `ats_company_id`: Company identifier in ATS

### Migration
```bash
# Run the migration to add new fields
alembic upgrade head
```

## Compliance Features

### ✅ Legal & Ethical
- Uses official APIs with proper terms of service
- No web scraping that violates ToS
- Respects rate limits and robots.txt

### ✅ Stable & Reliable  
- JSON APIs instead of fragile HTML parsing
- Proper error handling and retries
- Structured data extraction

### ✅ Visa-Friendly Targeting
- Comprehensive keyword analysis
- Accredited sponsor prioritization
- International student indicators

## API Sources Implemented

### Primary ATS Sources
1. **Greenhouse** - `boards-api.greenhouse.io/v1/boards/{company}/jobs`
2. **Lever** - `api.lever.co/v0/postings/{company}`
3. **Workable** - `{company}.workable.com/api/v1/published`
4. **SmartRecruiters** - `api.smartrecruiters.com/v1/companies/{id}/postings`

### Aggregator
- **Adzuna** - `api.adzuna.com/v1/api/jobs/au/search`

## Next Steps

### 1. API Access Setup
- Register for Adzuna API credentials
- Apply for SEEK Developer API partnership
- Contact Workable for API access if needed

### 2. Company Discovery
- Research which ATS each target company uses
- Build comprehensive target company lists
- Implement ATS detection for career pages

### 3. Sponsor Data
- Download latest accredited sponsor list from Home Affairs
- Set up automated sponsor list updates
- Implement sponsor matching improvements

### 4. Monitoring
- Set up scraping schedules
- Monitor API rate limits
- Track job quality metrics

## Benefits Over Web Scraping

- **Legal compliance**: No ToS violations
- **Stability**: APIs don't break with UI changes  
- **Rich data**: Structured metadata and salary info
- **Performance**: Faster than browser automation
- **Scalability**: Can handle high volumes efficiently
- **Visa targeting**: Built-in sponsor prioritization
