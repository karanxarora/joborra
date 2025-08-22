import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import Job, Company, VisaKeyword
import tempfile
import os

@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

def test_create_company(test_db):
    """Test company creation"""
    company = Company(
        name="Test Company",
        website="https://test.com",
        size="medium",
        industry="Technology",
        location="Sydney, NSW"
    )
    test_db.add(company)
    test_db.commit()
    
    retrieved = test_db.query(Company).filter(Company.name == "Test Company").first()
    assert retrieved is not None
    assert retrieved.name == "Test Company"
    assert retrieved.website == "https://test.com"

def test_create_job(test_db):
    """Test job creation with company relationship"""
    # Create company first
    company = Company(name="Tech Corp", industry="Technology")
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    
    # Create job
    job = Job(
        title="Software Engineer",
        description="Python developer position",
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
        international_student_friendly=True,
        source_website="test.com",
        source_url="https://test.com/job/123",
        source_job_id="123"
    )
    test_db.add(job)
    test_db.commit()
    
    retrieved = test_db.query(Job).filter(Job.title == "Software Engineer").first()
    assert retrieved is not None
    assert retrieved.company_id == company.id
    assert retrieved.visa_sponsorship is True
    assert retrieved.visa_sponsorship_confidence == 0.8

def test_create_visa_keyword(test_db):
    """Test visa keyword creation"""
    keyword = VisaKeyword(
        keyword="visa sponsorship",
        keyword_type="positive",
        weight=3.0,
        category="sponsorship"
    )
    test_db.add(keyword)
    test_db.commit()
    
    retrieved = test_db.query(VisaKeyword).filter(VisaKeyword.keyword == "visa sponsorship").first()
    assert retrieved is not None
    assert retrieved.weight == 3.0
    assert retrieved.category == "sponsorship"

def test_job_company_relationship(test_db):
    """Test job-company relationship"""
    company = Company(name="Relationship Test Corp")
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    
    job1 = Job(
        title="Job 1",
        company_id=company.id,
        source_website="test.com",
        source_url="https://test.com/job/1"
    )
    job2 = Job(
        title="Job 2", 
        company_id=company.id,
        source_website="test.com",
        source_url="https://test.com/job/2"
    )
    
    test_db.add_all([job1, job2])
    test_db.commit()
    
    # Test relationship
    company_with_jobs = test_db.query(Company).filter(Company.id == company.id).first()
    assert len(company_with_jobs.jobs) == 2
    
    job_with_company = test_db.query(Job).filter(Job.title == "Job 1").first()
    assert job_with_company.company.name == "Relationship Test Corp"
