# AI-Powered IPO Analytics Platform

## 🚀 Overview
The **IPO Analytics Platform** is a sophisticated Django-based web application designed to help investors analyze, track, and optimize their IPO investments. By leveraging real-time market data, sentiment analysis, and Modern Portfolio Theory (MPT), the platform provides actionable insights and personalized portfolio recommendations.

## ✨ Key Features

### 1. Intelligent Dashboards
-   **Main Dashboard:** Real-time overview of market indices (NIFTY 50, SENSEX) and AI-curated "Top Picks" based on your risk profile.
-   **Risk Dashboard:** Detailed breakdown of portfolio volatility, Value at Risk (VaR), and risk-adjusted return metrics.
-   **Sentiment Dashboard:** Tracks market mood and social media trends for upcoming IPOs using sentiment analysis.

### 2. AI-Driven Recommendations
-   **Personalized Scoring:** IPOs are scored (0-100) based on Financial Health (40%), Growth Potential (30%), and Risk Factors (30%).
-   **Weighted Matching:** Recommendations are tailored to your specific **Investor Persona** (Conservative, Balanced, Growth, Aggressive).

### 3. Portfolio Optimization
-   **Smart Allocation:** Uses an optimization algorithm to suggest the ideal capital allocation across multiple IPOs to maximize returns while adhering to your risk tolerance.
-   **Stress Testing:** Simulates market crashes (-20%) and sector-specific downturns to test portfolio resilience.

## 🛠️ Tech Stack
-   **Backend:** Django 4.2 (Python)
-   **Database:** SQLite (Development) / PostgreSQL (Production ready)
-   **Frontend:** Bootstrap 5 (Responsive, "System UI" Design)
-   **Analysis:** NumPy, Pandas (Financial modeling)
-   **Data:** Integration with NSE/BSE data sources

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/ipo-platform.git
    cd ipo-platform
    ```

2.  **Create Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations**
    ```bash
    python3 manage.py migrate
    ```

5.  **Initialize Data**
    Populate the database with sample IPOs and market data:
    ```bash
    python3 manage.py populate_db
    ```

6.  **Run Server**
    ```bash
    python3 manage.py runserver
    ```
    Access the app at `http://127.0.0.1:8000`.

## 📂 Project Structure
```
ipo_platform/
├── manage.py              # Django CLI entry point
├── ipo_platform/          # Project settings
│   ├── settings.py
│   └── urls.py
└── ipo/                   # Main application
    ├── models.py          # Database Schema (IPO, InvestorProfile)
    ├── views.py           # Logic for Dashboards & Analysis
    ├── risk_assessment.py # Volatility & VaR logic
    ├── recommendation_engine.py # Scoring algorithms
    ├── portfolio_optimization.py # MPT Allocation logic
    └── templates/         # HTML/Bootstrap UI
```

## 🛡️ Architecture
The system follows a modular architecture:
1.  **Data Ingestion Layer:** `MarketDataService` fetches and normalizes raw market data.
2.  **Intelligence Layer:** `RiskAssessor` and `RecommendationEngine` process this data to generate derived metrics (Risk Scores, Sentiment).
3.  **Presentation Layer:** Django Views rendering clean, responsive Bootstrap templates.

## 🤝 Contributing
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/NewFeature`).
3.  Commit your changes.
4.  Push to the branch and open a Pull Request.

---
*Built with ❤️ for intelligent investing.*
