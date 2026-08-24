"""Small, interpretable IPO performance model.

The target is post-listing return: (current_price / listing_price) - 1.
Rows with missing features are excluded; missing values are never fabricated.
"""
from dataclasses import dataclass, asdict
import logging
import math

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)
FEATURES = ("roe", "roa", "revenue_growth", "debt_to_equity", "pe_ratio", "market_cap", "issue_size")

@dataclass
class PredictionResult:
    prediction: float | None
    available: bool
    experimental: bool
    sample_size: int
    metrics: dict
    message: str

    def as_dict(self): return asdict(self)

def _row(ipo):
    values = []
    for field in FEATURES:
        value = getattr(ipo, field, None)
        if value is None: return None
        try: value = float(value)
        except (TypeError, ValueError): return None
        if not math.isfinite(value): return None
        values.append(value)
    listing, current = getattr(ipo, "listing_price", None), getattr(ipo, "current_price", None)
    if listing is None or current is None or float(listing) <= 0: return None
    return values, (float(current) / float(listing) - 1) * 100

def train_and_predict(ipos, target_ipo=None):
    rows = [row for ipo in ipos if (row := _row(ipo)) is not None]
    if len(rows) < 5:
        return PredictionResult(None, False, True, len(rows), {}, "Experimental: at least 5 complete listed observations are required.")
    x, y = np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
    test_size = max(2, int(round(len(rows) * .2)))
    if test_size >= len(rows): test_size = 1
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=42)
    model = LinearRegression().fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {"mae": round(float(mean_absolute_error(y_test, predictions)), 4), "rmse": round(float(math.sqrt(mean_squared_error(y_test, predictions))), 4), "r2": round(float(r2_score(y_test, predictions)), 4) if len(y_test) > 1 else None}
    target = _row(target_ipo) if target_ipo else None
    prediction = float(model.predict([target[0]])[0]) if target else None
    return PredictionResult(round(prediction, 2) if prediction is not None else None, prediction is not None, False, len(rows), metrics, "Model evaluated on a held-out test split.")
