"""
Enhanced Recommendation Engine
Provides sophisticated IPO recommendations with ML-based predictions.
"""

from .models import Recommendation, IPO, InvestorProfile
from decimal import Decimal
import logging
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class IPOScorer:
    """
    Standardizes IPO evaluation metrics across peers.
    """
    
    def __init__(self, ipo, peers: list = None):
        self.ipo = ipo
        self.peers = peers or []
        self._load_ipo_values()
    
    def _load_ipo_values(self):
        """Load and normalize IPO values."""
        self.roe = float(self.ipo.roe) if self.ipo.roe else None
        self.roa = float(self.ipo.roa) if self.ipo.roa else None
        self.volatility = float(self.ipo.volatility) if self.ipo.volatility else None
        self.debt_to_equity = float(getattr(self.ipo, 'debt_to_equity', 0) or 0)
        self.revenue_growth = float(self.ipo.revenue_growth) if self.ipo.revenue_growth else None
        self.market_cap = float(self.ipo.market_cap) if self.ipo.market_cap else None
        self.pe_ratio = float(self.ipo.pe_ratio) if self.ipo.pe_ratio else None
        self.issue_size = float(self.ipo.issue_size) if self.ipo.issue_size else None
        
        # Qualitative traits
        self.esg_score = float(self.ipo.esg_score or 50)
        self.management_quality = float(self.ipo.management_quality or 50)
        self.brand_moat = float(self.ipo.brand_moat or 50)
    
    def get_all_scores(self) -> dict:
        """Calculate all scores for the IPO."""
        financial_score = self._calculate_financial_score()
        risk_score = self._calculate_risk_score()
        growth_score = self._calculate_growth_score()
        valuation_score = self._calculate_valuation_score()
        quality_score = self._calculate_quality_score()
        
        overall_score = (
            financial_score * 0.20 +
            risk_score * 0.10 +
            growth_score * 0.20 +
            valuation_score * 0.15 +
            quality_score * 0.10 +
            self.esg_score * 0.10 +
            self.management_quality * 0.10 +
            self.brand_moat * 0.05
        )
        
        return {
            'financial_score': round(financial_score, 1),
            'risk_score': round(risk_score, 1),
            'growth_score': round(growth_score, 1),
            'valuation_score': round(valuation_score, 1),
            'quality_score': round(quality_score, 1),
            'esg_score': round(self.esg_score, 1),
            'management_score': round(self.management_quality, 1),
            'moat_score': round(self.brand_moat, 1),
            'overall_score': round(overall_score, 1),
        }
    
    def _calculate_financial_score(self) -> float:
        score = 50
        
        # ROE Scoring
        if self.roe is not None:
            # ROE thresholds: >20(+30), >15(+25), >10(+20), >5(+10), >0(+5), else(-10)
            roe_map = [(20, 30), (15, 25), (10, 20), (5, 10), (0, 5)]
            score += next((pt for lim, pt in roe_map if self.roe >= lim), -10)
        else:
            score += 15  # Neutral assumption
        
        if self.roa is not None:
            if self.roa >= 10:
                score += 20
            elif self.roa >= 5:
                score += 15
            elif self.roa >= 2:
                score += 10
            elif self.roa > 0:
                score += 5
            else:
                score -= 5
        else:
            score += 10
        
        if self.debt_to_equity:
            if self.debt_to_equity > 2:
                score -= 15
            elif self.debt_to_equity > 1.5:
                score -= 10
            elif self.debt_to_equity > 1:
                score -= 5
            elif self.debt_to_equity > 0.5:
                score -= 2
        
        return min(100, max(0, score))
    
    def _calculate_risk_score(self) -> float:
        score = 50
        if self.volatility is not None:
            if self.volatility >= 50:
                score += 30
            elif self.volatility >= 35:
                score += 20
            elif self.volatility >= 25:
                score += 10
            elif self.volatility >= 15:
                score += 5
            else:
                score -= 10
        else:
            score += 10
        
        if self.debt_to_equity:
            if self.debt_to_equity > 2:
                score += 20
            elif self.debt_to_equity > 1.5:
                score += 15
            elif self.debt_to_equity > 1:
                score += 10
            elif self.debt_to_equity > 0.5:
                score += 5
        
        if self.market_cap:
            if self.market_cap < 50: # 50 Cr
                score += 15
            elif self.market_cap < 200: # 200 Cr
                score += 10
            elif self.market_cap < 500: # 500 Cr
                score += 5
        
        return min(100, max(0, score))
    
    def _calculate_growth_score(self) -> float:
        score = 50
        if self.revenue_growth is not None:
            if self.revenue_growth >= 30:
                score += 30
            elif self.revenue_growth >= 20:
                score += 25
            elif self.revenue_growth >= 15:
                score += 20
            elif self.revenue_growth >= 10:
                score += 15
            elif self.revenue_growth >= 5:
                score += 10
            elif self.revenue_growth > 0:
                score += 5
            else:
                score -= 15
        else:
            score += 15
        
        if self.market_cap:
            if self.market_cap > 1000: # 1000 Cr
                score += 15
            elif self.market_cap > 500: # 500 Cr
                score += 10
            elif self.market_cap > 200: # 200 Cr
                score += 5
        
        return min(100, max(0, score))
    
    def _calculate_valuation_score(self) -> float:
        score = 50
        if self.pe_ratio is not None:
            if self.pe_ratio < 15:
                score += 30
            elif self.pe_ratio < 20:
                score += 25
            elif self.pe_ratio < 25:
                score += 20
            elif self.pe_ratio < 30:
                score += 15
            elif self.pe_ratio < 40:
                score += 5
            else:
                score -= 10
        else:
            score += 15
        
        if self.issue_size:
            if 50 <= self.issue_size <= 500: # 50 Cr to 500 Cr
                score += 15
            elif 10 <= self.issue_size <= 1000: # 10 Cr to 1000 Cr
                score += 10
            elif self.issue_size > 0:
                score += 5
        
        return min(100, max(0, score))
    
    def _calculate_quality_score(self) -> float:
        score = 50
        lead_manager = getattr(self.ipo, 'lead_manager', '') or ''
        quality_managers = ['Goldman Sachs', 'Morgan Stanley', 'JP Morgan', 'Citi', 
                           'Axis Capital', 'ICICI Securities', 'HDFC Bank']
        if any(qm.lower() in lead_manager.lower() for qm in quality_managers):
            score += 20
        elif lead_manager and lead_manager != 'N/A':
            score += 10
        
        listing_at = getattr(self.ipo, 'listing_at', 'NSE') or 'NSE'
        if listing_at in ['NSE', 'BSE']:
            score += 10
        
        if self.market_cap and self.market_cap > 1000: # 1000 Cr
            score += 10
        
        return min(100, max(0, score))


