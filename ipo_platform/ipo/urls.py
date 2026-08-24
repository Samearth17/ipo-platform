"""
URL Configuration for IPO Platform
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .api_views import (
    RealTimeMarketDataAPI,
    MarketIndicesAPI,
    RecommendationAPI,
    TopRecommendationsAPI,
    PortfolioOptimizationAPI,
    SentimentAnalysisAPI,
    SocialSentimentAPI,
    RiskAssessmentAPI,
    PortfolioRiskAPI,
    IPOAnalysisAPI,
    TechnicalIndicatorsAPI,
    RefreshMarketDataAPI,
)

urlpatterns = [
    # Home
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # Password Reset & Change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile Management
    path('profile/', views.create_profile, name='create_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    
    # IPOs
    path('browse/', views.ipo_list, name='ipo_list'),
    path('ipo/<int:pk>/', views.ipo_detail, name='ipo_detail'),
    
    # Recommendations
    path('recommendations/', views.recommendations, name='recommendations'),
    
    # Portfolio
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/generate/', views.generate_portfolio, name='generate_portfolio'),
    path('portfolio/save/', views.save_current_portfolio, name='save_current_portfolio'),
    path('portfolio/saved/', views.saved_portfolios, name='saved_portfolios'),
    path('portfolio/saved/<int:pk>/', views.saved_portfolio_detail, name='saved_portfolio_detail'),
    path('portfolio/saved/<int:pk>/delete/', views.delete_saved_portfolio, name='delete_saved_portfolio'),
    
    # New Feature Pages
    path('risk-dashboard/', views.risk_dashboard, name='risk_dashboard'),
    path('sentiment-dashboard/', views.sentiment_dashboard, name='sentiment_dashboard'),
    
    # Watchlist
    path('watchlist/', views.watchlist, name='watchlist'),
    path('watchlist/add/<int:pk>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:pk>/', views.remove_from_watchlist, name='remove_from_watchlist'),

    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    
    # Search
    path('api/search/', views.search_suggestions, name='search_suggestions'),
    
    # Market Data APIs
    path('api/market-data/', RealTimeMarketDataAPI.as_view(), name='market-data-api'),
    path('api/market-indices/', MarketIndicesAPI.as_view(), name='market-indices-api'),
    path('api/refresh-market-data/', RefreshMarketDataAPI.as_view(), name='refresh-market-data-api'),
    
    # Recommendation APIs
    path('api/recommendations/', RecommendationAPI.as_view(), name='recommendations-api'),
    path('api/top-recommendations/', TopRecommendationsAPI.as_view(), name='top-recommendations-api'),
    
    # Portfolio APIs
    path('api/portfolio-optimization/', PortfolioOptimizationAPI.as_view(), name='portfolio-optimization-api'),
    path('api/portfolio-risk/', PortfolioRiskAPI.as_view(), name='portfolio-risk-api'),
    
    # Sentiment APIs
    path('api/sentiment/<str:symbol>/', SentimentAnalysisAPI.as_view(), name='sentiment-analysis-api'),
    path('api/social-sentiment/<str:symbol>/', SocialSentimentAPI.as_view(), name='social-sentiment-api'),
    
    # Risk APIs
    path('api/risk-assessment/', RiskAssessmentAPI.as_view(), name='risk-assessment-api'),
    path('api/risk-assessment/<str:symbol>/', RiskAssessmentAPI.as_view(), name='risk-assessment-symbol-api'),
    
    # Analysis APIs
    path('api/ipo-analysis/', IPOAnalysisAPI.as_view(), name='ipo-analysis-api'),
    path('api/ipo-analysis/<int:pk>/', IPOAnalysisAPI.as_view(), name='ipo-analysis-detail-api'),
    
    # Technical Analysis APIs
    path('api/technical-indicators/<str:symbol>/', TechnicalIndicatorsAPI.as_view(), name='technical-indicators-api'),
]
