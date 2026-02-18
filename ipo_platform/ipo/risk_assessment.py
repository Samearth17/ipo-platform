"""
Risk Assessment Module
Comprehensive risk analysis and assessment for IPO investments.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics for an IPO."""
    volatility: float
    beta: float
    Sharpe_ratio: float
    Treynor_ratio: float
    VaR_95: float
    VaR_99: float
    max_drawdown: float
    downside_risk: float
    sortino_ratio: float
    information_ratio: float
    tracking_error: float
    correlation_to_market: float


@dataclass
class RiskAssessment:
    """Complete risk assessment result."""
    symbol: str
    overall_risk_score: float
    risk_level: str
    risk_factors: List[Dict]
    metrics: RiskMetrics
    risk_rating: str
    composite_score: float
    last_updated: datetime


class RiskAssessor:
    """Comprehensive risk assessment for IPOs."""
    
    RISK_WEIGHTS = {
        'volatility': 0.20,
        'beta': 0.15,
        'debt_to_equity': 0.15,
        'liquidity': 0.10,
        'market_correlation': 0.10,
        'downside_risk': 0.15,
        'concentration': 0.15
    }
    
    SECTOR_RISK_ADJUSTMENTS = {
        'Technology': 1.1,
        'Healthcare': 1.0,
        'Finance': 0.9,
        'Energy': 1.2,
        'Consumer': 0.95,
        'Industrial': 1.0,
        'Real Estate': 1.1,
        'Materials': 1.15,
        'Utilities': 0.8,
        'Communication': 1.0
    }
    
    def __init__(self, market_data_service=None):
        self.market_data = market_data_service
    
    def assess_risk(self, ipo, investor_profile=None) -> RiskAssessment:
        """Perform comprehensive risk assessment for an IPO."""
        risk_factors = self._identify_risk_factors(ipo)
        metrics = self._calculate_metrics(ipo)
        overall_score = self._calculate_composite_risk_score(ipo, metrics, risk_factors)
        risk_level = self._get_risk_level(overall_score)
        risk_rating = self._get_risk_rating(overall_score, ipo)
        
        return RiskAssessment(
            symbol=getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
            overall_risk_score=round(overall_score, 1),
            risk_level=risk_level,
            risk_factors=risk_factors,
            metrics=metrics,
            risk_rating=risk_rating,
            composite_score=round(overall_score, 2),
            last_updated=datetime.now()
        )
    
    def _identify_risk_factors(self, ipo) -> List[Dict]:
        factors = []
        
        volatility = float(ipo.volatility) if ipo.volatility else None
        if volatility:
            if volatility > 40:
                factors.append({
                    'factor': 'High Volatility',
                    'severity': 'High',
                    'description': f'Historical volatility of {volatility}% indicates significant price swings',
                    'impact': 'Price may fluctuate significantly',
                    'mitigation': 'Consider dollar-cost averaging'
                })
            elif volatility > 25:
                factors.append({
                    'factor': 'Moderate Volatility',
                    'severity': 'Medium',
                    'description': f'Volatility of {volatility}% is above average',
                    'impact': 'Moderate price fluctuations expected',
                    'mitigation': 'Set appropriate stop-loss levels'
                })
        
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        if debt_to_equity > 2:
            factors.append({
                'factor': 'High Leverage',
                'severity': 'High',
                'description': f'Debt-to-Equity ratio of {debt_to_equity} indicates high financial leverage',
                'impact': 'Higher fixed obligations and bankruptcy risk',
                'mitigation': 'Prefer companies with lower debt'
            })
        elif debt_to_equity > 1:
            factors.append({
                'factor': 'Moderate Leverage',
                'severity': 'Medium',
                'description': f'Debt-to-Equity ratio of {debt_to_equity} is moderate',
                'impact': 'Some debt burden present',
                'mitigation': 'Monitor debt levels over time'
            })
        
        market_cap = float(ipo.market_cap) if ipo.market_cap else None
        if market_cap and market_cap < 500000000:
            factors.append({
                'factor': 'Small Cap',
                'severity': 'High',
                'description': 'Small market capitalization indicates limited resources',
                'impact': 'Higher risk of failure, less liquidity',
                'mitigation': 'Diversify across multiple small caps'
            })
        
        sector = getattr(ipo, 'sector', None)
        if sector and sector in self.SECTOR_RISK_ADJUSTMENTS:
            adjustment = self.SECTOR_RISK_ADJUSTMENTS[sector]
            if adjustment > 1.0:
                factors.append({
                    'factor': f'{sector} Sector Risk',
                    'severity': 'Medium' if adjustment < 1.15 else 'High',
                    'description': f'{sector} sector has elevated risk characteristics',
                    'impact': 'Sector-specific challenges present',
                    'mitigation': 'Consider sector diversification'
                })
        
        return factors
    
    def _calculate_metrics(self, ipo) -> RiskMetrics:
        volatility = float(getattr(ipo, 'volatility', 30) or 30)
        market_cap = float(getattr(ipo, 'market_cap', 1000000000) or 1000000000)
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 1) or 1)
        roe = float(getattr(ipo, 'roe', 10) or 10)
        revenue_growth = float(getattr(ipo, 'revenue_growth', 15) or 15)
        
        beta = volatility / 20
        
        expected_return = revenue_growth / 100
        risk_free_rate = 0.05
        Sharpe_ratio = (expected_return - risk_free_rate) / max(volatility / 100, 0.01)
        
        market_return = 0.10
        Treynor_ratio = (expected_return - risk_free_rate) / max(beta, 0.01)
        
        VaR_95 = volatility * 1.65 / 100
        VaR_99 = volatility * 2.33 / 100
        
        max_drawdown = volatility * 2 / 100
        
        downside_risk = volatility * 0.8 / 100
        
        Sortino_ratio = (expected_return - risk_free_rate) / max(downside_risk, 0.01)
        
        information_ratio = (expected_return - market_return) / max(volatility / 100, 0.01)
        
        tracking_error = volatility * 0.5 / 100
        
        correlation_to_market = min(0.95, 0.5 + (volatility / 100) * 0.5)
        
        return RiskMetrics(
            volatility=round(volatility, 2),
            beta=round(beta, 2),
            Sharpe_ratio=round(Sharpe_ratio, 2),
            Treynor_ratio=round(Treynor_ratio, 2),
            VaR_95=round(VaR_95, 4),
            VaR_99=round(VaR_99, 4),
            max_drawdown=round(max_drawdown, 4),
            downside_risk=round(downside_risk, 4),
            sortino_ratio=round(Sortino_ratio, 2),
            information_ratio=round(information_ratio, 2),
            tracking_error=round(tracking_error, 4),
            correlation_to_market=round(correlation_to_market, 2)
        )
    
    def _calculate_composite_risk_score(self, ipo, metrics: RiskMetrics, factors: List[Dict]) -> float:
        score = 0
        
        score += min(20, metrics.volatility * 0.5)
        
        score += min(15, metrics.beta * 10)
        
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        score += min(15, debt_to_equity * 5)
        
        market_cap = float(getattr(ipo, 'market_cap', 1000000000) or 1000000000)
        if market_cap < 500000000:
            score += 10
        elif market_cap < 2000000000:
            score += 5
        
        score += min(15, metrics.downside_risk * 100)
        
        high_risk_factors = sum(1 for f in factors if f['severity'] == 'High')
        medium_risk_factors = sum(1 for f in factors if f['severity'] == 'Medium')
        score += min(25, high_risk_factors * 10 + medium_risk_factors * 5)
        
        return min(100, score)
    
    def _get_risk_level(self, score: float) -> str:
        if score < 25:
            return 'Low'
        elif score < 45:
            return 'Medium'
        elif score < 65:
            return 'High'
        else:
            return 'Very High'
    
    def _get_risk_rating(self, score: float, ipo) -> str:
        market_cap = float(getattr(ipo, 'market_cap', 0) or 0)
        
        if score < 20:
            base_rating = 'AAA'
        elif score < 30:
            base_rating = 'AA'
        elif score < 40:
            base_rating = 'A'
        elif score < 50:
            base_rating = 'BBB'
        elif score < 60:
            base_rating = 'BB'
        elif score < 75:
            base_rating = 'B'
        else:
            base_rating = 'CCC'
        
        if market_cap > 10000000000 and score > 40:
            base_rating = base_rating.replace('B', 'A').replace('C', 'B')
        
        return base_rating
    
    def compare_risk(self, ipos: List) -> Dict:
        comparisons = []
        for ipo in ipos:
            assessment = self.assess_risk(ipo)
            comparisons.append({
                'symbol': getattr(ipo, 'symbol', ipo.company_name),
                'company_name': ipo.company_name,
                'risk_score': assessment.overall_risk_score,
                'risk_level': assessment.risk_level,
                'risk_rating': assessment.risk_rating,
                'volatility': assessment.metrics.volatility,
                'beta': assessment.metrics.beta
            })
        
        comparisons.sort(key=lambda x: x['risk_score'])
        
        return {
            'ranked_ipos': comparisons,
            'lowest_risk': comparisons[0] if comparisons else None,
            'highest_risk': comparisons[-1] if comparisons else None
        }


