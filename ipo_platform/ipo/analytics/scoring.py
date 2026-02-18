"""
Advanced Scoring Module
Provides sophisticated IPO scoring algorithms.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IPOAnalysis:
    """Complete IPO analysis result."""
    symbol: str
    financial_score: float
    growth_score: float
    risk_score: float
    momentum_score: float
    valuation_score: float
    quality_score: float
    overall_score: float
    percentiles: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class AdvancedScorer:
    """
    Advanced IPO scoring with multiple factors and peer comparison.
    """
    
    WEIGHTS = {
        'financial': 0.25,
        'growth': 0.20,
        'risk': 0.15,
        'momentum': 0.15,
        'valuation': 0.15,
        'quality': 0.10
    }
    
    def __init__(self, peer_data: List[Dict] = None):
        self.peer_data = peer_data or []
    
    def analyze_ipo(self, ipo, peers: List = None) -> IPOAnalysis:
        """Perform comprehensive IPO analysis."""
        financial_score = self._calculate_financial_score(ipo)
        growth_score = self._calculate_growth_score(ipo)
        risk_score = self._calculate_risk_score(ipo)
        momentum_score = self._calculate_momentum_score(ipo)
        valuation_score = self._calculate_valuation_score(ipo)
        quality_score = self._calculate_quality_score(ipo)
        
        overall_score = (
            financial_score * self.WEIGHTS['financial'] +
            growth_score * self.WEIGHTS['growth'] +
            risk_score * self.WEIGHTS['risk'] +
            momentum_score * self.WEIGHTS['momentum'] +
            valuation_score * self.WEIGHTS['valuation'] +
            quality_score * self.WEIGHTS['quality']
        )
        
        percentiles = self._calculate_percentiles(ipo, peers)
        strengths, weaknesses = self._identify_strengths_weaknesses(ipo, percentiles)
        recommendations = self._generate_recommendations(ipo, percentiles)
        
        return IPOAnalysis(
            symbol=getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
            financial_score=round(financial_score, 1),
            growth_score=round(growth_score, 1),
            risk_score=round(risk_score, 1),
            momentum_score=round(momentum_score, 1),
            valuation_score=round(valuation_score, 1),
            quality_score=round(quality_score, 1),
            overall_score=round(overall_score, 1),
            percentiles=percentiles,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    def _calculate_financial_score(self, ipo) -> float:
        score = 50
        
        roe = float(ipo.roe) if ipo.roe else None
        if roe is not None:
            if roe >= 20:
                score += 25
            elif roe >= 15:
                score += 20
            elif roe >= 10:
                score += 15
            elif roe >= 5:
                score += 10
            elif roe > 0:
                score += 5
            else:
                score -= 10
        else:
            score += 15
        
        roa = float(ipo.roa) if ipo.roa else None
        if roa is not None:
            if roa >= 10:
                score += 15
            elif roa >= 5:
                score += 10
            elif roa >= 2:
                score += 5
        else:
            score += 10
        
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        if debt_to_equity > 0:
            score -= min(15, debt_to_equity * 5)
        
        return min(100, max(0, score))
    
    def _calculate_growth_score(self, ipo) -> float:
        score = 50
        
        revenue_growth = float(ipo.revenue_growth) if ipo.revenue_growth else None
        if revenue_growth is not None:
            if revenue_growth >= 30:
                score += 30
            elif revenue_growth >= 20:
                score += 25
            elif revenue_growth >= 15:
                score += 20
            elif revenue_growth >= 10:
                score += 15
            elif revenue_growth >= 5:
                score += 10
            elif revenue_growth > 0:
                score += 5
            else:
                score -= 15
        else:
            score += 15
        
        market_cap = float(ipo.market_cap) if ipo.market_cap else None
        if market_cap:
            if market_cap > 10000000000:
                score += 20
            elif market_cap > 2000000000:
                score += 15
            elif market_cap > 500000000:
                score += 10
        
        return min(100, max(0, score))
    
    def _calculate_risk_score(self, ipo) -> float:
        score = 50
        
        volatility = float(ipo.volatility) if ipo.volatility else None
        if volatility is not None:
            if volatility >= 50:
                score += 30
            elif volatility >= 35:
                score += 20
            elif volatility >= 25:
                score += 10
            elif volatility >= 15:
                score += 5
            else:
                score -= 10
        else:
            score += 10
        
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        if debt_to_equity > 0:
            if debt_to_equity > 2:
                score += 20
            elif debt_to_equity > 1.5:
                score += 15
            elif debt_to_equity > 1:
                score += 10
        
        market_cap = float(ipo.market_cap) if ipo.market_cap else None
        if market_cap and market_cap < 500000000:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_momentum_score(self, ipo) -> float:
        score = 50
        
        status = getattr(ipo, 'status', 'UPCOMING')
        if status == 'LISTED':
            listing_price = float(ipo.listing_price) if ipo.listing_price else None
            current_price = float(ipo.current_price) if ipo.current_price else None
            if listing_price and current_price and listing_price > 0:
                return_change = ((current_price - listing_price) / listing_price) * 100
                score += min(30, max(-30, return_change))
        elif status == 'ONGOING':
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_valuation_score(self, ipo) -> float:
        score = 50
        
        pe_ratio = float(ipo.pe_ratio) if ipo.pe_ratio else None
        if pe_ratio is not None:
            if pe_ratio < 15:
                score += 25
            elif pe_ratio < 20:
                score += 20
            elif pe_ratio < 25:
                score += 15
            elif pe_ratio < 30:
                score += 10
            elif pe_ratio < 40:
                score += 5
            else:
                score -= 10
        else:
            score += 15
        
        issue_size = float(ipo.issue_size) if ipo.issue_size else None
        if issue_size:
            if 100000000 <= issue_size <= 10000000000:
                score += 15
        
        return min(100, max(0, score))
    
    def _calculate_quality_score(self, ipo) -> float:
        score = 50
        
        lead_manager = getattr(ipo, 'lead_manager', '') or ''
        quality_managers = ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Citi', 'Axis Capital', 'ICICI Securities']
        if any(qm.lower() in lead_manager.lower() for qm in quality_managers):
            score += 15
        elif lead_manager and lead_manager != 'N/A':
            score += 8
        
        listing_at = getattr(ipo, 'listing_at', 'NSE') or 'NSE'
        if listing_at in ['NSE', 'BSE']:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_percentiles(self, ipo, peers: List = None) -> Dict[str, float]:
        """Calculate percentile rankings against peers."""
        if not peers:
            return {k: 50 for k in ['overall', 'financial', 'growth', 'risk', 'momentum']}
        
        scores = {
            'financial': self._calculate_financial_score(ipo),
            'growth': self._calculate_growth_score(ipo),
            'risk': self._calculate_risk_score(ipo),
            'momentum': self._calculate_momentum_score(ipo)
        }
        
        percentiles = {}
        for key, score in scores.items():
            peer_values = [float(getattr(p, 'roe', 10)) if key == 'financial' else 
                          float(getattr(p, 'revenue_growth', 15)) if key == 'growth' else
                          float(getattr(p, 'volatility', 25)) if key == 'risk' else 50 for p in peers]
            below_count = sum(1 for v in peer_values if v < score)
            percentile = (below_count / len(peer_values)) * 100 if peer_values else 50
            percentiles[key] = round(percentile, 1)
        
        overall_score = sum(scores.values()) / len(scores)
        overall_scores = [sum([float(getattr(p, 'roe', 10)), float(getattr(p, 'revenue_growth', 15)), float(getattr(p, 'volatility', 25))]) / 3 for p in peers]
        below_count = sum(1 for v in overall_scores if v < overall_score)
        percentiles['overall'] = round((below_count / len(overall_scores)) * 100, 1) if overall_scores else 50
        
        return percentiles
    
    def _identify_strengths_weaknesses(self, ipo, percentiles: Dict) -> Tuple[List[str], List[str]]:
        strengths = []
        weaknesses = []
        
        categories = [
            ('financial', 'Financial Health'),
            ('growth', 'Growth Potential'),
            ('risk', 'Risk Profile'),
            ('momentum', 'Price Momentum'),
            ('valuation', 'Valuation'),
            ('quality', 'Quality Metrics')
        ]
        
        for key, label in categories:
            percentile = percentiles.get(key, 50)
            if percentile >= 75:
                strengths.append(f"{label} in top 25% of peers")
            elif percentile >= 60:
                strengths.append(f"{label} above average")
            elif percentile < 25:
                weaknesses.append(f"{label} in bottom 25% of peers")
            elif percentile < 40:
                weaknesses.append(f"{label} below average")
        
        roe = float(ipo.roe) if ipo.roe else None
        if roe and roe > 20:
            strengths.append("Strong ROE (>20%)")
        
        volatility = float(ipo.volatility) if ipo.volatility else None
        if volatility and volatility > 40:
            weaknesses.append("High volatility (>40%)")
        
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        if debt_to_equity > 1.5:
            weaknesses.append("High leverage (D/E > 1.5)")
        
        return strengths[:5], weaknesses[:5]
    
    def _generate_recommendations(self, ipo, percentiles: Dict) -> List[str]:
        recommendations = []
        
        overall = percentiles.get('overall', 50)
        if overall >= 75:
            recommendations.append("Strong candidate - consider allocating more capital")
        elif overall >= 60:
            recommendations.append("Solid choice - suitable for core portfolio")
        elif overall >= 40:
            recommendations.append("Average pick - consider for satellite portfolio")
        else:
            recommendations.append("Weaker candidate - careful position sizing needed")
        
        risk_percentile = percentiles.get('risk', 50)
        if risk_percentile > 70:
            recommendations.append("Higher risk - use smaller position size")
        elif risk_percentile < 30:
            recommendations.append("Lower risk profile - suitable for conservative investors")
        
        growth_percentile = percentiles.get('growth', 50)
        if growth_percentile > 70:
            recommendations.append("Strong growth - consider for growth allocation")
        
        pe_ratio = float(ipo.pe_ratio) if ipo.pe_ratio else None
        if pe_ratio and pe_ratio > 40:
            recommendations.append("Premium valuation - wait for better entry point")
        elif pe_ratio and pe_ratio > 0 and pe_ratio < 15:
            recommendations.append("Attractive valuation - good entry opportunity")
        
        return recommendations[:3]


class PeerComparator:
    def __init__(self, ipos: List):
        self.ipos = ipos
        self.scorer = AdvancedScorer(ipos)
    
    def get_rankings(self, metric: str = 'overall_score') -> List[Dict]:
        rankings = []
        for ipo in self.ipos:
            analysis = self.scorer.analyze_ipo(ipo, self.ipos)
            score = analysis.overall_score
            rankings.append({
                'ipo': ipo,
                'score': score,
                'analysis': analysis
            })
        
        rankings.sort(key=lambda x: x['score'], reverse=True)
        return rankings
    
    def get_top_performers(self, n: int = 5) -> List[Dict]:
        return self.get_rankings()[:n]
    
    def get_sector_leaders(self, sector: str) -> List[Dict]:
        sector_ipos = [ipo for ipo in self.ipos if getattr(ipo, 'sector', '') == sector]
        comparator = PeerComparator(sector_ipos)
        return comparator.get_rankings()
    
    def compare(self, ipo1, ipo2) -> Dict:
        analysis1 = self.scorer.analyze_ipo(ipo1, self.ipos)
        analysis2 = self.scorer.analyze_ipo(ipo2, self.ipos)
        
        comparisons = {}
        for field in ['financial_score', 'growth_score', 'risk_score', 
                      'momentum_score', 'valuation_score', 'quality_score', 'overall_score']:
            val1 = getattr(analysis1, field, 0)
            val2 = getattr(analysis2, field, 0)
            comparisons[field] = {
                'ipo1': round(val1, 1),
                'ipo2': round(val2, 1),
                'winner': 'ipo1' if val1 > val2 else ('ipo2' if val2 > val1 else 'tie')
            }
        
        return {
            'ipo1': {'name': ipo1.company_name, 'analysis': analysis1},
            'ipo2': {'name': ipo2.company_name, 'analysis': analysis2},
            'comparisons': comparisons
        }


def calculate_composite_score(scores: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """Calculate weighted composite score."""
    if weights is None:
        weights = AdvancedScorer.WEIGHTS
    
    total = 0
    total_weight = 0
    
    for category, score in scores.items():
        weight = weights.get(category, 0)
        total += score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 50
    
    return min(100, max(0, total / total_weight))

