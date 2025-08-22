import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import VisaKeyword
from app.visa_analyzer import VisaFriendlyAnalyzer
import tempfile
import os

@pytest.fixture
def test_db_with_keywords():
    """Create test database with visa keywords"""
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Add test keywords
    keywords = [
        VisaKeyword(keyword="visa sponsorship", keyword_type="positive", weight=3.0, category="sponsorship"),
        VisaKeyword(keyword="sponsor visa", keyword_type="positive", weight=3.0, category="sponsorship"),
        VisaKeyword(keyword="citizens only", keyword_type="negative", weight=-3.0, category="sponsorship"),
        VisaKeyword(keyword="graduate program", keyword_type="positive", weight=3.0, category="student_friendly"),
        VisaKeyword(keyword="entry level", keyword_type="positive", weight=2.0, category="student_friendly"),
        VisaKeyword(keyword="0-2 years", keyword_type="positive", weight=2.0, category="experience"),
    ]
    
    db.add_all(keywords)
    db.commit()
    
    yield db
    
    db.close()
    os.close(db_fd)
    os.unlink(db_path)

def test_visa_analyzer_initialization(test_db_with_keywords):
    """Test visa analyzer initialization"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    assert analyzer.visa_keywords is not None
    assert len(analyzer.visa_keywords['sponsorship_positive']) > 0

def test_visa_sponsorship_detection_positive(test_db_with_keywords):
    """Test positive visa sponsorship detection"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    job_data = {
        'title': 'Software Engineer',
        'description': 'We offer visa sponsorship for the right candidate. Join our team!',
        'company_name': 'Tech Corp'
    }
    
    visa_sponsorship, confidence, student_friendly = analyzer.analyze_job(job_data)
    
    assert visa_sponsorship is True
    assert confidence > 0.5
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1

def test_visa_sponsorship_detection_negative(test_db_with_keywords):
    """Test negative visa sponsorship detection"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    job_data = {
        'title': 'Software Engineer',
        'description': 'Australian citizens only. Security clearance required.',
        'company_name': 'Government Corp'
    }
    
    visa_sponsorship, confidence, student_friendly = analyzer.analyze_job(job_data)
    
    assert visa_sponsorship is False
    assert confidence < 0.5

def test_student_friendly_detection(test_db_with_keywords):
    """Test student-friendly job detection"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    job_data = {
        'title': 'Graduate Software Engineer',
        'description': 'Entry level position in our graduate program. Perfect for recent graduates.',
        'company_name': 'Student Corp'
    }
    
    visa_sponsorship, confidence, student_friendly = analyzer.analyze_job(job_data)
    
    assert student_friendly is True

def test_skills_extraction(test_db_with_keywords):
    """Test skills extraction from job description"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    job_data = {
        'title': 'Python Developer',
        'description': 'Looking for Python developer with React, SQL, and AWS experience. Docker knowledge preferred.',
        'company_name': 'Tech Corp'
    }
    
    required_skills, preferred_skills = analyzer.extract_skills(job_data)
    
    assert isinstance(required_skills, list)
    assert isinstance(preferred_skills, list)
    # Should find some of the mentioned skills
    all_skills = required_skills + preferred_skills
    assert any('python' in skill for skill in all_skills)

def test_company_size_heuristic(test_db_with_keywords):
    """Test company size heuristic for student-friendliness"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    # Test with large company
    job_data = {
        'title': 'Software Engineer',
        'description': 'Join our team',
        'company_name': 'Commonwealth Bank'
    }
    
    result = analyzer._check_company_size_friendly(job_data)
    assert result is True
    
    # Test with unknown company
    job_data['company_name'] = 'Unknown Small Corp'
    result = analyzer._check_company_size_friendly(job_data)
    assert result is False

def test_job_level_heuristic(test_db_with_keywords):
    """Test job level heuristic for student-friendliness"""
    analyzer = VisaFriendlyAnalyzer(test_db_with_keywords)
    
    # Test entry level job
    job_data = {
        'title': 'Junior Software Engineer',
        'description': 'Entry level position'
    }
    
    result = analyzer._check_job_level_friendly(job_data)
    assert result is True
    
    # Test senior level job
    job_data['title'] = 'Senior Software Architect'
    result = analyzer._check_job_level_friendly(job_data)
    assert result is False
