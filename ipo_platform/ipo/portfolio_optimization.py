"""Long-only portfolio allocation using expected returns and covariance."""
import math
import numpy as np
from scipy.optimize import minimize
from .analytics.scoring import IPOScorer
from .models import IPO

TRADING_DAYS = 252
RISK_FREE_RATE = .05
MAX_ASSET_WEIGHT = .40

def _compatible(ipo, persona):
    limits = {"conservative": (20, .5), "moderate": (35, 1.5), "balanced": (35, 1.5), "growth": (45, 2.5), "aggressive": (60, 3)}
    max_vol, max_debt = limits.get(persona, limits["moderate"])
    volatility = getattr(ipo, "volatility", None)
    debt = float(getattr(ipo, "debt_to_equity", 0) or 0)
    return (volatility is None or float(volatility) <= max_vol) and debt <= max_debt

class PortfolioOptimizer:
    def __init__(self, profile): self.profile = profile
    def optimize_portfolio(self, ipos=None, allocation_amount=None, diversification=5, method=None):
        ipos = list(ipos) if ipos is not None else list(IPO.objects.all())
        recs = [self._recommendation(ipo) for ipo in ipos]
        recs = [rec for rec in recs if rec["is_compatible"] or self.profile.persona == "aggressive"]
        if not recs: return {"success": False, "portfolio": [], "metrics": {}, "error": "No compatible IPOs with sufficient data."}
        recs = sorted(recs, key=lambda r: r["overall_score"], reverse=True)[:max(1, int(diversification))]
        method = method or {"conservative":"min_volatility", "moderate":"max_sharpe", "balanced":"max_sharpe", "growth":"max_sharpe", "aggressive":"max_sharpe"}.get(self.profile.persona, "max_sharpe")
        weights, expected, covariance, data_note = self._optimize(recs, method)
        amount = float(allocation_amount or self.profile.max_investment)
        portfolio = []
        for rec, weight, exp in zip(recs, weights, expected):
            portfolio.append({"company_name": rec["ipo"].company_name, "sector": getattr(rec["ipo"], "sector", "Unknown"), "weight": round(float(weight), 6), "allocated_amount": round(amount*float(weight), 2), "expected_return": round(float(exp)*100, 2), "rating": rec["rating"], "recommendation": rec})
        p_return = float(weights @ expected); variance = float(weights @ covariance @ weights); p_vol = math.sqrt(max(variance,0)); sharpe = (p_return-RISK_FREE_RATE)/p_vol if p_vol else 0
        return {"success": True, "portfolio": portfolio, "strategy": method, "data_note": data_note, "metrics":{"expected_return":round(p_return*100,2),"portfolio_risk":round(p_vol*100,2),"portfolio_volatility":round(p_vol*100,2),"sharpe_ratio":round(sharpe,3),"diversification_score":round((1-max(weights))*100,1)}}
    def _recommendation(self, ipo):
        scores = IPOScorer(ipo).get_all_scores()
        return {**scores, "ipo":ipo, "rating":"BUY" if scores["overall_score"]>=65 else "HOLD", "confidence_score":50, "is_compatible":_compatible(ipo,self.profile.persona), "rationale":"Canonical quantitative score used for portfolio selection."}
    def _series(self, ipo):
        prices = getattr(ipo, "historical_prices", None)
        if prices is not None and len(prices) >= 3:
            values=np.asarray(prices,dtype=float); return values[1:]/values[:-1]-1, True
        listing,current=getattr(ipo,"listing_price",None),getattr(ipo,"current_price",None)
        exp=(float(current)/float(listing)-1) if listing and current and float(listing)>0 else 0.0
        vol=float(getattr(ipo,"volatility",25) or 25)/100
        return np.array([exp]), False
    def _optimize(self,recs,method):
        series=[]; actual=True
        for rec in recs:
            s, is_actual=self._series(rec["ipo"]); series.append(s); actual &= is_actual
        expected=np.array([float(np.mean(s))*TRADING_DAYS if len(s)>1 else float(s[0]) for s in series])
        n=len(recs); covariance=np.diag(np.array([max(float(np.std(s,ddof=1))*math.sqrt(TRADING_DAYS) if len(s)>1 else float(getattr(r["ipo"],"volatility",25) or 25)/100,.0001) for s,r in zip(series,recs)])**2)
        if actual and len(set(map(len,series)))==1 and len(series[0])>1: covariance=np.cov(np.array(series)) * TRADING_DAYS
        covariance=np.nan_to_num(covariance,nan=0,posinf=1,neginf=0); x0=np.ones(n)/n; max_weight=max(MAX_ASSET_WEIGHT, 1/n); bounds=[(0,max_weight)]*n; constraints={"type":"eq","fun":lambda w:np.sum(w)-1}
        if method=="equal_weight": weights=x0
        elif method=="score_weighted": weights=np.array([max(r["overall_score"],0) for r in recs]); weights=weights/weights.sum() if weights.sum() else x0; weights=np.minimum(weights,MAX_ASSET_WEIGHT); weights/=weights.sum()
        else:
            def objective(w):
                variance=float(w@covariance@w)
                return variance if method=="min_volatility" else -((float(w@expected)-RISK_FREE_RATE)/math.sqrt(variance) if variance>0 else 0)
            result=minimize(objective,x0,bounds=bounds,constraints=constraints,method="SLSQP")
            weights=result.x if result.success and abs(sum(result.x)-1)<.001 else x0
        return weights, expected, covariance, "Historical returns used." if actual else "Historical prices unavailable; stored volatility/current-vs-listing fields are explicit fallbacks."
