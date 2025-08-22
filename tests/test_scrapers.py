import pytest
from unittest.mock import Mock, patch
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.seek_scraper import SeekScraper
from app.scrapers.indeed_scraper import IndeedScraper

class TestBaseScraper:
    """Test base scraper functionality"""
    
    def test_extract_salary_range(self):
        """Test salary extraction from text"""
        from app.scrapers.seek_scraper import SeekScraper
        scraper = SeekScraper()
        
        # Test range format
        min_sal, max_sal = scraper.extract_salary("$80,000 - $120,000")
        assert min_sal == 80000
        assert max_sal == 120000
        
        # Test 'to' format
        min_sal, max_sal = scraper.extract_salary("80000 to 120000 AUD")
        assert min_sal == 80000
        assert max_sal == 120000
        
        # Test single value
        min_sal, max_sal = scraper.extract_salary("$100,000")
        assert min_sal == 100000
        assert max_sal == 100000
        
        # Test invalid format
        min_sal, max_sal = scraper.extract_salary("Competitive salary")
        assert min_sal is None
        assert max_sal is None
    
    def test_normalize_location(self):
        """Test location normalization"""
        from app.scrapers.seek_scraper import SeekScraper
        scraper = SeekScraper()
        
        # Test with state abbreviation
        city, state = scraper.normalize_location("Sydney, NSW")
        assert city == "Sydney"
        assert state == "New South Wales"
        
        # Test with full state name
        city, state = scraper.normalize_location("Melbourne, Victoria")
        assert city == "Melbourne"
        assert state == "Victoria"
        
        # Test city only
        city, state = scraper.normalize_location("Brisbane")
        assert city == "Brisbane"
        assert state is None
        
        # Test empty location
        city, state = scraper.normalize_location("")
        assert city is None
        assert state is None

class TestSeekScraper:
    """Test Seek scraper functionality"""
    
    def test_initialization(self):
        """Test Seek scraper initialization"""
        scraper = SeekScraper()
        assert scraper.base_url == "https://www.seek.com.au"
        assert scraper.delay == 3
    
    def test_extract_employment_type(self):
        """Test employment type extraction"""
        scraper = SeekScraper()
        
        # Test internship
        emp_type = scraper._extract_employment_type("Software Intern", "Internship program")
        assert emp_type == "internship"
        
        # Test contract
        emp_type = scraper._extract_employment_type("Contract Developer", "6 month contract")
        assert emp_type == "contract"
        
        # Test part-time
        emp_type = scraper._extract_employment_type("Part-time Analyst", "20 hours per week")
        assert emp_type == "part-time"
        
        # Test full-time (default)
        emp_type = scraper._extract_employment_type("Software Engineer", "Join our team")
        assert emp_type == "full-time"
    
    def test_extract_experience_level(self):
        """Test experience level extraction"""
        scraper = SeekScraper()
        
        # Test senior
        level = scraper._extract_experience_level("Senior Developer", "Lead our team")
        assert level == "senior"
        
        # Test entry
        level = scraper._extract_experience_level("Junior Developer", "Graduate position")
        assert level == "entry"
        
        # Test mid (default)
        level = scraper._extract_experience_level("Software Engineer", "Join our team")
        assert level == "mid"

class TestIndeedScraper:
    """Test Indeed scraper functionality"""
    
    def test_initialization(self):
        """Test Indeed scraper initialization"""
        scraper = IndeedScraper()
        assert scraper.base_url == "https://au.indeed.com"
        assert scraper.delay == 3
    
    def test_extract_employment_type(self):
        """Test employment type extraction"""
        scraper = IndeedScraper()
        
        # Test internship
        emp_type = scraper._extract_employment_type("Marketing Intern", "Summer internship")
        assert emp_type == "internship"
        
        # Test contract
        emp_type = scraper._extract_employment_type("Freelance Writer", "Contract position")
        assert emp_type == "contract"
        
        # Test part-time
        emp_type = scraper._extract_employment_type("Part-time Sales", "Casual hours")
        assert emp_type == "part-time"
        
        # Test full-time (default)
        emp_type = scraper._extract_employment_type("Data Analyst", "Permanent role")
        assert emp_type == "full-time"
    
    def test_extract_experience_level(self):
        """Test experience level extraction"""
        scraper = IndeedScraper()
        
        # Test senior
        level = scraper._extract_experience_level("Principal Engineer", "Architecture role")
        assert level == "senior"
        
        # Test entry
        level = scraper._extract_experience_level("Graduate Trainee", "Entry level")
        assert level == "entry"
        
        # Test mid (default)
        level = scraper._extract_experience_level("Business Analyst", "Join our team")
        assert level == "mid"

# Mock tests for actual scraping (to avoid hitting real websites)
class TestScrapingIntegration:
    """Test scraping integration without hitting real websites"""
    
    @patch('app.scrapers.base_scraper.BaseScraper.get_selenium_driver')
    def test_seek_scraper_mock(self, mock_driver):
        """Test Seek scraper with mocked driver"""
        # Mock the selenium driver
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        
        # Mock job elements
        mock_job_element = Mock()
        mock_title_element = Mock()
        mock_title_element.text = "Software Engineer"
        mock_title_element.get_attribute.return_value = "https://seek.com/job/123"
        
        mock_company_element = Mock()
        mock_company_element.text = "Tech Corp"
        
        mock_location_element = Mock()
        mock_location_element.text = "Sydney, NSW"
        
        mock_job_element.find_element.side_effect = [
            mock_title_element,  # title
            mock_company_element,  # company
            mock_location_element,  # location
        ]
        
        scraper = SeekScraper()
        
        # Test parse_job_details
        job_data = scraper.parse_job_details(mock_job_element)
        
        assert job_data is not None
        assert job_data['title'] == "Software Engineer"
        assert job_data['company_name'] == "Tech Corp"
        assert job_data['location'] == "Sydney, NSW"
        assert job_data['source_website'] == "seek.com.au"
    
    @patch('app.scrapers.base_scraper.BaseScraper.get_selenium_driver')
    def test_indeed_scraper_mock(self, mock_driver):
        """Test Indeed scraper with mocked driver"""
        # Mock the selenium driver
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        
        # Mock job elements
        mock_job_element = Mock()
        mock_title_element = Mock()
        mock_title_element.text = "Data Analyst"
        mock_title_element.get_attribute.return_value = "https://indeed.com/job?jk=abc123"
        
        mock_company_element = Mock()
        mock_company_element.text = "Analytics Corp"
        
        mock_location_element = Mock()
        mock_location_element.text = "Melbourne, VIC"
        
        mock_job_element.find_element.side_effect = [
            mock_title_element,  # title
            mock_company_element,  # company
            mock_location_element,  # location
        ]
        
        scraper = IndeedScraper()
        
        # Test parse_job_details
        job_data = scraper.parse_job_details(mock_job_element)
        
        assert job_data is not None
        assert job_data['title'] == "Data Analyst"
        assert job_data['company_name'] == "Analytics Corp"
        assert job_data['location'] == "Melbourne, VIC"
        assert job_data['source_website'] == "indeed.com.au"
