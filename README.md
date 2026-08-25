# Quantitative IPO Recommendation & Portfolio Optimization Platform

## Overview

A Django application for explainable IPO scoring, investor-personalized recommendations, historical-return risk analysis, interpretable performance prediction, and constrained long-only portfolio allocation. It is an analytics/demo platform, not investment advice.

## Core Features

- Canonical 0–100 IPO score with component explanations.
- Risk metrics: annualized volatility, beta, Sharpe, Sortino, drawdown, VaR 95/99, and market correlation when price series are supplied.
- Investor profiles: Conservative, Balanced, Growth, and Aggressive.
- Linear regression for post-listing return with a held-out test split and MAE/RMSE/R².
- Equal-weight, score-weighted, minimum-volatility, and maximum-Sharpe portfolio methods.
- Multi-user dashboard, private watchlists, saved portfolio snapshots, and Google sign-in.

## Google OAuth and user accounts

The application uses `django-allauth` with Google’s identity-only `openid`, `email`, and `profile` scopes. Configure a **Web application** OAuth client in Google Cloud and add this authorised redirect URI exactly:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

Create a local `.env` from `.env.example` and provide `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. Never commit either value. OAuth accounts receive an isolated investor profile and are sent to persona onboarding on first sign-in.

Private records are always queried by `request.user`; saved-portfolio detail/delete routes return 404 for another account.

## Architecture

`ipo/analytics/scoring.py` is the single scoring authority. `risk_assessment.py`, `prediction.py`, and `portfolio_optimization.py` contain the quantitative services; views and APIs call `RecommendationEngine` and these services rather than embedding formulas.

## Quantitative Scoring Model

Every component is normalized to 0–100 and the weighted total is 0–100:

| Component | Weight |
|---|---:|
| Financial health | 20% |
| Growth | 15% |
| Valuation | 15% |
| Risk / safety | 15% |
| Quality | 10% |
| Momentum | 10% |
| ESG | 5% |
| Management | 10% |

Risk uses the safety convention: 100 is very low risk and 0 is very high risk.

## Risk Analytics

For a supplied price series, daily return is `P[t] / P[t-1] - 1`; volatility is sample standard deviation annualized by `sqrt(252)`. Sharpe and Sortino use a 5% annual risk-free assumption. VaR is historical 5th/1st percentile loss, and maximum drawdown is peak-to-trough loss. IPOs without historical prices use only stored volatility and explicitly label the fallback.

## ML Prediction

The experimental model uses complete rows containing ROE, ROA, revenue growth, debt/equity, P/E, market cap, and issue size. The target is post-listing return from listing price to current price. Rows with missing features are excluded; fewer than five rows yields no prediction. With enough rows, a `LinearRegression` model is evaluated on a held-out split and exposes MAE, RMSE, and R².

## Portfolio Optimization

Weights are long-only, sum to one, and are capped at 40% per asset. Expected returns come from historical returns when present, otherwise current-vs-listing return or zero when unavailable. Covariance is `w.T @ covariance @ w`; volatility is its square root and Sharpe is `(return - risk_free_rate) / volatility`. Fallbacks are returned in `data_note` and are not historical performance claims.

## Investor Profiles

Conservative selects minimum volatility; Balanced uses maximum Sharpe; Growth uses maximum Sharpe with a looser compatibility filter; Aggressive tolerates more risk and emphasizes growth. Profile constraints are visible in recommendation rationale.

## Tech Stack

Django, Django REST Framework, PostgreSQL in production, SQLite locally, NumPy, SciPy, scikit-learn, WhiteNoise, and Gunicorn.

## Local Setup

```bash
cd ipo_platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py seed_demo_data   # optional; clearly labelled sample data
python manage.py runserver
```

## Environment Variables

Local defaults are available for SQLite development. Production requires `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, and comma-separated `ALLOWED_HOSTS`. Optional integrations use `ALPHA_VANTAGE_API_KEY` and `DEMO_DATA=true` only when sample market responses are intentionally desired.

Google login requires the exact environment variable names `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET`. Local development may load these from the uncommitted
`.env` file. Production settings read them directly from Render's environment;
they are required and production startup fails with a safe configuration error if
either is missing.

## Deployment on Render

Use the included `render.yaml`, or configure:

```bash
pip install -r requirements.txt
python ipo_platform/manage.py migrate --noinput
python ipo_platform/manage.py collectstatic --noinput
gunicorn ipo_platform.wsgi:application --chdir ipo_platform
```

Set `DJANGO_SETTINGS_MODULE=ipo_platform.settings_production`, `SECRET_KEY`,
`DATABASE_URL` from Render PostgreSQL, `DEBUG=false`, `ALLOWED_HOSTS=your-service.onrender.com`,
`GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET`. Do not commit secrets. Add
`https://your-service.onrender.com/accounts/google/login/callback/` to the Google
OAuth client's authorized redirect URIs.

## Limitations

The repository schema does not yet persist daily prices, so historical analytics and covariance optimization require an attached/imported price series; field-based fallbacks are explicitly labelled. The ML model is experimental and its metrics depend on the available listed IPO sample. Demo data is not live market data.
