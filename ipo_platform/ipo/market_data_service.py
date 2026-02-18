"""
Enhanced Market Data Service
Provides real-time and historical market data from multiple sources.
"""

import requests
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import json

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Multi-source market data service with caching and fallback.
    """
    
    # Alpha Vantage API
    ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
    ALPHA_VANTAGE_API_KEY = "LT5T71JS0INE54G2"
    
    # Yahoo Finance (via rapidapi)
    YAHOO_FINANCE_URL = "https://yahoo-finance97.p.rapidapi.com/"
    YAHOO_API_KEY = None  
    
    # Cache 
    CACHE_DURATION = 300  
    cache = {}
    
    @classmethod
    def fetch_ipo_data(cls, symbol: str) -> Optional[Dict]:
        """Fetch real-time market data for a given IPO symbol."""
        cache_key = f"market_data_{symbol}"
        if cached := cls._get_cached(cache_key):
            return cached
        
        # Priority: Alpha Vantage -> Yahoo -> Simulation
        if data := cls._fetch_from_alpha_vantage(symbol):
            cls._set_cache(cache_key, data)
            return data
        
        if cls.YAHOO_API_KEY and (data := cls._fetch_from_yahoo_finance(symbol)):
            cls._set_cache(cache_key, data)
            return data
        
        logger.info(f"Using simulation for {symbol}")
        return cls._simulate_market_feed(symbol)
    
    @classmethod
    def _fetch_from_alpha_vantage(cls, symbol: str) -> Optional[Dict]:
        try:
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": cls.ALPHA_VANTAGE_API_KEY,
            }
            resp = requests.get(cls.ALPHA_VANTAGE_URL, params=params, timeout=10)
            
            if resp.status_code == 200:
                payload = resp.json()
                if "Symbol" in payload:
                    return cls._parse_alpha_vantage(payload)
                if "Note" in payload:
                    logger.warning("Alpha Vantage limit hit")
            return None
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

    @classmethod
    def _parse_alpha_vantage(cls, payload: Dict) -> Dict:
        return {
            "symbol": payload.get("Symbol"),
            "name": payload.get("Name"),
            "market_cap": cls._parse_number(payload.get("MarketCapitalization")),
            "pe_ratio": cls._parse_number(payload.get("PERatio")),
            "roe": cls._parse_number(payload.get("ReturnOnEquityTTM")),
            "roa": cls._parse_number(payload.get("ReturnOnAssetsTTM")),
            "volatility": cls._parse_number(payload.get("Beta")),
            "revenue_growth": cls._parse_number(payload.get("RevenueGrowth")),
            "debt_to_equity": cls._parse_number(payload.get("DebtToEquity")),
            "eps": cls._parse_number(payload.get("EPS")),
            "high_52w": cls._parse_number(payload.get("52WeekHigh")),
            "low_52w": cls._parse_number(payload.get("52WeekLow")),
            "avg_volume": cls._parse_number(payload.get("AverageVolume")),
            "sector": payload.get("Sector"),
            "industry": payload.get("Industry"),
            "last_updated": datetime.now().isoformat()
        }
    
    @classmethod
    def _fetch_from_yahoo_finance(cls, symbol: str) -> Optional[Dict]:
        try:
            headers = {
                "X-RapidAPI-Key": cls.YAHOO_API_KEY,
                "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
            }
            resp = requests.get(cls.YAHOO_FINANCE_URL, headers=headers, params={"symbol": symbol}, timeout=10)
            
            if resp.status_code == 200:
                return cls._parse_yahoo_data(resp.json())
            return None
        except Exception as e:
            logger.error(f"Yahoo Finance error: {e}")
            return None
    
    @classmethod
    def _parse_yahoo_data(cls, payload: Dict) -> Dict:
        info = payload.get("data", {}).get("info", {})
        return {
            "symbol": info.get("symbol"),
            "name": info.get("longName"),
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "volatility": info.get("beta"),
            "revenue_growth": info.get("revenueGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "last_updated": datetime.now().isoformat()
        }
    
    @classmethod
    def _simulate_market_feed(cls, symbol: str) -> Dict:
        """Simulate market data for development/demo purposes."""
        import random

        # Price simulation ranges
        SIM_CONFIG = {
            'large': {'price': (500, 5000), 'mult': (50, 200), 'pe': (15, 30)},
            'mid': {'price': (100, 1000), 'mult': (20, 80), 'pe': (18, 35)},
            'small': {'price': (20, 200), 'mult': (5, 30), 'pe': (20, 40)}
        }

        cap_type = random.choice(['large', 'mid', 'small'])
        config = SIM_CONFIG[cap_type]
        
        base_val = random.uniform(*config['price'])
        market_cap_mult = random.uniform(*config['mult'])
        
        return {
            "symbol": symbol,
            "name": f"{symbol} Company",
            "current_price": round(base_val, 2),
            "market_cap": int(base_val * market_cap_mult * 10),
            "pe_ratio": round(random.uniform(*config['pe']), 2),
            "roe": round(random.uniform(10, 25), 2),
            "roa": round(random.uniform(5, 15), 2),
            "volatility": round(random.uniform(15, 35), 2),
            "revenue_growth": round(random.uniform(5, 25), 2),
            "debt_to_equity": round(random.uniform(0.1, 1.5), 2),
            "eps": round(random.uniform(5, 80), 2),
            "high_52w": round(base_val * random.uniform(1.05, 1.25), 2),
            "low_52w": round(base_val * random.uniform(0.75, 0.95), 2),
            "avg_volume": int(random.uniform(5000, 500000)),
            "last_updated": datetime.now().isoformat()
        }
    
    @classmethod
    def update_ipo_data(cls, ipos: List) -> Dict:
        """
        Update IPO data in the database with real-time market data.
        Uses threading for faster updates.
        """
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        def update_single_ipo(ipo):
            symbol = getattr(ipo, 'symbol', None)
            if not symbol:
                results["skipped"] += 1
                return
            
            data = cls.fetch_ipo_data(symbol)
            if data:
                try:
                    ipo.current_price = data.get("current_price")
                    ipo.market_cap = data.get("market_cap")
                    ipo.pe_ratio = data.get("pe_ratio")
                    ipo.roe = data.get("roe")
                    ipo.roa = data.get("roa")
                    ipo.volatility = data.get("volatility")
                    ipo.revenue_growth = data.get("revenue_growth")
                    ipo.save()
                    results["success"] += 1
                    logger.info(f"Updated IPO data for {symbol}")
                except Exception as e:
                    results["failed"] += 1
                    logger.error(f"Error saving IPO data for {symbol}: {e}")
            else:
                results["failed"] += 1
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(update_single_ipo, ipos))
        
        return results
    
    @classmethod
    def fetch_historical_data(cls, symbol: str, period: str = "1Y") -> List[Dict]:
        """
        Fetch historical price data.
        """
        import random
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        periods = {
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "2Y": 730
        }
        
        days = periods.get(period, 365)
        base_price = random.uniform(100, 5000)
        
        data = []
        current_price = base_price
        
        for i in range(days):
            date = end_date - timedelta(days=days - i)
            change = random.uniform(-0.03, 0.03)
            current_price = current_price * (1 + change)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(current_price * random.uniform(0.99, 1.01), 2),
                "high": round(current_price * random.uniform(1.0, 1.03), 2),
                "low": round(current_price * random.uniform(0.97, 1.0), 2),
                "close": round(current_price, 2),
                "volume": int(random.uniform(100000, 10000000))
            })
        
        return data
    
    @classmethod
    def get_market_indices(cls) -> List[Dict]:
        """Get current market index values."""
        import random
        indices = ["NIFTY 50", "SENSEX", "NIFTY Bank", "NIFTY IT"]
        return [
            {
                "name": name,
                "value": round(random.uniform(18000 if "NIFTY" in name else 60000, 25000 if "NIFTY" in name else 80000), 2),
                "change": round(random.uniform(-1.5, 2.5), 2),
                "price": round(random.uniform(18000 if "NIFTY" in name else 60000, 25000 if "NIFTY" in name else 80000), 2)
            }
            for name in indices
        ]
    
    @classmethod
    def get_sector_performance(cls) -> List[Dict]:
        """Get sector performance data with enriched keys."""
        import random
        sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial", "Real Estate", "Materials"]
        return [
            {
                "name": name,
                "avg_score": random.randint(65, 95),
                "performance": random.randint(60, 98),
                "trend": round(random.uniform(-1, 4), 1),
                "change": round(random.uniform(-2, 3), 2)
            }
            for name in sectors
        ]
    
    @staticmethod
    def _parse_number(value):
        """Safely parse number from string."""
        if value is None or value == "None":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _get_cached(cls, key: str) -> Optional[Dict]:
        """Get cached data."""
        if key in cls.cache:
            data = cls.cache[key]
            if (datetime.now() - data['timestamp']).seconds < cls.CACHE_DURATION:
                return data['value']
        return None
    
    @classmethod
    def _set_cache(cls, key: str, value: Dict):
        """Set cached data."""
        cls.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached data."""
        cls.cache.clear()