class RiskAnalyzer:
    @staticmethod
    def calculate_risk_rating(ipo, persona: str) -> Tuple[bool, str, list]:
        risk_reasons = []
        volatility = float(ipo.volatility) if ipo.volatility else 25
        debt_to_equity = float(getattr(ipo, 'debt_to_equity', 0) or 0)
        # Market cap is already in Crores
        market_cap = float(ipo.market_cap) if ipo.market_cap else 100
        
        if persona == 'conservative':
            max_volatility = 20
            max_debt = 0.5
            min_market_cap = 500 # 500 Cr
            risk_level = 'low'
        elif persona == 'moderate':
            max_volatility = 35
            max_debt = 1.5
            min_market_cap = 200 # 200 Cr
            risk_level = 'medium'
        else:
            max_volatility = 50
            max_debt = 3.0
            min_market_cap = 50 # 50 Cr
            risk_level = 'high'
        
        is_compatible = True
        
        if volatility > max_volatility:
            is_compatible = False
            risk_reasons.append(f"High volatility ({volatility:.1f}%)")
        
        if debt_to_equity > max_debt:
            is_compatible = False
            risk_reasons.append(f"High debt-to-equity ({debt_to_equity:.1f})")
        
        if market_cap < min_market_cap:
            is_compatible = False
            risk_reasons.append(f"Small market cap (₹{market_cap/10000000:.0f}Cr)")
        
        return is_compatible, risk_level, risk_reasons


