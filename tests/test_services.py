import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Job, Company, VisaKeyword
from app.services import JobService, ScrapingService
from app.schemas import JobFilter
import tempfile
import os

@pytest.fixture
def test_db_with_data():
    """Create test database with sample data"""
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Add visa keywords
    keywords = [
        VisaKeyword(keyword="visa sponsorship", keyword_type="positive", weight=3.0, category="sponsorship"),
        VisaKeyword(keyword="graduate program", keyword_type="positive", weight=3.0, category="student_friendly"),
        VisaKeyword(keyword="citizens only", keyword_type="negative", weight=-3.0, category="sponsorship"),
    ]
    db.add_all(keywords)
    
    # Add test companies
    companies = [
        Company(name="Tech Corp", industry="Technology", location="Sydney"),
        Company(name="Finance Corp", industry="Finance", location="Melbourne"),
    ]
    db.add_all(companies)
    db.commit()
    
    # Add test jobs
    jobs = [
        Job(
            title="Software Engineer",
            description="Python developer position with visa sponsorship",
            company_id=1,
            location="Sydney, NSW",
            city="Sydney",
            state="New South Wales",
            salary_min=80000,
            salary_max=120000,
            employment_type="full-time",
            experience_level="mid",
            visa_sponsorship=True,
            visa_sponsorship_confidence=0.8,
            international_student_friendly=False,
            source_website="test.com",
            source_url="https://test.com/job/1",
            source_job_id="1"
        ),
        Job(
            title="Graduate Analyst",
            description="Entry level graduate program position",
            company_id=2,
            location="Melbourne, VIC",
            city="Melbourne",
            state="Victoria",
            salary_min=60000,
            salary_max=80000,
            employment_type="full-time",
            experience_level="entry",
            visa_sponsorship=False,
            visa_sponsorship_confidence=0.2,
            international_student_friendly=True,
            source_website="test.com",
            source_url="https://test.com/job/2",
            source_job_id="2"
        )
    ]
    db.add_all(jobs)
    db.commit()
    
    yield db
    
    db.close()
    os.close(db_fd)
    os.unlink(db_path)

def test_job_service_create_company(test_db_with_data):
    """Test JobService company creation"""
    service = JobService(test_db_with_data)
    
    # Create new company
    company = service.create_or_get_company("New Tech Corp", industry="Technology")
    assert company.name == "New Tech Corp"
    assert company.industry == "Technology"
    
    # Get existing company
    existing = service.create_or_get_company("Tech Corp")
    assert existing.name == "Tech Corp"
    assert existing.id == 1  # Should be the first company we created

def test_job_service_process_scraped_job(test_db_with_data):
    """Test processing scraped job data"""
    service = JobService(test_db_with_data)
    
    job_data = {
        'title': 'Data Scientist',
        'company_name': 'AI Corp',
        'description': 'We offer visa sponsorship for qualified candidates',
        'location': 'Brisbane, QLD',
        'city': 'Brisbane',
        'state': 'Queensland',
        'salary_min': 90000,
        'salary_max': 130000,
        'employment_type': 'full-time',
        'experience_level': 'mid',
        'source_website': 'newsite.com',
        'source_url': 'https://newsite.com/job/123',
        'source_job_id': '123'
    }
    
    job = service.process_scraped_job(job_data)
    assert job is not None
    assert job.title == 'Data Scientist'
    assert job.visa_sponsorship is True  # Should be detected from description
    assert job.visa_sponsorship_confidence > 0.5

def test_job_service_duplicate_prevention(test_db_with_data):
    """Test duplicate job prevention"""
    service = JobService(test_db_with_data)
    
    # Try to add duplicate job (same source_url)
    job_data = {
        'title': 'Duplicate Job',
        'company_name': 'Test Corp',
        'description': 'Test description',
        'source_website': 'test.com',
        'source_url': 'https://test.com/job/1',  # Same as existing job
        'source_job_id': '1'
    }
    
    job = service.process_scraped_job(job_data)
    assert job is not None
    assert job.title == "Software Engineer"  # Should return existing job

def test_job_service_search_jobs(test_db_with_data):
    """Test job search functionality"""
    service = JobService(test_db_with_data)
    
    # Basic search
    filters = JobFilter()
    result = service.search_jobs(filters)
    assert result.total == 2
    assert len(result.jobs) == 2
    
    # Search by title
    filters = JobFilter(title="Software")
    result = service.search_jobs(filters)
    assert result.total == 1
    assert result.jobs[0].title == "Software Engineer"
    
    # Search by location
    filters = JobFilter(city="Sydney")
    result = service.search_jobs(filters)
    assert result.total == 1
    assert result.jobs[0].city == "Sydney"
    
    # Search by visa sponsorship
    filters = JobFilter(visa_sponsorship=True)
    result = service.search_jobs(filters)
    assert result.total == 1
    assert result.jobs[0].visa_sponsorship is True
    
    # Search by student friendly
    filters = JobFilter(international_student_friendly=True)
    result = service.search_jobs(filters)
    assert result.total == 1
    assert result.jobs[0].international_student_friendly is True

def test_job_service_search_pagination(test_db_with_data):
    """Test job search pagination"""
    service = JobService(test_db_with_data)
    
    # First page
    filters = JobFilter()
    result = service.search_jobs(filters, page=1, per_page=1)
    assert result.total == 2
    assert len(result.jobs) == 1
    assert result.page == 1
    assert result.total_pages == 2
    
    # Second page
    result = service.search_jobs(filters, page=2, per_page=1)
    assert len(result.jobs) == 1
    assert result.page == 2

def test_job_service_get_stats(test_db_with_data):
    """Test job statistics"""
    service = JobService(test_db_with_data)
    
    stats = service.get_job_stats()
    assert stats['total_jobs'] == 2
    assert stats['visa_friendly_jobs'] == 1
    assert stats['student_friendly_jobs'] == 1
    assert stats['visa_friendly_percentage'] == 50.0
    assert stats['student_friendly_percentage'] == 50.0
    assert 'jobs_by_state' in stats
    assert 'jobs_by_source' in stats

@pytest.mark.skip(reason="Scraping removed from app")
def test_scraping_service_initialization(test_db_with_data):
    """Test scraping service initialization"""
    service = ScrapingService(test_db_with_data)
    assert service.job_service is not None

@pytest.mark.skip(reason="Scraping removed from app")
def test_scraping_service_cleanup(test_db_with_data):
    """Test old job cleanup"""
    service = ScrapingService(test_db_with_data)
    # This test is skipped; logic retained for reference
    deleted_count = service.cleanup_old_jobs(days=1)
    assert deleted_count == 0
    remaining_jobs = test_db_with_data.query(Job).count()
    assert remaining_jobs == 2
