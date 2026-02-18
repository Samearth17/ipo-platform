"""
Portfolio Optimization Module
Implements Modern Portfolio Theory (MPT) for IPO portfolio optimization.
"""

from decimal import Decimal
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """
    Portfolio optimizer using Modern Portfolio Theory.
    """
    
    RISK_FREE_RATE = 0.05  # 5% annual risk-free rate
    
    def __init__(self, investor_profile):
        self.profile = investor_profile
        self.risk_params = investor_profile.get_risk_parameters()
        self.strategy = investor_profile.get_persona_strategy()
        
    def optimize_portfolio(self, ipos: List, allocation_amount: float = None, diversification: int = 5) -> Dict:
        """Optimize portfolio allocation based on investor profile."""
        if allocation_amount is None:
            allocation_amount = float(self.profile.max_investment)
        
        from .recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine(self.profile)
        recommendations = engine.get_filtered_recommendations(
            ipos, 
            filters={'only_compatible': True, 'min_score': 40}
        )
        
        if not recommendations:
            return {
                'success': False,
                'error': 'No compatible IPOs found for your risk profile',
                'portfolio': [],
                'metrics': None
            }
        
        portfolio = self._build_efficient_portfolio(recommendations, allocation_amount, diversification)
        metrics = self._calculate_advanced_metrics(portfolio, recommendations)
        
        return {
            'success': True,
            'portfolio': portfolio,
            'metrics': metrics,
            'total_allocation': allocation_amount,
            'strategy': self.strategy['name']
        }
    
    def _build_efficient_portfolio(self, recommendations: List, total_amount: float, diversification: int = 5) -> List[Dict]:
        """Build an efficient portfolio using enhanced selection logic."""
        portfolio = []
        
        # Determine number of holdings base on diversification level (1 to 10)
        # 1-3: concentrated (few holdings), 4-7: balanced, 8-10: diversified
        num_holdings = diversification
        
        # Sort recommendations based on persona-specific priorities
        if self.profile.persona == 'conservative':
            # Priority: High risk_score (low risk) and high quality_score
            sorted_recs = sorted(
                recommendations, 
                key=lambda x: (x['risk_score'] * 0.6 + x['quality_score'] * 0.4), 
                reverse=True
            )
        elif self.profile.persona == 'aggressive':
            # Priority: High growth_score and high potential
            sorted_recs = sorted(
                recommendations, 
                key=lambda x: (x['growth_score'] * 0.7 + x['overall_score'] * 0.3), 
                reverse=True
            )
        else:  # moderate
            sorted_recs = recommendations
            
        top_recs = sorted_recs[:num_holdings]
        if not top_recs:
            return []
        
        # Calculate base weights from overall scores
        scores = [rec['overall_score'] for rec in top_recs]
        total_score = sum(scores)
        
        # Guard against zero or NaN total_score
        import math
        if total_score <= 0 or math.isnan(total_score) or math.isinf(total_score):
            total_score = 100.0 if not math.isnan(total_score) else 100.0
        
        for rec in top_recs:
            score = rec.get('overall_score', 0)
            if math.isnan(score) or math.isinf(score):
                score = 50.0
            
            # Base weight from score
            weight = score / total_score if total_score > 0 else (1.0 / len(top_recs))
            
            # Apply AGGRESSIVE persona adjustments to weights
            if self.profile.persona == 'conservative':
                # Favor lower volatility (higher risk_score)
                weight *= (1.5 if rec['risk_score'] > 65 else 0.5)
            elif self.profile.persona == 'aggressive':
                # Favor high growth
                weight *= (1.5 if rec['growth_score'] > 65 else 0.5)
            
            allocated_amount = total_amount * weight
            
            if math.isnan(allocated_amount) or math.isinf(allocated_amount):
                allocated_amount = 0.0
            if math.isnan(weight) or math.isinf(weight):
                weight = 0.0
                
            holding = {
                'recommendation': rec,
                'company_name': rec['ipo'].company_name,
                'symbol': getattr(rec['ipo'], 'symbol', rec['ipo'].company_name[:4].upper()),
                'sector': rec['ipo'].sector,
                'allocated_amount': round(float(allocated_amount), 2),
                'weight': round(float(weight), 4),
                'expected_return': rec['growth_score'] / 100,
                'risk_score': rec['risk_score'] / 100,
                'financial_score': rec['financial_score'] / 100,
                'overall_score': rec['overall_score'],
                'rating': rec['rating'],
                'rationale': rec.get('rationale', '')[:100]
            }
            portfolio.append(holding)
        
        # Normalize weights to exactly 1.0
        total_weight = sum(h['weight'] for h in portfolio)
        if total_weight > 0:
            for h in portfolio:
                h['weight'] = round(h['weight'] / total_weight, 4)
                h['allocated_amount'] = round(total_amount * h['weight'], 2)
                
        # Final adjustment to ensure sum matches exactly total_amount
        current_total = sum(h['allocated_amount'] for h in portfolio)
        diff = round(total_amount - current_total, 2)
        if diff != 0 and portfolio:
            portfolio[0]['allocated_amount'] += diff
        
        return portfolio
    
    def _calculate_advanced_metrics(self, portfolio: List[Dict], recommendations: List) -> Dict:
        """Calculate advanced portfolio metrics."""
        if not portfolio:
            return {
                'total_return': 0,
                'portfolio_risk': 0,
                'Sharpe_ratio': 0,
                'diversification_score': 0,
                'VaR_95': 0,
                'max_drawdown': 0,
                'beta': 1.0,
                'alpha': 0
            }
        
        weights = [h['weight'] for h in portfolio]
        returns = [h['expected_return'] for h in portfolio]
        risks = [h['risk_score'] for h in portfolio]
        
        # Portfolio expected return
        portfolio_return = sum(w * r for w, r in zip(weights, returns))
        
        # Portfolio risk (simplified)
        portfolio_risk = sum(w * r for w, r in zip(weights, risks))
        
        # Sharpe Ratio
        Sharpe_ratio = (portfolio_return - self.RISK_FREE_RATE) / max(portfolio_risk, 0.01)
        
        # Diversification Score
        diversification_score = self._calculate_diversification_score(portfolio)
        
        # Value at Risk
        VaR_95 = portfolio_risk * 1.65
        
        # Beta
        beta = 1.0 + (portfolio_risk - 0.5) * 0.5
        
        # Alpha
        alpha = portfolio_return - (self.RISK_FREE_RATE + beta * (0.10 - self.RISK_FREE_RATE))
        
        # Max Drawdown
        max_drawdown = portfolio_risk * 2
        
        return {
            'expected_return': round(portfolio_return * 100, 2),
            'portfolio_risk': round(portfolio_risk * 100, 2),
            'Sharpe_ratio': round(Sharpe_ratio, 2),
            'diversification_score': round(diversification_score, 2),
            'VaR_95': round(VaR_95 * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'beta': round(beta, 2),
            'alpha': round(alpha * 100, 2)
        }
    
    def _calculate_diversification_score(self, portfolio: List[Dict]) -> float:
        """Calculate portfolio diversification score (0-100)."""
        if not portfolio:
            return 0
        
        sectors = set(h['sector'] for h in portfolio)
        sector_score = min(len(sectors) / 3, 1.0) * 50
        
        weights = [h['weight'] for h in portfolio]
        max_weight = max(weights)
        weight_score = (1 - max_weight) * 30
        
        count_score = min(len(portfolio) / 5, 1.0) * 20
        
        return min(sector_score + weight_score + count_score, 100)
    
    def rebalance_portfolio(self, current_portfolio: List[Dict], target_allocations: Dict = None) -> List[Dict]:
        """Calculate rebalancing recommendations."""
        recommendations = []
        
        if target_allocations is None:
            target_allocations = self.strategy.get('target_allocation', {})
        
        current_sectors = {}
        for holding in current_portfolio:
            sector = holding.get('sector', 'Other')
            current_sectors[sector] = current_sectors.get(sector, 0) + holding['weight']
        
        for sector, target in target_allocations.items():
            current = current_sectors.get(sector, 0)
            difference = target/100 - current
            
            if abs(difference) > 0.05:
                action = "Increase" if difference > 0 else "Decrease"
                recommendations.append({
                    'sector': sector,
                    'action': action,
                    'current_allocation': round(current * 100, 1),
                    'target_allocation': target,
                    'adjustment': round(abs(difference) * 100, 1)
                })
        
        return recommendations


def stress_test_portfolio(portfolio: List[Dict], scenarios: Dict) -> Dict:
    """Perform stress testing on portfolio."""
    results = {}
    
    for scenario_name, scenario_data in scenarios.items():
        market_change = scenario_data.get('market_change', 0)
        sector_changes = scenario_data.get('sector_changes', {})
        
        total_impact = 0
        for holding in portfolio:
            impact = market_change
            
            sector = holding.get('sector', 'Other')
            if sector in sector_changes:
                impact += sector_changes[sector]
            
            beta = holding.get('risk_score', 0.5)
            impact *= beta
            
            weighted_impact = impact * holding['weight']
            total_impact += weighted_impact
        
        results[scenario_name] = {
            'portfolio_impact': round(total_impact, 2),
            'loss_percentage': round(total_impact * 100, 2) if total_impact < 0 else 0,
            'recommendation': _get_stress_recommendation(total_impact)
        }
    
    return results


def _get_stress_recommendation(impact: float) -> str:
    """Get recommendation based on stress test impact."""
    if impact < -20:
        return "Consider reducing exposure or hedging"
    elif impact < -10:
        return "Review portfolio allocation"
    elif impact < -5:
        return "Monitor closely"
    else:
        return "Portfolio resilient in this scenario"

