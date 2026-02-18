"""
NSE India IPO Data Service
Fetches authentic IPO data from NSE's official API.
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class NSEIPOService:
    """Service to fetch IPO data from NSE India."""
    
    BASE_URL = "https://www.nseindia.com"
    
    # NSE API endpoints
    ENDPOINTS = {
        'current': '/api/ipo-current-issues',
        'upcoming': '/api/ipo-upcoming-issues',
        'past': '/api/ipo-past-issues'
    }
    
    # Required headers to avoid blocking
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nseindia.com/'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize session with cookies from NSE homepage."""
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            logger.info("NSE session initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {e}")
    
    def fetch_current_ipos(self) -> List[Dict]:
        """Fetch currently ongoing IPOs."""
        return self._fetch_ipos('current')
    
    def fetch_upcoming_ipos(self) -> List[Dict]:
        """Fetch upcoming IPOs."""
        return self._fetch_ipos('upcoming')
    
    def fetch_past_ipos(self) -> List[Dict]:
        """Fetch past/listed IPOs."""
        return self._fetch_ipos('past')
    
    def fetch_all_ipos(self) -> Dict[str, List[Dict]]:
        """Fetch all IPO categories."""
        return {
            'current': self.fetch_current_ipos(),
            'upcoming': self.fetch_upcoming_ipos(),
            'past': self.fetch_past_ipos()
        }
    
    def _fetch_ipos(self, category: str) -> List[Dict]:
        """Fetch IPOs from NSE API."""
        if category not in self.ENDPOINTS:
            logger.error(f"Invalid category: {category}")
            return []
        
        url = f"{self.BASE_URL}{self.ENDPOINTS[category]}"
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ipos = self._parse_nse_response(data, category)
                logger.info(f"Fetched {len(ipos)} {category} IPOs from NSE")
                return ipos
            else:
                logger.error(f"NSE API returned status {response.status_code} for {category}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching {category} IPOs: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching {category} IPOs: {e}")
            return []
    
    def _parse_nse_response(self, data: Dict, category: str) -> List[Dict]:
        """Parse NSE API response into standardized format."""
        ipos = []
        
        # NSE returns data in different formats for different endpoints
        if isinstance(data, dict):
            ipo_list = data.get('data', []) or data.get('issues', [])
        elif isinstance(data, list):
            ipo_list = data
        else:
            logger.warning(f"Unexpected NSE response format for {category}")
            return []
        
        for item in ipo_list:
            try:
                parsed = self._parse_ipo_item(item, category)
                if parsed:
                    ipos.append(parsed)
            except Exception as e:
                logger.error(f"Error parsing IPO item: {e}")
                continue
        
        return ipos
    
    def _parse_ipo_item(self, item: Dict, category: str) -> Optional[Dict]:
        """Parse individual IPO item from NSE."""
        try:
            # Map NSE status to our model
            status_map = {
                'current': 'ONGOING',
                'upcoming': 'UPCOMING',
                'past': 'LISTED'
            }
            
            # Extract company name (NSE uses different field names)
            company_name = (
                item.get('companyName') or 
                item.get('issuerCompany') or 
                item.get('company') or
                'Unknown Company'
            )
            
            # Extract symbol
            symbol = (
                item.get('symbol') or 
                item.get('scrip') or
                company_name[:4].upper()
            )
            
            # Parse dates
            open_date = self._parse_date(item.get('openDate') or item.get('issueStartDate'))
            close_date = self._parse_date(item.get('closeDate') or item.get('issueEndDate'))
            listing_date = self._parse_date(item.get('listingDate'))
            
            # Parse price band
            price_band_lower, price_band_upper = self._parse_price_band(
                item.get('priceBand') or item.get('issuePrice')
            )
            
            # Parse issue size
            issue_size = self._parse_issue_size(
                item.get('issueSize') or item.get('totalIssueSize')
            )
            
            return {
                'company_name': company_name,
                'symbol': symbol,
                'status': status_map.get(category, 'UPCOMING'),
                'open_date': open_date,
                'close_date': close_date,
                'listing_date': listing_date,
                'price_band_lower': price_band_lower,
                'price_band_upper': price_band_upper,
                'issue_size': issue_size,
                'listing_at': item.get('exchange', 'NSE'),
                'lead_manager': item.get('leadManager', ''),
                'registrar': item.get('registrar', ''),
                'sector': item.get('sector') or item.get('industry', 'General'),
                'lot_size': self._parse_int(item.get('lotSize')),
                'listing_price': self._parse_decimal(item.get('listingPrice')),
                'nse_data': item  # Store raw NSE data for reference
            }
            
        except Exception as e:
            logger.error(f"Error parsing IPO item: {e}")
            return None
    
    def _parse_date(self, date_str) -> Optional[datetime]:
        """Parse date string from NSE."""
        if not date_str:
            return None
        
        # Try common date formats
        formats = [
            '%d-%b-%Y',  # 15-Jan-2024
            '%d/%m/%Y',  # 15/01/2024
            '%Y-%m-%d',  # 2024-01-15
            '%d %b %Y',  # 15 Jan 2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _parse_price_band(self, price_str) -> tuple:
        """Parse price band string."""
        if not price_str:
            return None, None
        
        try:
            # Handle formats like "100-120" or "₹100 to ₹120"
            price_str = str(price_str).replace('₹', '').replace('Rs', '').strip()
            
            if '-' in price_str:
                parts = price_str.split('-')
            elif 'to' in price_str.lower():
                parts = price_str.lower().split('to')
            else:
                # Single price
                price = Decimal(price_str.strip())
                return price, price
            
            lower = Decimal(parts[0].strip())
            upper = Decimal(parts[1].strip())
            return lower, upper
            
        except Exception as e:
            logger.warning(f"Could not parse price band: {price_str}")
            return None, None
    
    def _parse_issue_size(self, size_str) -> Optional[Decimal]:
        """Parse issue size (usually in crores)."""
        if not size_str:
            return None
        
        try:
            # Remove currency symbols and text
            size_str = str(size_str).replace('₹', '').replace('Rs', '').replace('Cr', '').replace('crore', '').strip()
            return Decimal(size_str)
        except Exception:
            logger.warning(f"Could not parse issue size: {size_str}")
            return None
    
    def _parse_decimal(self, value) -> Optional[Decimal]:
        """Parse decimal value."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None
    
    def _parse_int(self, value) -> Optional[int]:
        """Parse integer value."""
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None
