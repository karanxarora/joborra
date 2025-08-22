"""
Comprehensive visa keyword management system for Australia
"""

from typing import Dict, List, Set
import re
from dataclasses import dataclass

@dataclass
class KeywordMatch:
    keyword: str
    category: str
    weight: float
    positions: List[int]

class VisaKeywordAnalyzer:
    """Analyze job descriptions for visa-friendly indicators"""
    
    def __init__(self):
        self.positive_keywords = {
            # Visa types & work rights
            'visa_types': [
                'international students', 'student visa', 'graduate visa',
                '485 visa', '500 visa', 'subclass 485', 'subclass 500',
                'subclass 482', '482 visa', 'TSS visa', 'sponsorship',
                'visa sponsorship', 'employer sponsorship', 'work rights',
                'full working rights', 'valid visa', 'eligible to work in Australia',
                'work permit'
            ],
            # Programs & entry routes
            'programs': [
                'internship', 'graduate program', 'graduate role',
                'trainee program', 'cadetship'
            ],
            # HR openness indicators
            'openness': [
                'welcome international', 'open to candidates requiring sponsorship',
                'overseas applicants welcome', 'visa support',
                'support for relocation'
            ]
        }
        
        self.negative_keywords = {
            # Citizenship requirements
            'citizenship': [
                'Australian citizen only', 'must be an Australian citizen',
                'Australian citizenship required', 'must be PR',
                'permanent resident only'
            ],
            # Security clearance
            'clearance': [
                'security clearance required', 'baseline clearance',
                'NV1 clearance', 'NV2 clearance'
            ]
        }
        
        # Keyword weights for scoring
        self.weights = {
            'visa_types': 2.0,
            'programs': 1.5,
            'openness': 1.8,
            'citizenship': -3.0,
            'clearance': -2.5
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text for visa-friendly indicators"""
        text_lower = text.lower()
        
        positive_matches = []
        negative_matches = []
        total_score = 0.0
        
        # Check positive keywords
        for category, keywords in self.positive_keywords.items():
            weight = self.weights.get(category, 1.0)
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    positions = [m.start() for m in re.finditer(re.escape(keyword.lower()), text_lower)]
                    match = KeywordMatch(keyword, category, weight, positions)
                    positive_matches.append(match)
                    total_score += weight
        
        # Check negative keywords
        for category, keywords in self.negative_keywords.items():
            weight = self.weights.get(category, -1.0)
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    positions = [m.start() for m in re.finditer(re.escape(keyword.lower()), text_lower)]
                    match = KeywordMatch(keyword, category, abs(weight), positions)
                    negative_matches.append(match)
                    total_score += weight
        
        # Calculate confidence score (0-1)
        max_possible_positive = sum(len(keywords) * self.weights.get(cat, 1.0) 
                                  for cat, keywords in self.positive_keywords.items())
        confidence = max(0.0, min(1.0, total_score / (max_possible_positive * 0.1)))
        
        # Determine visa friendliness
        is_visa_friendly = len(positive_matches) > 0 and len(negative_matches) == 0
        is_student_friendly = any(
            keyword in text_lower for keyword in 
            ['student', 'graduate', 'internship', 'trainee', 'cadet']
        )
        
        return {
            'is_visa_friendly': is_visa_friendly,
            'confidence_score': confidence,
            'is_student_friendly': is_student_friendly,
            'positive_matches': positive_matches,
            'negative_matches': negative_matches,
            'total_score': total_score
        }
    
    def get_all_keywords(self) -> Dict[str, List[str]]:
        """Get all keywords organized by type"""
        all_keywords = {}
        
        # Flatten positive keywords
        for category, keywords in self.positive_keywords.items():
            all_keywords[f'positive_{category}'] = keywords
        
        # Flatten negative keywords
        for category, keywords in self.negative_keywords.items():
            all_keywords[f'negative_{category}'] = keywords
        
        return all_keywords
    
    def add_keyword(self, keyword: str, category: str, is_positive: bool = True, weight: float = 1.0):
        """Add a new keyword to the analyzer"""
        keyword_dict = self.positive_keywords if is_positive else self.negative_keywords
        
        if category not in keyword_dict:
            keyword_dict[category] = []
        
        if keyword.lower() not in [k.lower() for k in keyword_dict[category]]:
            keyword_dict[category].append(keyword)
            
        # Update weight if provided
        if category not in self.weights:
            self.weights[category] = weight if is_positive else -weight
    
    def remove_keyword(self, keyword: str, category: str, is_positive: bool = True):
        """Remove a keyword from the analyzer"""
        keyword_dict = self.positive_keywords if is_positive else self.negative_keywords
        
        if category in keyword_dict:
            keyword_dict[category] = [k for k in keyword_dict[category] 
                                    if k.lower() != keyword.lower()]


# Initialize global analyzer instance
visa_analyzer = VisaKeywordAnalyzer()

def analyze_job_visa_friendliness(title: str, description: str) -> Dict:
    """Convenience function to analyze a job's visa friendliness"""
    combined_text = f"{title} {description}"
    return visa_analyzer.analyze_text(combined_text)