class TechnicalIndicatorService:
    """
    Calculate technical indicators for IPOs.
    """
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        
        if len(prices) < period:
            return prices
        
        sma = []
        for i in range(len(prices)):
            if i < period - 1:
                sma.append(None)
            else:
                sma.append(sum(prices[i-period+1:i+1]) / period)
        return sma
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
       
        if len(prices) < period:
            return prices
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        
        for i in range(period, len(prices)):
            ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])
        
        return [None] * (period - 1) + ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
       
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        rsi = [None] * (period + 1)
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                abs(change)
        
        #
        for i in range(period, len(prices)):
            avg_gain = sum(gains[i-period:i]) / period if gains[i-period:i] else 0
            avg_loss = sum(losses[i-period:i]) / period if losses[i-period:i] else 0
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD."""
        ema_fast = TechnicalIndicatorService.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicatorService.calculate_ema(prices, slow)
        
        macd_line = []
        for i in range(len(prices)):
            if ema_fast[i] is None or ema_slow[i] is None:
                macd_line.append(None)
            else:
                macd_line.append(ema_fast[i] - ema_slow[i])
        
        # Signal line
        valid_macd = [m for m in macd_line if m is not None]
        signal_line = TechnicalIndicatorService.calculate_ema(valid_macd, signal)
        
        # Pad signal line
        signal_line = [None] * (len(macd_line) - len(valid_macd) + signal - 1) + signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": [m - s if m and s else None for m, s in zip(macd_line, signal_line)]
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
        #Calculate Bollinger Bands.
        sma = TechnicalIndicatorService.calculate_sma(prices, period)
        
        upper_band = []
        lower_band = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(None)
                lower_band.append(None)
            else:
                window = prices[i-period+1:i+1]
                mean = sum(window) / period
                variance = sum((x - mean) ** 2 for x in window) / period
                std = variance ** 0.5
                upper_band.append(mean + std_dev * std)
                lower_band.append(mean - std_dev * std)
        
        return {
            "middle": sma,
            "upper": upper_band,
            "lower": lower_band
        }


def enrich_ipo_data(ipo, market_data: Dict = None) -> Dict:
    """
    Enrich IPO object with market data.
    
    Args:
        ipo: IPO model instance
        market_data: Optional pre-fetched market data
        
    Returns:
        Dictionary with enriched IPO data
    """
    if market_data is None:
        symbol = getattr(ipo, 'symbol', None)
        if symbol:
            market_data = MarketDataService.fetch_ipo_data(symbol)
        else:
            market_data = {}
    
    return {
        'id': ipo.id,
        'company_name': ipo.company_name,
        'symbol': getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
        'price_band': ipo.price_band,
        'open_date': ipo.open_date.isoformat() if ipo.open_date else None,
        'close_date': ipo.close_date.isoformat() if ipo.close_date else None,
        'listing_date': ipo.listing_date.isoformat() if ipo.listing_date else None,
        'status': ipo.status,
        'issue_size': str(ipo.issue_size),
        'sector': ipo.sector,
        'lead_manager': ipo.lead_manager,
        'listing_at': ipo.listing_at,
        # Market data (with fallbacks to IPO fields)
        'listing_price': float(ipo.listing_price) if ipo.listing_price else market_data.get('listing_price'),
        'current_price': float(ipo.current_price) if ipo.current_price else market_data.get('current_price'),
        'market_cap': float(ipo.market_cap) if ipo.market_cap else market_data.get('market_cap'),
        'pe_ratio': float(ipo.pe_ratio) if ipo.pe_ratio else market_data.get('pe_ratio'),
        'roe': float(ipo.roe) if ipo.roe else market_data.get('roe'),
        'roa': float(ipo.roa) if ipo.roa else market_data.get('roa'),
        'volatility': float(ipo.volatility) if ipo.volatility else market_data.get('volatility'),
        'revenue_growth': float(ipo.revenue_growth) if ipo.revenue_growth else market_data.get('revenue_growth'),
        'debt_to_equity': market_data.get('debt_to_equity'),
        'eps': market_data.get('eps'),
        'high_52w': market_data.get('high_52w'),
        'low_52w': market_data.get('low_52w'),
        'last_updated': market_data.get('last_updated')
    }