class PortfolioRiskAnalyzer:
    def __init__(self):
        self.risk_assessor = RiskAssessor()
    
    def analyze_portfolio_risk(self, holdings: List, portfolio_value: float) -> Dict:
        if not holdings:
            return {'error': 'No holdings provided'}
        
        weights = [h.get('weight', 0) for h in holdings]
        volatilities = [h.get('volatility', 30) for h in holdings]
        betas = [h.get('beta', 1.5) for h in holdings]
        
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        portfolio_volatility = sum(w * v for w, v in zip(weights, volatilities))
        portfolio_beta = sum(w * b for w, b in zip(weights, betas))
        
        sector_weights = {}
        for h in holdings:
            sector = h.get('sector', 'Other')
            sector_weights[sector] = sector_weights.get(sector, 0) + h.get('weight', 0)
        
        max_concentration = max(sector_weights.values()) if sector_weights else 1
        
        risk_score = (
            portfolio_volatility * 0.3 +
            portfolio_beta * 10 * 0.2 +
            max_concentration * 100 * 0.2 +
            (len(holdings) < 3 and 20 or 0)
        )
        risk_score = min(100, risk_score)
        
        portfolio_VaR_95 = portfolio_volatility * 1.65 / 100 * portfolio_value
        portfolio_VaR_99 = portfolio_volatility * 2.33 / 100 * portfolio_value
        
        return {
            'portfolio_volatility': round(portfolio_volatility, 2),
            'portfolio_beta': round(portfolio_beta, 2),
            'risk_score': round(risk_score, 1),
            'risk_level': self._risk_level_from_score(risk_score),
            'VaR_95': round(portfolio_VaR_95, 2),
            'VaR_99': round(portfolio_VaR_99, 2),
            'max_concentration': round(max_concentration * 100, 1),
            'sector_allocation': sector_weights,
            'diversification_score': round((1 - max_concentration) * 100, 1),
            'num_holdings': len(holdings)
        }
    
    def _risk_level_from_score(self, score: float) -> str:
        if score < 30:
            return 'Low'
        elif score < 50:
            return 'Medium'
        elif score < 70:
            return 'High'
        else:
            return 'Very High'
    
    def stress_test_portfolio(self, holdings: List, scenarios: Dict) -> Dict:
        results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            market_drop = scenario_params.get('market_drop', 0)
            
            portfolio_impact = 0
            for h in holdings:
                beta = h.get('beta', 1.0)
                weight = h.get('weight', 0)
                sector_impact = scenario_params.get('sector_impacts', {}).get(h.get('sector', ''), 0)
                
                impact = (market_drop * beta) + sector_impact
                portfolio_impact += impact * weight
            
            results[scenario_name] = {
                'portfolio_impact': round(portfolio_impact, 2),
                'loss_percentage': round(abs(portfolio_impact) * 100, 2),
                'recommendation': self._get_stress_recommendation(portfolio_impact)
            }
        
        return results
    
    def _get_stress_recommendation(self, impact: float) -> str:
        if impact < -25:
            return "Significant risk - Consider reducing exposure"
        elif impact < -15:
            return "Elevated risk - Review allocation"
        elif impact < -10:
            return "Moderate impact - Monitor closely"
        else:
            return "Portfolio shows resilience in this scenario"


def calculate_risk_adjusted_return(recommendation: Dict, risk_metrics: RiskMetrics) -> Dict:
    risk_penalty = risk_metrics.volatility * 0.1 + risk_metrics.beta * 5
    risk_bonus = risk_metrics.Sharpe_ratio * 10 + risk_metrics.Sortino_ratio * 5
    
    adjusted_score = recommendation.get('overall_score', 50) - risk_penalty + risk_bonus
    adjusted_score = min(100, max(0, adjusted_score))
    
    return {
        **recommendation,
        'overall_score': round(adjusted_score, 1),
        'volatility': risk_metrics.volatility,
        'beta': risk_metrics.beta,
        'Sharpe_ratio': risk_metrics.Sharpe_ratio,
        'VaR_95': round(risk_metrics.VaR_95 * 100, 2),
        'risk_adjusted_return': round(adjusted_score, 1)
    }

