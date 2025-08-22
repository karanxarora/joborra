import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api import app
from app.database import get_db, Base
from app.models import Job, Company, VisaKeyword
import tempfile
import os

@pytest.fixture
def test_client():
    """Create test client with temporary database"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    # Override dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Add test data
    db = TestingSessionLocal()
    
    # Add visa keywords
    keywords = [
        VisaKeyword(keyword="visa sponsorship", keyword_type="positive", weight=3.0, category="sponsorship"),
        VisaKeyword(keyword="graduate program", keyword_type="positive", weight=3.0, category="student_friendly"),
    ]
    db.add_all(keywords)
    
    # Add test company and jobs
    company = Company(name="Test Tech Corp", industry="Technology")
    db.add(company)
    db.commit()
    db.refresh(company)
    
    jobs = [
        Job(
            title="Software Engineer",
            description="Python developer with visa sponsorship available",
            company_id=company.id,
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
            title="Graduate Developer",
            description="Entry level position in our graduate program",
            company_id=company.id,
            location="Melbourne, VIC",
            city="Melbourne", 
            state="Victoria",
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
    db.close()
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)

def test_root_endpoint(test_client):
    """Test root health check endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Joborra API is running"
    assert data["status"] == "healthy"

def test_job_search_basic(test_client):
    """Test basic job search"""
    response = test_client.get("/jobs/search")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] == 2
    assert len(data["jobs"]) == 2

def test_job_search_with_filters(test_client):
    """Test job search with filters"""
    # Search by title
    response = test_client.get("/jobs/search?title=Software")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["title"] == "Software Engineer"
    
    # Search by location
    response = test_client.get("/jobs/search?city=Sydney")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["city"] == "Sydney"
    
    # Search by visa sponsorship
    response = test_client.get("/jobs/search?visa_sponsorship=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["visa_sponsorship"] is True

def test_visa_friendly_jobs(test_client):
    """Test visa-friendly jobs endpoint"""
    response = test_client.get("/jobs/visa-friendly")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["visa_sponsorship"] is True

def test_student_friendly_jobs(test_client):
    """Test student-friendly jobs endpoint"""
    response = test_client.get("/jobs/student-friendly")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["jobs"][0]["international_student_friendly"] is True

def test_job_stats(test_client):
    """Test job statistics endpoint"""
    response = test_client.get("/jobs/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "visa_friendly_jobs" in data
    assert "student_friendly_jobs" in data
    assert data["total_jobs"] == 2
    assert data["visa_friendly_jobs"] == 1
    assert data["student_friendly_jobs"] == 1

def test_get_job_by_id(test_client):
    """Test getting specific job by ID"""
    # First get all jobs to find an ID
    response = test_client.get("/jobs/search")
    jobs = response.json()["jobs"]
    job_id = jobs[0]["id"]
    
    # Get specific job
    response = test_client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id

def test_get_nonexistent_job(test_client):
    """Test getting non-existent job"""
    response = test_client.get("/jobs/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_visa_keywords_endpoints(test_client):
    """Test visa keywords endpoints"""
    # Get keywords
    response = test_client.get("/visa-keywords")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # We added 2 test keywords
    
    # Create new keyword
    new_keyword = {
        "keyword": "test keyword",
        "keyword_type": "positive",
        "weight": 2.0,
        "category": "test"
    }
    response = test_client.post("/visa-keywords", json=new_keyword)
    assert response.status_code == 200
    created = response.json()
    assert created["keyword"] == "test keyword"

def test_pagination(test_client):
    """Test pagination in job search"""
    # Test first page
    response = test_client.get("/jobs/search?page=1&per_page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 1
    assert len(data["jobs"]) == 1
    assert data["total_pages"] == 2
    
    # Test second page
    response = test_client.get("/jobs/search?page=2&per_page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["jobs"]) == 1

def test_scraping_endpoints(test_client):
    """Test scraping endpoints (without actual scraping)"""
    # Note: These will fail in actual scraping but should return proper responses
    response = test_client.post("/scraping/start?search_terms=test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "started" in data["message"].lower()
