"""Investor-personalized recommendations built on the canonical scorer."""
import logging
from .models import IPO, Recommendation, InvestorProfile
from .analytics.scoring import IPOScorer
from .prediction import train_and_predict

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    @staticmethod
    def calculate_risk_rating(ipo, persona):
        limits = {"conservative": (20, .5, "low", 500), "moderate": (35, 1.5, "medium", 200), "aggressive": (50, 3, "high", 50)}
        max_vol, max_debt, level, min_cap = limits.get(persona, limits["moderate"])
        vol = float(ipo.volatility) if ipo.volatility is not None else None
        debt = float(getattr(ipo, "debt_to_equity", 0) or 0)
        cap = float(ipo.market_cap) if ipo.market_cap is not None else None
        reasons, compatible = [], True
        if vol is not None and vol > max_vol: compatible = False; reasons.append(f"volatility {vol:.1f}% exceeds {max_vol:.0f}%")
        if debt > max_debt: compatible = False; reasons.append(f"debt-to-equity {debt:.1f} exceeds {max_debt:.1f}")
        if cap is not None and cap < min_cap: compatible = False; reasons.append(f"market cap below {min_cap:g}")
        return compatible, level, reasons

class IPOScorerCompat(IPOScorer): pass
IPOScorer = IPOScorerCompat

class RecommendationEngine:
    def __init__(self, investor_profile: InvestorProfile, ipos=None):
        self.investor_profile = investor_profile
        self.persona = investor_profile.persona
        self.ipos = list(ipos) if ipos is not None else list(IPO.objects.all())

    def predict_performance(self, ipo):
        result = train_and_predict(self.ipos, ipo)
        return result.prediction

    def score_ipo_for_investor(self, ipo):
        scores = IPOScorer(ipo, self.ipos).get_all_scores()
        compatible, risk_level, reasons = RiskAnalyzer.calculate_risk_rating(ipo, self.persona)
        prediction = self.predict_performance(ipo)
        # Persona changes the decision threshold/fit, not the canonical score.
        fit_adjustment = self._persona_adjustment(scores)
        adjusted = max(0, min(100, scores["overall_score"] + fit_adjustment))
        rating = self._get_recommendation_rating(adjusted)
        positives = [name for name in ("financial", "growth", "valuation", "quality", "momentum", "esg", "management") if scores[f"{name}_score"] >= 70]
        negatives = [name for name in ("financial", "growth", "valuation", "risk", "quality", "momentum") if scores[f"{name}_score"] < 40]
        rationale = f"{rating}: overall score {adjusted:.1f}/100 for {self.persona} profile."
        if positives: rationale += " Positive factors: " + ", ".join(positives) + "."
        if negatives: rationale += " Watch factors: " + ", ".join(negatives) + "."
        if reasons: rationale += " Profile constraints: " + "; ".join(reasons) + "."
        return {"ipo": ipo, "rating": rating, "confidence_score": self._confidence(scores, compatible), "is_compatible": compatible,
                "risk_level": risk_level, "persona_adjustment": fit_adjustment, "rationale": rationale,
                "human_insight": "Recommendation is explained by the component scores and investor constraints.",
                "strategy_fit": round(max(0, min(100, 50 + fit_adjustment)), 1), "predicted_return": prediction,
                "prediction_available": prediction is not None, **scores, "overall_score": round(adjusted, 1),
                "financial_score": scores["financial_score"], "growth_score": scores["growth_score"], "risk_score": scores["risk_score"]}

    def _persona_adjustment(self, scores):
        if self.persona == "conservative": return round((scores["risk_score"] - 50) * .20 + (scores["quality_score"] - 50) * .10, 2)
        if self.persona == "aggressive": return round((scores["growth_score"] - 50) * .20, 2)
        return round((scores["financial_score"] - 50) * .05 + (scores["risk_score"] - 50) * .05, 2)

    @staticmethod
    def _confidence(scores, compatible):
        return round(max(30, min(95, 50 + sum(abs(scores[f"{k}_score"] - 50) for k in ("financial", "growth", "valuation")) / 6 + (10 if compatible else -10))), 1)
    @staticmethod
    def _get_recommendation_rating(score):
        return "STRONG_BUY" if score >= 80 else "BUY" if score >= 65 else "HOLD" if score >= 50 else "SELL" if score >= 35 else "STRONG_SELL"
    def recommend(self, ipo_list=None): return sorted([self.score_ipo_for_investor(ipo) for ipo in (ipo_list or self.ipos)], key=lambda row: row["overall_score"], reverse=True)
    def get_top_recommendations(self, ipos=None, limit=5): return self.recommend(ipos)[:limit]
    def get_filtered_recommendations(self, ipos=None, filters=None):
        filters = filters or {}; rows = self.recommend(ipos)
        return [row for row in rows if row["overall_score"] >= filters.get("min_score", 0) and (not filters.get("only_compatible") or row["is_compatible"]) and (not filters.get("sectors") or row["ipo"].sector in filters["sectors"])]

def create_recommendation(investor_profile, ipo):
    data = RecommendationEngine(investor_profile).score_ipo_for_investor(ipo)
    return Recommendation.objects.update_or_create(investor_profile=investor_profile, ipo=ipo, defaults={k: data[k] for k in ("rating", "confidence_score", "financial_score", "risk_score", "growth_score", "overall_score", "rationale", "human_insight")})[0]

from .portfolio_optimization import PortfolioOptimizer
