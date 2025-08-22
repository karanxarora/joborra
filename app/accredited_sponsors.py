"""
Accredited Sponsor list integration for employer prioritization
"""

import requests
import pandas as pd
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class AccreditedSponsorManager:
    """Manage Australian accredited sponsor data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.sponsors_file = self.data_dir / "accredited_sponsors.csv"
        self.sponsors_set = set()
        self.sponsors_data = {}
        
    def load_sponsors_from_csv(self, csv_path: str = None) -> bool:
        """Load sponsors from CSV file"""
        try:
            file_path = csv_path or self.sponsors_file
            if not Path(file_path).exists():
                logger.warning(f"Sponsors file not found: {file_path}")
                return False
            
            df = pd.read_csv(file_path)
            
            # Expected columns: company_name, abn, status, approval_date, etc.
            for _, row in df.iterrows():
                company_name = str(row.get('company_name', '')).strip()
                if company_name:
                    normalized_name = self.normalize_company_name(company_name)
                    self.sponsors_set.add(normalized_name)
                    self.sponsors_data[normalized_name] = {
                        'original_name': company_name,
                        'abn': row.get('abn', ''),
                        'status': row.get('status', 'active'),
                        'approval_date': row.get('approval_date', ''),
                        'location': row.get('location', '')
                    }
            
            logger.info(f"Loaded {len(self.sponsors_set)} accredited sponsors")
            return True
            
        except Exception as e:
            logger.error(f"Error loading sponsors from CSV: {e}")
            return False
    
    def download_sponsors_data(self) -> bool:
        """
        Download latest accredited sponsors data from Department of Home Affairs
        Note: This would need to be adapted based on the actual data source format
        """
        try:
            # This is a placeholder - the actual implementation would depend on
            # the specific format and URL of the Home Affairs data
            
            # Example URLs (these may not be current):
            urls = [
                "https://www.homeaffairs.gov.au/reports-and-publications/files/accredited-sponsors.csv",
                # Add other potential URLs
            ]
            
            for url in urls:
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        with open(self.sponsors_file, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"Downloaded sponsors data from {url}")
                        return self.load_sponsors_from_csv()
                except requests.RequestException:
                    continue
            
            logger.warning("Could not download sponsors data from any URL")
            return False
            
        except Exception as e:
            logger.error(f"Error downloading sponsors data: {e}")
            return False
    
    def normalize_company_name(self, company_name: str) -> str:
        """Normalize company name for matching"""
        if not company_name:
            return ""
        
        # Convert to lowercase and remove common suffixes/prefixes
        normalized = company_name.lower().strip()
        
        # Remove common company suffixes
        suffixes = [
            'pty ltd', 'pty. ltd.', 'pty ltd.', 'pty. ltd',
            'limited', 'ltd', 'ltd.', 'inc', 'inc.', 'corp', 'corp.',
            'company', 'co', 'co.', 'group', 'grp', 'australia',
            'australian', 'au'
        ]
        
        for suffix in suffixes:
            if normalized.endswith(f' {suffix}'):
                normalized = normalized[:-len(f' {suffix}')].strip()
        
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def is_accredited_sponsor(self, company_name: str) -> bool:
        """Check if a company is an accredited sponsor"""
        if not company_name:
            return False
        
        normalized = self.normalize_company_name(company_name)
        return normalized in self.sponsors_set
    
    def find_similar_sponsors(self, company_name: str, threshold: float = 0.8) -> List[Dict]:
        """Find similar sponsor names using fuzzy matching"""
        try:
            from difflib import SequenceMatcher
        except ImportError:
            logger.warning("difflib not available for fuzzy matching")
            return []
        
        if not company_name:
            return []
        
        normalized_input = self.normalize_company_name(company_name)
        matches = []
        
        for sponsor_name in self.sponsors_set:
            similarity = SequenceMatcher(None, normalized_input, sponsor_name).ratio()
            if similarity >= threshold:
                matches.append({
                    'sponsor_name': sponsor_name,
                    'similarity': similarity,
                    'data': self.sponsors_data.get(sponsor_name, {})
                })
        
        # Sort by similarity descending
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
    
    def get_sponsor_info(self, company_name: str) -> Optional[Dict]:
        """Get detailed sponsor information"""
        normalized = self.normalize_company_name(company_name)
        return self.sponsors_data.get(normalized)
    
    def get_sponsors_count(self) -> int:
        """Get total number of loaded sponsors"""
        return len(self.sponsors_set)
    
    def search_sponsors(self, query: str) -> List[Dict]:
        """Search sponsors by name"""
        if not query:
            return []
        
        query_normalized = self.normalize_company_name(query)
        results = []
        
        for sponsor_name, data in self.sponsors_data.items():
            if query_normalized in sponsor_name:
                results.append({
                    'sponsor_name': sponsor_name,
                    'data': data
                })
        
        return results

# Global instance
sponsor_manager = AccreditedSponsorManager()

def check_company_sponsor_status(company_name: str) -> Dict:
    """Check if a company is an accredited sponsor and get details"""
    is_sponsor = sponsor_manager.is_accredited_sponsor(company_name)
    sponsor_info = sponsor_manager.get_sponsor_info(company_name) if is_sponsor else None
    
    # If not exact match, try fuzzy matching
    similar_sponsors = []
    if not is_sponsor:
        similar_sponsors = sponsor_manager.find_similar_sponsors(company_name, threshold=0.7)
        if similar_sponsors:
            # Consider it a potential sponsor if high similarity match found
            best_match = similar_sponsors[0]
            if best_match['similarity'] > 0.9:
                is_sponsor = True
                sponsor_info = best_match['data']
    
    return {
        'is_accredited_sponsor': is_sponsor,
        'sponsor_info': sponsor_info,
        'similar_sponsors': similar_sponsors[:3],  # Top 3 matches
        'confidence': similar_sponsors[0]['similarity'] if similar_sponsors else 1.0 if is_sponsor else 0.0
    }
