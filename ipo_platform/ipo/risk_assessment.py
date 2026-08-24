"""Historical-return risk analytics with explicit fallbacks."""
from dataclasses import dataclass
from datetime import datetime
import math
import numpy as np
from .analytics.scoring import calculate_risk_score

TRADING_DAYS = 252
RISK_FREE_RATE = 0.05

@dataclass
class RiskMetrics:
    volatility: float; beta: float; Sharpe_ratio: float; Treynor_ratio: float; VaR_95: float; VaR_99: float
    max_drawdown: float; downside_risk: float; sortino_ratio: float; information_ratio: float; tracking_error: float
    correlation_to_market: float

@dataclass
class RiskAssessment:
    symbol: str; overall_risk_score: float; risk_level: str; risk_factors: list; metrics: RiskMetrics
    risk_rating: str; composite_score: float; last_updated: datetime

def _returns(prices):
    values = np.asarray(prices, dtype=float)
    values = values[np.isfinite(values) & (values > 0)]
    return values[1:] / values[:-1] - 1 if len(values) > 1 else np.array([])

class RiskAssessor:
    def __init__(self, market_data_service=None): self.market_data = market_data_service
    def assess_risk(self, ipo, investor_profile=None, prices=None, market_prices=None):
        metrics = self._calculate_metrics(ipo, prices, market_prices)
        score = calculate_risk_score(ipo, metrics)
        level = "Very Low" if score >= 80 else "Low" if score >= 65 else "Moderate" if score >= 45 else "High" if score >= 25 else "Very High"
        factors = self._identify_risk_factors(ipo, metrics)
        return RiskAssessment(getattr(ipo, "symbol", None) or ipo.company_name[:4].upper(), round(score, 1), level, factors, metrics, level, round(score, 2), datetime.now())
    def _calculate_metrics(self, ipo, prices=None, market_prices=None):
        if prices is None: prices = getattr(ipo, "historical_prices", None)
        returns = _returns(prices) if prices is not None else np.array([])
        market_returns = _returns(market_prices) if market_prices else np.array([])
        if len(returns) >= 2:
            vol = float(np.std(returns, ddof=1) * math.sqrt(TRADING_DAYS))
            mean = float(np.mean(returns) * TRADING_DAYS)
            downside = returns[returns < 0]
            downside_dev = float(np.std(downside, ddof=1) * math.sqrt(TRADING_DAYS)) if len(downside) >= 2 else 0.0
            var95, var99 = float(-np.quantile(returns, .05)), float(-np.quantile(returns, .01))
            cumulative = np.cumprod(1 + returns); drawdown = float(np.max(1 - cumulative / np.maximum.accumulate(cumulative)))
            beta, corr = 1.0, 0.0
            if len(market_returns) == len(returns) and np.std(market_returns) > 0:
                beta = float(np.cov(returns, market_returns, ddof=1)[0, 1] / np.var(market_returns, ddof=1)); corr = float(np.corrcoef(returns, market_returns)[0, 1])
            sharpe = (mean - RISK_FREE_RATE) / vol if vol > 0 else 0.0
            sortino = (mean - RISK_FREE_RATE) / downside_dev if downside_dev > 0 else 0.0
            return RiskMetrics(round(vol * 100, 2), round(beta, 3), round(sharpe, 3), round((mean - RISK_FREE_RATE) / beta if beta else 0, 3), round(var95, 5), round(var99, 5), round(drawdown, 5), round(downside_dev, 5), round(sortino, 3), 0.0, round(vol, 5), round(corr, 3))
        # No price history is available in the current schema. Preserve the stored field and label it in factors.
        vol = float(getattr(ipo, "volatility", 25) or 25) / 100
        return RiskMetrics(round(vol * 100, 2), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, vol, 0.0, 0.0, vol, 0.0)
    def _identify_risk_factors(self, ipo, metrics):
        factors = []
        if not getattr(ipo, "historical_prices", None): factors.append({"factor":"Data availability","severity":"Medium","description":"Historical return series unavailable; stored volatility is used as an estimate.","source":"IPO record"})
        if metrics.volatility > 40: factors.append({"factor":"High volatility","severity":"High","description":f"Annualized volatility is {metrics.volatility:.1f}%."})
        debt = float(getattr(ipo, "debt_to_equity", 0) or 0)
        if debt > 2: factors.append({"factor":"High leverage","severity":"High","description":f"Debt-to-equity is {debt:.1f}."})
        if metrics.max_drawdown > .3: factors.append({"factor":"Drawdown","severity":"High","description":f"Maximum drawdown is {metrics.max_drawdown:.1%}."})
        return factors
    def compare_risk(self, ipos):
        ranked = [{"ipo": ipo, "assessment": self.assess_risk(ipo), "risk_score": self.assess_risk(ipo).overall_risk_score} for ipo in ipos]
        ranked.sort(key=lambda row: row["risk_score"], reverse=True)
        return {"ranked_ipos": ranked, "lowest_risk": ranked[:5], "highest_risk": ranked[-5:][::-1]}

class PortfolioRiskAnalyzer:
    def analyze_portfolio_risk(self, holdings, portfolio_value):
        if not holdings: return {"portfolio_volatility": 0, "portfolio_beta": 0, "risk_score": 100, "risk_level":"Very Low", "VaR_95":0, "VaR_99":0, "diversification_score":0}
        weights = np.array([float(h.get("weight", 0)) for h in holdings]); weights = weights / weights.sum() if weights.sum() else np.ones(len(holdings))/len(holdings)
        vols = np.array([float(h.get("volatility", 25))/100 for h in holdings]); betas = np.array([float(h.get("beta", 1)) for h in holdings])
        covariance = np.diag(vols ** 2); variance = float(weights @ covariance @ weights); vol = math.sqrt(max(variance, 0))
        score = max(0, min(100, 100 - vol * 100))
        return {"portfolio_volatility": round(vol*100,2), "portfolio_beta":round(float(weights@betas),2), "risk_score":round(score,1), "risk_level":"Low" if score>=65 else "Moderate" if score>=45 else "High", "VaR_95":round(1.645*vol*portfolio_value,2), "VaR_99":round(2.326*vol*portfolio_value,2), "diversification_score":round((1-max(weights))*100,1)}
    def stress_test_portfolio(self, holdings, scenarios):
        return {name: {"portfolio_impact": round(sum(float(h.get("weight",0))*(scenario.get("market_drop",0)*float(h.get("beta",1))+scenario.get("sector_impacts",{}).get(h.get("sector"),0)) for h in holdings),2)} for name, scenario in scenarios.items()}

def calculate_risk_adjusted_return(recommendation, risk_metrics):
    result = dict(recommendation); result["risk_adjusted_return"] = result.get("overall_score", 50); return result
