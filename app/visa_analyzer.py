import re
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.models import VisaKeyword
import logging

logger = logging.getLogger(__name__)

class VisaFriendlyAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.visa_keywords = self._load_visa_keywords()
        
    def _load_visa_keywords(self) -> Dict[str, List[Dict]]:
        """Load visa keywords from database"""
        keywords = self.db.query(VisaKeyword).all()
        
        categorized = {
            'sponsorship_positive': [],
            'sponsorship_negative': [],
            'student_friendly': [],
            'experience_indicators': []
        }
        
        for keyword in keywords:
            if keyword.category == 'sponsorship' and keyword.keyword_type == 'positive':
                categorized['sponsorship_positive'].append({
                    'keyword': keyword.keyword.lower(),
                    'weight': keyword.weight
                })
            elif keyword.category == 'sponsorship' and keyword.keyword_type == 'negative':
                categorized['sponsorship_negative'].append({
                    'keyword': keyword.keyword.lower(),
                    'weight': keyword.weight
                })
            elif keyword.category == 'student_friendly':
                categorized['student_friendly'].append({
                    'keyword': keyword.keyword.lower(),
                    'weight': keyword.weight
                })
            elif keyword.category == 'experience':
                categorized['experience_indicators'].append({
                    'keyword': keyword.keyword.lower(),
                    'weight': keyword.weight
                })
        
        # If no keywords in DB, use defaults
        if not keywords:
            return self._get_default_keywords()
            
        return categorized
    
    def _get_default_keywords(self) -> Dict[str, List[Dict]]:
        """Default visa-friendly keywords"""
        return {
            'sponsorship_positive': [
                {'keyword': 'visa sponsorship', 'weight': 3.0},
                {'keyword': 'sponsor visa', 'weight': 3.0},
                {'keyword': '482 visa', 'weight': 2.5},
                {'keyword': '186 visa', 'weight': 2.5},
                {'keyword': '187 visa', 'weight': 2.5},
                {'keyword': 'temporary skill shortage', 'weight': 2.5},
                {'keyword': 'tss visa', 'weight': 2.5},
                {'keyword': 'employer nomination', 'weight': 2.0},
                {'keyword': 'skilled migration', 'weight': 2.0},
                {'keyword': 'work visa', 'weight': 1.5},
                {'keyword': 'international candidates', 'weight': 2.0},
                {'keyword': 'overseas applicants', 'weight': 2.0},
                {'keyword': 'global talent', 'weight': 1.8},
                {'keyword': 'relocation assistance', 'weight': 1.5}
            ],
            'sponsorship_negative': [
                {'keyword': 'australian citizens only', 'weight': -3.0},
                {'keyword': 'pr holders only', 'weight': -3.0},
                {'keyword': 'permanent residents only', 'weight': -3.0},
                {'keyword': 'no visa sponsorship', 'weight': -3.0},
                {'keyword': 'citizenship required', 'weight': -2.5},
                {'keyword': 'security clearance', 'weight': -2.0},
                {'keyword': 'must be eligible to work', 'weight': -1.0}
            ],
            'student_friendly': [
                {'keyword': 'graduate program', 'weight': 3.0},
                {'keyword': 'graduate opportunity', 'weight': 2.5},
                {'keyword': 'entry level', 'weight': 2.0},
                {'keyword': 'junior', 'weight': 2.0},
                {'keyword': 'internship', 'weight': 2.5},
                {'keyword': 'trainee', 'weight': 2.0},
                {'keyword': 'recent graduate', 'weight': 2.5},
                {'keyword': 'new graduate', 'weight': 2.5},
                {'keyword': 'student', 'weight': 1.5},
                {'keyword': 'mentorship', 'weight': 1.0},
                {'keyword': 'training provided', 'weight': 1.5}
            ],
            'experience_indicators': [
                {'keyword': '0-2 years', 'weight': 2.0},
                {'keyword': '1-3 years', 'weight': 1.5},
                {'keyword': 'no experience required', 'weight': 2.5},
                {'keyword': 'fresh graduate', 'weight': 2.0}
            ]
        }
    
    def analyze_job(self, job_data: Dict) -> Tuple[bool, float, bool]:
        """
        Analyze job for visa sponsorship and student-friendliness
        Returns: (visa_sponsorship, confidence_score, student_friendly)
        """
        text_content = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        # Calculate visa sponsorship score
        visa_score = 0.0
        student_score = 0.0
        
        # Check positive sponsorship indicators
        for item in self.visa_keywords['sponsorship_positive']:
            if item['keyword'] in text_content:
                visa_score += item['weight']
                
        # Check negative sponsorship indicators
        for item in self.visa_keywords['sponsorship_negative']:
            if item['keyword'] in text_content:
                visa_score += item['weight']  # These are negative weights
                
        # Check student-friendly indicators
        for item in self.visa_keywords['student_friendly']:
            if item['keyword'] in text_content:
                student_score += item['weight']
                
        # Check experience level indicators
        for item in self.visa_keywords['experience_indicators']:
            if item['keyword'] in text_content:
                student_score += item['weight']
        
        # Normalize scores
        visa_sponsorship = visa_score > 0.5
        confidence_score = min(max(visa_score / 5.0, 0.0), 1.0)  # Normalize to 0-1
        student_friendly = student_score > 1.0
        
        # Additional heuristics
        if self._check_company_size_friendly(job_data):
            student_score += 0.5
            
        if self._check_job_level_friendly(job_data):
            student_score += 1.0
            
        student_friendly = student_score > 1.0
        
        return visa_sponsorship, confidence_score, student_friendly
    
    def _check_company_size_friendly(self, job_data: Dict) -> bool:
        """Check if company size is typically student-friendly"""
        company_name = job_data.get('company_name', '').lower()
        
        # Large companies often have structured graduate programs
        large_companies = [
            'commonwealth bank', 'westpac', 'anz', 'nab',
            'telstra', 'optus', 'woolworths', 'coles',
            'bhp', 'rio tinto', 'fortescue', 'santos',
            'qantas', 'jetstar', 'virgin',
            'atlassian', 'canva', 'afterpay', 'zip'
        ]
        
        return any(company in company_name for company in large_companies)
    
    def _check_job_level_friendly(self, job_data: Dict) -> bool:
        """Check if job level is suitable for students"""
        title = job_data.get('title', '').lower()
        
        entry_indicators = [
            'graduate', 'junior', 'entry', 'trainee', 
            'intern', 'assistant', 'associate', 'coordinator'
        ]
        
        senior_indicators = [
            'senior', 'lead', 'principal', 'manager', 
            'director', 'head of', 'chief'
        ]
        
        has_entry = any(indicator in title for indicator in entry_indicators)
        has_senior = any(indicator in title for indicator in senior_indicators)
        
        return has_entry and not has_senior
    
    def extract_skills(self, job_data: Dict) -> Tuple[List[str], List[str]]:
        """Extract required and preferred skills from job description"""
        description = job_data.get('description', '').lower()
        
        # Common tech skills
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'angular', 'vue.js',
            'c++', 'c#', '.net', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'git', 'jenkins', 'ci/cd', 'agile', 'scrum', 'jira',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau', 'power bi'
        ]
        
        # Business skills
        business_skills = [
            'project management', 'communication', 'leadership', 'teamwork',
            'problem solving', 'analytical', 'customer service', 'sales',
            'marketing', 'finance', 'accounting', 'hr', 'operations'
        ]
        
        all_skills = tech_skills + business_skills
        found_skills = []
        
        for skill in all_skills:
            if skill in description:
                found_skills.append(skill)
        
        # Simple heuristic: first half are required, rest are preferred
        mid_point = len(found_skills) // 2
        required_skills = found_skills[:mid_point] if found_skills else []
        preferred_skills = found_skills[mid_point:] if found_skills else []
        
        return required_skills, preferred_skills
