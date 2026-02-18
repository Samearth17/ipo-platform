# IPO Analytics Platform

## Overview

The IPO Analytics Platform is a Django-based web application built to help investors analyze, track, and optimize IPO investments in a structured and data-driven way.
The platform combines financial analysis, sentiment evaluation, and portfolio optimization techniques inspired by Modern Portfolio Theory (MPT). Instead of simply listing IPOs, it provides risk assessment, scoring, and allocation recommendations tailored to different investor profiles.

## Core Features

### Dashboards
The platform includes multiple dashboards designed to provide clarity and actionable insights:

**Main Dashboard**
Displays an overview of major market indices such as NIFTY 50 and SENSEX, along with curated IPO suggestions based on the user’s selected risk profile.

**Risk Dashboard**
Breaks down portfolio volatility, Value at Risk (VaR), and risk-adjusted performance metrics to help users understand downside exposure.

**Sentiment Dashboard**
Tracks overall market sentiment and public perception of upcoming IPOs using sentiment analysis techniques applied to news and social signals.


### Recommendation System

IPOs are evaluated using a structured scoring model:

* Financial Health – 40%
* Growth Potential – 30%
* Risk Factors – 30%

Each IPO receives a score between 0 and 100. Recommendations are aligned with the selected investor persona:

* Conservative
* Balanced
* Growth
* Aggressive

This ensures that suggestions are not generic but tailored to individual risk preferences.



### Portfolio Optimization

The platform includes a portfolio optimization module that:

* Suggests capital allocation across selected IPOs
* Attempts to maximize expected returns while respecting risk tolerance
* Applies principles inspired by Modern Portfolio Theory

It also supports stress testing scenarios, such as:

* Simulated market crashes (e.g., -20%)
* Sector-specific downturns

This helps users evaluate how resilient their portfolio may be under adverse conditions.



## Technology Stack

* Backend: Django 4.2 (Python)
* Database: SQLite (Development) / PostgreSQL (Production)
* Frontend: Bootstrap 5
* Financial Analysis: NumPy, Pandas
* Market Data: Integrated with NSE/BSE data sources



## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ipo-platform.git
cd ipo-platform
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python3 manage.py migrate
```

5. Populate the database with sample IPO and market data:

```bash
python3 manage.py populate_db
```

6. Run the development server:

```bash
python3 manage.py runserver
```

Access the application at:
http://127.0.0.1:8000


## Project Structure

```
ipo_platform/
├── manage.py
├── ipo_platform/
│   ├── settings.py
│   └── urls.py
└── ipo/
    ├── models.py
    ├── views.py
    ├── risk_assessment.py
    ├── recommendation_engine.py
    ├── portfolio_optimization.py
    └── templates/
```

* `models.py` defines database schemas such as IPO and InvestorProfile.
* `views.py` contains logic for dashboards and data rendering.
* `risk_assessment.py` handles volatility and Value at Risk calculations.
* `recommendation_engine.py` implements IPO scoring logic.
* `portfolio_optimization.py` handles capital allocation using MPT principles.


## Architecture Overview

The platform follows a modular architecture:

**Data Layer**
Responsible for fetching and normalizing raw market and IPO data.

**Intelligence Layer**
Processes financial data, computes risk metrics, generates scores, and performs portfolio optimization.

**Presentation Layer**
Django views render structured and responsive Bootstrap templates for user interaction.

This separation ensures scalability and maintainability.

## Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch and open a Pull Request

