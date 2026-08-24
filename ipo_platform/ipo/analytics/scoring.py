"""Canonical, explainable IPO scoring."""
from dataclasses import dataclass
from math import isfinite

WEIGHTS = {"financial": .20, "growth": .15, "valuation": .15, "risk": .15,
           "quality": .10, "momentum": .10, "esg": .05, "management": .10}

def clamp(value, low=0.0, high=100.0):
    return round(max(low, min(high, float(value))) if isfinite(float(value)) else 50.0, 2)

def _value(obj, name, default=None):
    try:
        value = getattr(obj, name, default)
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default

def _linear(value, low, high, reverse=False):
    if value is None or high == low: return 50.0
    ratio = (value - low) / (high - low)
    return clamp((1 - ratio if reverse else ratio) * 100)

def calculate_financial_score(ipo):
    return clamp(.55 * _linear(_value(ipo, "roe"), -10, 30) + .25 * _linear(_value(ipo, "roa"), -5, 20) + .20 * _linear(_value(ipo, "debt_to_equity"), 0, 3, True))

def calculate_growth_score(ipo): return _linear(_value(ipo, "revenue_growth"), -20, 50)

def calculate_valuation_score(ipo):
    pe = _value(ipo, "pe_ratio")
    return 50.0 if pe is None or pe <= 0 else _linear(pe, 10, 60, True)

def calculate_risk_score(ipo, risk_metrics=None):
    """100 is very low risk; 0 is very high risk."""
    volatility = getattr(risk_metrics, "volatility", None) if risk_metrics else _value(ipo, "volatility")
    beta = getattr(risk_metrics, "beta", None) if risk_metrics else None
    drawdown = getattr(risk_metrics, "max_drawdown", None) if risk_metrics else None
    parts = [_linear(volatility, 5, 80, True), _linear(_value(ipo, "debt_to_equity", 0), 0, 3, True)]
    if beta is not None: parts.append(_linear(beta, .5, 2.5, True))
    if drawdown is not None: parts.append(_linear(abs(drawdown), 0, .8, True))
    return clamp(sum(parts) / len(parts))

def calculate_quality_score(ipo):
    manager = str(getattr(ipo, "lead_manager", "") or "")
    score = 65 if manager and manager.upper() != "N/A" else 50
    if str(getattr(ipo, "listing_at", "") or "").upper() in {"NSE", "BSE"}: score += 10
    if (_value(ipo, "market_cap", 0) or 0) > 1000: score += 15
    return clamp(score)

def calculate_momentum_score(ipo):
    listing, current = _value(ipo, "listing_price"), _value(ipo, "current_price")
    return 50.0 if not listing or not current or listing <= 0 else clamp(50 + max(-40, min(40, (current / listing - 1) * 100)))

def calculate_overall_score(scores):
    return clamp(sum(float(scores.get(key, 50)) * weight for key, weight in WEIGHTS.items()))

@dataclass
class IPOAnalysis:
    financial_score: float; growth_score: float; valuation_score: float; risk_score: float
    quality_score: float; momentum_score: float; esg_score: float; management_score: float
    overall_score: float; strengths: list; weaknesses: list; recommendations: list; percentiles: dict

class IPOScorer:
    WEIGHTS = WEIGHTS
    def __init__(self, ipo, peers=None, risk_metrics=None): self.ipo, self.peers, self.risk_metrics = ipo, list(peers or []), risk_metrics
    def get_all_scores(self):
        scores = {"financial": calculate_financial_score(self.ipo), "growth": calculate_growth_score(self.ipo), "valuation": calculate_valuation_score(self.ipo), "risk": calculate_risk_score(self.ipo, self.risk_metrics), "quality": calculate_quality_score(self.ipo), "momentum": calculate_momentum_score(self.ipo), "esg": clamp(_value(self.ipo, "esg_score", 50)), "management": clamp(_value(self.ipo, "management_quality", 50))}
        return {f"{key}_score": round(value, 1) for key, value in scores.items()} | {"moat_score": clamp(_value(self.ipo, "brand_moat", 50)), "overall_score": round(calculate_overall_score(scores), 1)}
    def calculate_financial_score(self): return calculate_financial_score(self.ipo)
    def calculate_growth_score(self): return calculate_growth_score(self.ipo)
    def calculate_valuation_score(self): return calculate_valuation_score(self.ipo)
    def calculate_risk_score(self): return calculate_risk_score(self.ipo, self.risk_metrics)
    def calculate_quality_score(self): return calculate_quality_score(self.ipo)
    def calculate_momentum_score(self): return calculate_momentum_score(self.ipo)

class AdvancedScorer:
    WEIGHTS = WEIGHTS
    def __init__(self, ipos=None): self.ipos = list(ipos or [])
    def analyze_ipo(self, ipo, peers=None):
        scores = IPOScorer(ipo, peers).get_all_scores()
        labels = {"financial":"financial health","growth":"growth","valuation":"valuation","risk":"risk profile","quality":"quality","momentum":"momentum","esg":"ESG","management":"management"}
        strengths = [label for key, label in labels.items() if scores[f"{key}_score"] >= 70]
        weaknesses = [label for key, label in labels.items() if scores[f"{key}_score"] < 40]
        rating = "BUY" if scores["overall_score"] >= 65 else "SELL" if scores["overall_score"] < 40 else "HOLD"
        return IPOAnalysis(*(scores[f"{key}_score"] for key in labels), scores["overall_score"], strengths, weaknesses, [rating], {})
    def get_rankings(self, metric="overall_score"):
        return sorted(({"ipo": ipo, "analysis": self.analyze_ipo(ipo, self.ipos), "score": getattr(self.analyze_ipo(ipo, self.ipos), metric, 0)} for ipo in self.ipos), key=lambda row: row["score"], reverse=True)
    def get_top_recommendations(self, n=5): return self.get_rankings()[:n]

class PeerComparator:
    def __init__(self, ipos): self.scorer = AdvancedScorer(ipos)
    def get_rankings(self): return self.scorer.get_rankings()
    def compare(self, ipo1, ipo2): return {"ipo1": self.scorer.analyze_ipo(ipo1), "ipo2": self.scorer.analyze_ipo(ipo2)}

def calculate_composite_score(scores, weights=None):
    weights = weights or WEIGHTS; total = sum(weights.get(key, 0) for key in scores)
    return clamp(sum(float(value) * weights.get(key, 0) for key, value in scores.items()) / total) if total else 50.0