class RecommendationEngine:
    _model = None
    _scaler = None
    _is_trained = False
    
    def __init__(self, investor_profile: InvestorProfile, ipos: list = None):
        self.investor_profile = investor_profile
        self.risk_params = investor_profile.get_risk_parameters()
        self.strategy = investor_profile.get_persona_strategy()
        self.persona = investor_profile.persona
        self.ipos = ipos or list(IPO.objects.all())
        
        if not RecommendationEngine._is_trained:
            self._train_model()
    
    def _train_model(self):
        """Train simple ML model using basic statistics."""
        try:
            training_data = []
            
            for ipo in self.ipos:
                if ipo.status == 'LISTED':
                    if ipo.listing_price and ipo.current_price:
                        performance = (float(ipo.current_price) - float(ipo.listing_price)) / float(ipo.listing_price) * 100
                        
                        training_data.append({
                            'roe': float(ipo.roe) if ipo.roe else 10,
                            'roa': float(ipo.roa) if ipo.roa else 5,
                            'volatility': float(ipo.volatility) if ipo.volatility else 25,
                            'debt_to_equity': float(getattr(ipo, 'debt_to_equity', 0) or 1),
                            'revenue_growth': float(ipo.revenue_growth) if ipo.revenue_growth else 15,
                            'market_cap': float(ipo.market_cap) if ipo.market_cap else 1000000000,
                            'pe_ratio': float(ipo.pe_ratio) if ipo.pe_ratio else 20,
                            'issue_size': float(ipo.issue_size) if ipo.issue_size else 1000000000,
                            'performance': performance
                        })
            
            if len(training_data) >= 10:
                # Simple linear regression using basic math
                n = len(training_data)
                sum_x = sum(d['roe'] + d['revenue_growth'] for d in training_data)
                sum_y = sum(d['performance'] for d in training_data)
                sum_xy = sum(d['roe'] * d['performance'] + d['revenue_growth'] * d['performance'] for d in training_data)
                sum_x2 = sum((d['roe'] + d['revenue_growth'])**2 for d in training_data)
                
                if n * sum_x2 != sum_x**2:
                    RecommendationEngine._slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
                    RecommendationEngine._intercept = (sum_y - RecommendationEngine._slope * sum_x) / n
                else:
                    RecommendationEngine._slope = 0.5
                    RecommendationEngine._intercept = 10
                
                RecommendationEngine._is_trained = True
                logger.info("Simple ML Model trained successfully")
            else:
                logger.warning("Insufficient training data for ML model")
                RecommendationEngine._slope = 0.5
                RecommendationEngine._intercept = 10
                RecommendationEngine._is_trained = True
                
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            RecommendationEngine._slope = 0.5
            RecommendationEngine._intercept = 10
            RecommendationEngine._is_trained = True
    
    def predict_performance(self, ipo) -> float:
        """Predict IPO performance using trained model."""
        if not RecommendationEngine._is_trained:
            scorer = EnhancedIPOScorer(ipo)
            scores = scorer.get_all_scores()
            return scores['overall_score'] * 0.8
        
        try:
            roe = float(ipo.roe) if ipo.roe else 10
            revenue_growth = float(ipo.revenue_growth) if ipo.revenue_growth else 15
            
            prediction = RecommendationEngine._slope * (roe + revenue_growth) + RecommendationEngine._intercept
            return max(-50, min(100, prediction))
            
        except Exception as e:
            logger.error(f"Error predicting performance: {e}")
            return 50.0
    
    def score_ipo_for_investor(self, ipo) -> dict:
        """Score an IPO for the specific investor."""
        scorer = IPOScorer(ipo, self.ipos)
        scores = scorer.get_all_scores()
        
        is_compatible, risk_level, risk_reasons = RiskAnalyzer.calculate_risk_rating(
            ipo, self.persona
        )
        
        predicted_performance = self.predict_performance(ipo)
        persona_adjustment = self._calculate_persona_adjustment(ipo, scores)
        
        adjusted_score = scores['overall_score']
        
        if not is_compatible:
            adjusted_score *= 0.7
        
        adjusted_score = adjusted_score * (1 + (persona_adjustment / 100))
        adjusted_score = (adjusted_score * 0.7) + (predicted_performance * 0.3)
        adjusted_score = min(100, max(0, adjusted_score))
        
        rating = self._get_recommendation_rating(adjusted_score)
        rationale = self._generate_rationale(ipo, scores, risk_reasons, is_compatible, predicted_performance)
        strategy_fit = self._evaluate_strategy_fit(ipo, scores)
        
        return {
            'ipo': ipo,
            'rating': rating,
            'confidence_score': self._calculate_confidence(scores, is_compatible, risk_level),
            'financial_score': scores['financial_score'],
            'risk_score': scores['risk_score'],
            'growth_score': scores['growth_score'],
            'valuation_score': scores['valuation_score'],
            'quality_score': scores['quality_score'],
            'overall_score': round(adjusted_score, 1),
            'is_compatible': is_compatible,
            'risk_level': risk_level,
            'persona_adjustment': persona_adjustment,
            'rationale': rationale,
            'human_insight': self._generate_human_insight(ipo, scores),
            'strategy_fit': strategy_fit,
            'predicted_return': round(predicted_performance, 1)
        }
    
    def _calculate_persona_adjustment(self, ipo, scores: dict) -> float:
        adjustment = 0
        volatility = float(ipo.volatility) if ipo.volatility else 25
        
        if self.persona == 'conservative':
            # Conservative: Heavier penalty for volatility and low quality
            if volatility > 20:
                adjustment -= min(25, (volatility - 20) * 1.5)
            if scores['quality_score'] < 60:
                adjustment -= 15
            if scores['risk_score'] < 50:
                adjustment -= 10
                
        elif self.persona == 'moderate':
            if scores['quality_score'] > 65:
                adjustment += 10
            if scores['financial_score'] > 65:
                adjustment += 10
            if volatility > 30:
                adjustment -= 10
                
        elif self.persona == 'aggressive':
            # Aggressive: Reward growth and high scores, tolerate volatility
            if scores['growth_score'] > 60:
                adjustment += 20
            if scores['quality_score'] > 65:
                adjustment += 10
            if scores['risk_score'] > 60:
                adjustment += 15
        
        return adjustment
    
    def _calculate_confidence(self, scores: dict, is_compatible: bool, risk_level: str) -> float:
        confidence = 70
        if scores['financial_score'] != 50:
            confidence += 10
        if scores['growth_score'] != 50:
            confidence += 10
        if scores['valuation_score'] != 50:
            confidence += 5
        
        if is_compatible:
            confidence += 5
        else:
            confidence -= 10
        
        return min(95, max(30, confidence))
    
    def _get_recommendation_rating(self, score: float) -> str:
        if score >= 80:
            return 'STRONG_BUY'
        elif score >= 65:
            return 'BUY'
        elif score >= 50:
            return 'HOLD'
        elif score >= 35:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    def _generate_rationale(self, ipo, scores: dict, risk_reasons: list, is_compatible: bool, predicted_performance: float) -> str:
        rationale = []
        
        if scores['financial_score'] >= 70:
            rationale.append(f"Strong financial health with ROE {ipo.roe}%" if ipo.roe else "Strong financial health")
        elif scores['financial_score'] < 40:
            rationale.append("Weak financial metrics - caution advised")
        else:
            rationale.append("Moderate financial health")
        
        if scores['growth_score'] >= 70:
            rationale.append("High growth potential")
        elif scores['growth_score'] < 40:
            rationale.append("Limited growth visibility")
        
        if not is_compatible:
            rationale.append(f"Not ideal for {self.persona} investors due to: {'; '.join(risk_reasons)}")
        else:
            rationale.append(f"Suitable risk profile for {self.persona} investors")
        
        rationale.append(f"Expected listing performance: {predicted_performance:.1f}%")
        
        return " | ".join(rationale)
    
    def _generate_human_insight(self, ipo, scores: dict) -> str:
        """Generates a more personal, human-like insight."""
        insights = []
        
        # Management insight
        mq = scores['management_score']
        if mq > 75:
            insights.append(f"The leadership team at {ipo.company_name} is exceptionally strong, bringing a level of seasoned experience that's rare in this sector.")
        elif mq < 40:
            insights.append(f"I have some reservations about the current management depth; they'll need to prove their execution capabilities post-listing.")
            
        # Moat insight
        moat = scores['moat_score']
        if moat > 70:
            insights.append("They've built a significant competitive 'moat' around their brand, which should protect margins in the long run.")
            
        # ESG insight
        esg = scores['esg_score']
        if esg > 80:
            insights.append("From an ethical standpoint, their high ESG score makes them a standout for conscious investors.")
        elif esg < 30:
            insights.append("Investors prioritizing environmental or social governance might find their current practices a bit concerning.")
            
        if not insights:
            insights.append(f"{ipo.company_name} presents a straightforward business case, though it doesn't quite have a 'signature' outlier trait yet.")
            
        return " ".join(insights)
    
    def _evaluate_strategy_fit(self, ipo, scores: dict) -> int:
        fit_score = 50
        
        sector_weights = self.strategy.get('sector_weights', {})
        if ipo.sector in sector_weights:
            fit_score += 20
        
        issue_size = float(ipo.issue_size) if ipo.issue_size else 0
        if self.investor_profile.min_investment <= issue_size <= self.investor_profile.max_investment:
            fit_score += 15
        
        if self.persona == 'conservative' and scores['quality_score'] >= 60:
            fit_score += 10
        elif self.persona == 'aggressive' and scores['growth_score'] >= 60:
            fit_score += 10
        
        return min(100, fit_score)
    
    def recommend(self, ipo_list: list = None) -> list:
        ipos = ipo_list or self.ipos
        recommendations = []
        for ipo in ipos:
            recommendation = self.score_ipo_for_investor(ipo)
            recommendations.append(recommendation)
        return sorted(recommendations, key=lambda x: x['overall_score'], reverse=True)
    
    def get_top_recommendations(self, ipos: list = None, limit: int = 5) -> list:
        recommendations = self.recommend(ipos)
        return recommendations[:limit]
    
    def get_filtered_recommendations(self, ipos: list = None, filters: dict = None) -> list:
        if filters is None:
            filters = {}
        
        recommendations = self.recommend(ipos)
        
        min_score = filters.get('min_score', 0)
        max_volatility = filters.get('max_volatility', 100)
        sectors = filters.get('sectors', [])
        only_compatible = filters.get('only_compatible', False)
        
        filtered = []
        for rec in recommendations:
            ipo = rec['ipo']
            
            if rec['overall_score'] < min_score:
                continue
            
            if float(ipo.volatility or 0) > max_volatility:
                continue
            
            if sectors and ipo.sector not in sectors:
                continue
            
            if only_compatible and not rec['is_compatible']:
                continue
            
            filtered.append(rec)
        
        return filtered


# PortfolioOptimizer is now imported from .portfolio_optimization
from .portfolio_optimization import PortfolioOptimizer


def create_recommendation(investor_profile: InvestorProfile, ipo: IPO) -> Recommendation:
    engine = RecommendationEngine(investor_profile)
    rec_data = engine.score_ipo_for_investor(ipo)
    
    recommendation, created = Recommendation.objects.update_or_create(
        investor_profile=investor_profile,
        ipo=ipo,
        defaults={
            'rating': rec_data['rating'],
            'confidence_score': rec_data['confidence_score'],
            'financial_score': rec_data['financial_score'],
            'risk_score': rec_data['risk_score'],
            'growth_score': rec_data['growth_score'],
            'overall_score': rec_data['overall_score'],
            'rationale': rec_data['rationale'],
            'human_insight': rec_data.get('human_insight', '')
        }
    )
    
    return recommendation

