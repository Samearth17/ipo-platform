"""
Enhanced Views
Views for IPO platform with all new features integrated.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.utils import timezone

from .models import IPO, InvestorProfile, Recommendation, PortfolioRecommendation, Watchlist, SavedPortfolio
from .recommendation_engine import RecommendationEngine, IPOScorer
from .portfolio_optimization import PortfolioOptimizer
from .market_data_service import MarketDataService, enrich_ipo_data
from .sentiment_analysis import SentimentAnalyzer, SocialMediaAnalyzer
from .risk_assessment import RiskAssessor, PortfolioRiskAnalyzer
from .analytics.scoring import AdvancedScorer, PeerComparator

import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Home page with featured IPOs and market overview."""
    featured_ipos = IPO.objects.filter(status='UPCOMING').order_by('-open_date')[:6]
    listed_ipos = IPO.objects.filter(status='LISTED').count()
    total_ipos = IPO.objects.count()
    
    market_indices = MarketDataService.get_market_indices()
    sector_performance = MarketDataService.get_sector_performance()
    
    context = {
        'featured_ipos': featured_ipos,
        'stats': {
            'total_ipos': total_ipos,
            'listed_ipos': listed_ipos,
            'active_investors': User.objects.filter(investor_profile__isnull=False).count(),
        },
        'market_indices': market_indices,
        'sector_performance': sector_performance
    }
    return render(request, 'index.html', context)


@require_http_methods(["GET", "POST"])
def signup(request):
    """User signup."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if User.objects.filter(username=username).exists():
            errors.append("Username already taken")
        if not email or '@' not in email:
            errors.append("Valid email required")
        if User.objects.filter(email=email).exists():
            errors.append("Email already registered")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        if password != password_confirm:
            errors.append("Passwords do not match")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {'errors': errors, 'username': username, 'email': email}
            return render(request, 'signup.html', context)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, f"Welcome {username}! Please set up your investor profile.")
            logger.info(f"New user registered: {username}")
            return redirect('create_profile')
        except Exception as e:
            logger.error(f"Error creating user {username}: {str(e)}")
            messages.error(request, "An error occurred during registration.")
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')


@require_http_methods(["GET", "POST"])
def user_login(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not hasattr(user, 'investor_profile'):
                messages.info(request, "Please set up your investor profile.")
                return redirect('create_profile')
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            logger.info(f"User logged in: {username}")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            logger.warning(f"Failed login attempt for username: {username}")
            return render(request, 'login.html', {'username': username})
    
    return render(request, 'login.html')


@login_required
def user_logout(request):
    """User logout."""
    logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    """User dashboard with personalized overview."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        return redirect('create_profile')
    if not profile.onboarding_completed:
        return redirect('create_profile')
    
    # Get recommendations
    engine = RecommendationEngine(profile)
    recommendations = engine.get_top_recommendations(IPO.objects.all(), limit=5)
    
    # Get portfolio
    try:
        portfolio = PortfolioRecommendation.objects.get(investor_profile=profile)
        portfolio_data = {
            'expected_return': float(portfolio.expected_return),
            'portfolio_risk': float(portfolio.portfolio_risk),
            'diversification': float(portfolio.diversification_score),
            'holdings_count': portfolio.top_recommendations.count(),
        }
    except PortfolioRecommendation.DoesNotExist:
        portfolio_data = None
    
    # Get market overview
    market_indices = MarketDataService.get_market_indices()
    sector_performance = MarketDataService.get_sector_performance()[:5]
    
    # Get watchlist summary
    try:
        watchlist = Watchlist.objects.get(user=request.user)
        watchlist_count = watchlist.ipos.count()
    except Watchlist.DoesNotExist:
        watchlist_count = 0
    
    # Stats
    total_ipos = IPO.objects.count()
    listed_ipos = IPO.objects.filter(status='LISTED').count()
    upcoming_ipos = IPO.objects.filter(status='UPCOMING').count()
    
    context = {
        'profile': profile,
        'strategy': profile.get_persona_strategy(),
        'recommendations': recommendations,
        'portfolio': portfolio_data,
        'watchlist_count': watchlist_count,
        'saved_portfolio_count': SavedPortfolio.objects.filter(user=request.user).count(),
        'recent_saved_portfolios': SavedPortfolio.objects.filter(user=request.user)[:3],
        'market_indices': market_indices,
        'sector_performance': sector_performance,
        'stats': {
            'total_ipos': total_ipos,
            'listed_ipos': listed_ipos,
            'upcoming_ipos': upcoming_ipos,
            'recommendations_count': len(recommendations),
        }
    }
    
    return render(request, 'ipo/dashboard.html', context)


@login_required
def create_profile(request):
    """Create/Edit investor profile."""
    profile, created = InvestorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        persona = request.POST.get('persona', 'balanced')
        if persona not in {'conservative', 'balanced', 'growth', 'aggressive'}:
            messages.error(request, 'Please select a valid investor persona.')
            return redirect('create_profile')
        investment_horizon = request.POST.get('investment_horizon', 'medium')
        
        # Robust parsing for risk_tolerance
        try:
            risk_tolerance = int(request.POST.get('risk_tolerance') or 5)
        except (ValueError, TypeError):
            risk_tolerance = 5
            
        try:
            min_investment = float(request.POST.get('min_investment') or 50000)
            max_investment = float(request.POST.get('max_investment') or 1000000)
        except (ValueError, TypeError):
            min_investment = 50000
            max_investment = 1000000
        
        profile.persona = persona
        profile.investment_horizon = investment_horizon
        profile.risk_tolerance = risk_tolerance
        profile.min_investment = min_investment
        profile.max_investment = max_investment
        profile.onboarding_completed = True
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')
    
    context = {
        'profile': profile,
        'is_onboarding': not profile.onboarding_completed,
        'google_account': _google_account(request.user),
        'personas': [
            {'value': 'conservative', 'label': 'Conservative', 'description': 'Capital preservation with modest growth'},
            {'value': 'balanced', 'label': 'Balanced', 'description': 'Balanced risk-return approach'},
            {'value': 'growth', 'label': 'Growth', 'description': 'Growth with risk guardrails'},
            {'value': 'aggressive', 'label': 'Aggressive', 'description': 'Growth maximization'}
        ]
    }
    
    return render(request, 'profile.html', context)


def _google_account(user):
    """Return Google identity data when available without requiring OAuth at startup."""
    try:
        return user.socialaccount_set.filter(provider='google').first()
    except Exception:
        return None


def ipo_list(request):
    """Browse all IPOs with filters."""
    ipos = IPO.objects.all().order_by('-open_date')
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        ipos = ipos.filter(
            Q(company_name__icontains=search) |
            Q(sector__icontains=search) |
            Q(lead_manager__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status', '')
    if status in ['UPCOMING', 'ONGOING', 'LISTED']:
        ipos = ipos.filter(status=status)
    
    # Sector filter
    sector = request.GET.get('sector', '').strip()
    if sector:
        ipos = ipos.filter(sector__icontains=sector)
    
    # Sort
    sort = request.GET.get('sort', '-open_date')
    if sort in ['open_date', '-open_date', 'issue_size', '-issue_size', 'company_name']:
        ipos = ipos.order_by(sort)
    
    recommendation_filter = request.GET.get('recommendation', '')
    min_score = request.GET.get('min_score', '')
    risk_level_filter = request.GET.get('risk_level', '')
    watched_ids = set()
    if request.user.is_authenticated:
        watched_ids = set(Watchlist.objects.filter(user=request.user).values_list('ipos__id', flat=True))
    cards = []
    for ipo in ipos:
        scores = IPOScorer(ipo).get_all_scores()
        overall, safety = scores['overall_score'], scores['risk_score']
        recommendation = 'BUY' if overall >= 65 else 'HOLD' if overall >= 50 else 'SELL'
        risk_level = 'Low' if safety >= 65 else 'Moderate' if safety >= 45 else 'High'
        if min_score:
            try:
                if overall < float(min_score):
                    continue
            except ValueError:
                pass
        if recommendation_filter and recommendation != recommendation_filter:
            continue
        if risk_level_filter and risk_level != risk_level_filter:
            continue
        ipo.quant_score, ipo.risk_level, ipo.recommendation_label = overall, risk_level, recommendation
        ipo.is_watchlisted = ipo.id in watched_ids
        cards.append(ipo)
    sectors = IPO.objects.values_list('sector', flat=True).distinct().order_by('sector')
    total_count = len(cards)
    
    context = {
        'ipos': cards,
        'search': search,
        'status': status,
        'sector': sector,
        'sort': sort,
        'sectors': sectors,
        'total_count': total_count,
        'recommendation_filter': recommendation_filter,
        'min_score': min_score,
        'risk_level_filter': risk_level_filter,
    }
    
    return render(request, 'ipo/ipo_list.html', context)


def ipo_detail(request, pk):
    """IPO detail page with analysis."""
    ipo = get_object_or_404(IPO, pk=pk)
    
    # Get market data
    symbol = getattr(ipo, 'symbol', ipo.company_name[:4].upper())
    market_data = MarketDataService.fetch_ipo_data(symbol)
    
    # Calculate scores
    scorer = IPOScorer(ipo)
    scores = scorer.get_all_scores()
    score_rows = [(label, scores[key]) for label, key in [
        ('Financial', 'financial_score'), ('Growth', 'growth_score'), ('Valuation', 'valuation_score'),
        ('Risk / Safety', 'risk_score'), ('Quality', 'quality_score'), ('Momentum', 'momentum_score'),
        ('ESG', 'esg_score'), ('Management', 'management_score')
    ]]
    
    # Get recommendation
    try:
        if not request.user.is_authenticated:
            raise InvestorProfile.DoesNotExist
        profile = InvestorProfile.objects.get(user=request.user)
        
        recommendation, created = Recommendation.objects.get_or_create(
            investor_profile=profile,
            ipo=ipo,
            defaults={
                'rating': 'HOLD',
                'confidence_score': 50,
                'financial_score': scores['financial_score'],
                'risk_score': scores['risk_score'],
                'growth_score': scores['growth_score'],
                'overall_score': scores['overall_score'],
                'rationale': 'Generating recommendation...'
            }
        )
        
        if created or recommendation.overall_score == 50:
            engine = RecommendationEngine(profile)
            rec_data = engine.score_ipo_for_investor(ipo)
            
            recommendation.rating = rec_data['rating']
            recommendation.confidence_score = rec_data['confidence_score']
            recommendation.financial_score = rec_data['financial_score']
            recommendation.risk_score = rec_data['risk_score']
            recommendation.growth_score = rec_data['growth_score']
            recommendation.overall_score = rec_data['overall_score']
            recommendation.rationale = rec_data['rationale']
            recommendation.human_insight = rec_data.get('human_insight', '')
            recommendation.save()
        
        has_recommendation = True
    except InvestorProfile.DoesNotExist:
        recommendation = None
        has_recommendation = False
    
    # Get sentiment analysis
    sentiment_analyzer = SentimentAnalyzer()
    sentiment = sentiment_analyzer.analyze_sentiment(symbol)
    sentiment_trend = sentiment_analyzer.get_sentiment_trend(symbol)
    
    # Get risk assessment
    risk_assessor = RiskAssessor()
    risk_assessment = risk_assessor.assess_risk(ipo)
    
    # Get peer comparison
    scorer = AdvancedScorer(IPO.objects.all())
    analysis = scorer.analyze_ipo(ipo, IPO.objects.all())
    
    # Related recommendations
    related_recommendations = Recommendation.objects.none()
    
    context = {
        'ipo': ipo,
        'scores': scores,
        'score_rows': score_rows,
        'recommendation': recommendation,
        'has_recommendation': has_recommendation,
        'sentiment': sentiment,
        'sentiment_trend': sentiment_trend,
        'risk_assessment': risk_assessment,
        'analysis': analysis,
        'related_recommendations': related_recommendations,
        'is_watchlisted': request.user.is_authenticated and Watchlist.objects.filter(user=request.user, ipos=ipo).exists(),
    }
    
    return render(request, 'ipo/ipo_detail.html', context)


@login_required
def recommendations(request):
    """Personalized recommendations page."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        messages.error(request, 'Please create your investor profile first')
        return redirect('create_profile')
    
    # Get filters
    rating_filter = request.GET.get('rating', '')
    sector_filter = request.GET.get('sector', '')
    sort_by = request.GET.get('sort', '-overall_score')
    
    # Get recommendations
    engine = RecommendationEngine(profile)
    all_recommendations = engine.get_filtered_recommendations(
        IPO.objects.all(),
        filters={
            'only_compatible': False,
            'min_score': 30
        }
    )
    
    # Apply filters
    if rating_filter:
        all_recommendations = [r for r in all_recommendations if r['rating'] == rating_filter]
    
    if sector_filter:
        all_recommendations = [r for r in all_recommendations if r['ipo'].sector == sector_filter]
    
    # Sort
    if sort_by:
        reverse = not sort_by.startswith('-')
        sort_field = sort_by.lstrip('-')
        all_recommendations.sort(key=lambda x: x.get(sort_field, 0), reverse=reverse)
    
    # Get unique sectors from saved recommendations
    sectors = list(set(
        r.ipo.sector for r in Recommendation.objects.filter(
            investor_profile=profile
        ).select_related('ipo')
    ))
    
    # Statistics
    total_recs = len(all_recommendations)
    avg_score = sum(r['overall_score'] for r in all_recommendations) / total_recs if total_recs > 0 else 0
    
    # Format for template
    formatted_recs = []
    for rec in all_recommendations[:50]:
        rec_obj = rec['recommendation'] if 'recommendation' in rec else None
        formatted_recs.append({
            'id': rec['ipo'].id,
            'company_name': rec['ipo'].company_name,
            'sector': rec['ipo'].sector,
            'rating': rec['rating'],
            'overall_score': rec['overall_score'],
            'financial_score': rec['financial_score'],
            'risk_score': rec['risk_score'],
            'growth_score': rec['growth_score'],
            'is_compatible': rec['is_compatible'],
            'risk_level': rec['risk_level'],
            'rationale': rec['rationale'][:200],
            'predicted_return': rec.get('predicted_return', 0)
        })
    
    context = {
        'profile': profile,
        'recommendations': formatted_recs,
        'total_count': total_recs,
        'avg_score': round(avg_score, 2),
        'rating': rating_filter,
        'sector': sector_filter,
        'sort': sort_by,
        'sectors': sectors
    }
    
    return render(request, 'ipo/recommendations.html', context)


@login_required
def portfolio(request):
    """Portfolio management page."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        messages.error(request, 'Please create your investor profile first')
        return redirect('create_profile')
    
    try:
        portfolio_obj = PortfolioRecommendation.objects.get(investor_profile=profile)
        top_recommendations = portfolio_obj.top_recommendations.all().order_by('-overall_score')
        has_portfolio = True
    except PortfolioRecommendation.DoesNotExist:
        top_recommendations = None
        portfolio_obj = None
        has_portfolio = False
    
    # Get portfolio risk analysis
    if has_portfolio and top_recommendations:
        # Calculate actual weights based on recommendations
        total_recs = top_recommendations.count()
        
        # Use the optimizer's persisted weights; equal weight is only a legacy fallback.
        weights = [float(rec.weight) for rec in top_recommendations]
        if not any(weights):
            weights = [1.0 / total_recs] * total_recs if total_recs else []
        
        holdings = []
        for idx, rec in enumerate(top_recommendations):
            ipo = rec.ipo
            weight = weights[idx] if idx < len(weights) else (1.0 / total_recs)
            holdings.append({
                'symbol': getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
                'company_name': ipo.company_name,
                'sector': ipo.sector,
                'weight': weight,
                'volatility': float(ipo.volatility) if ipo.volatility else 30,
                # No beta is stored in the schema; PortfolioRiskAnalyzer uses an explicit neutral fallback.
            })
        
        analyzer = PortfolioRiskAnalyzer()
        risk_analysis = analyzer.analyze_portfolio_risk(holdings, float(profile.max_investment))
        
        # Stress test scenarios
        scenarios = {
            "Market Crash (-20%)": {"market_drop": -20, "sector_impacts": {}},
            "Interest Rate Hike": {"market_drop": -10, "sector_impacts": {"Finance": -5}},
            "Tech Sector Correction": {"market_drop": -15, "sector_impacts": {"Technology": -10}}
        }
        stress_results = analyzer.stress_test_portfolio(holdings, scenarios)
    else:
        risk_analysis = None
        stress_results = None
    
    context = {
        'profile': profile,
        'portfolio': portfolio_obj,
        'recommendations': top_recommendations,
        'has_portfolio': has_portfolio,
        'total_count': top_recommendations.count() if top_recommendations else 0,
        'risk_analysis': risk_analysis,
        'stress_results': stress_results
    }
    
    return render(request, 'ipo/portfolio.html', context)


@login_required
def generate_portfolio(request):
    """Generate optimized portfolio."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        messages.error(request, 'Please create your investor profile first')
        return redirect('create_profile')
    
    if request.method == 'POST':
        allocation = float(request.POST.get('allocation_amount', 100000))
        diversification = int(request.POST.get('diversification', 5))
        
        status_filter = []
        if request.POST.get('include_upcoming'):
            status_filter.append('UPCOMING')
        if request.POST.get('include_ongoing'):
            status_filter.append('ONGOING')
        if request.POST.get('include_listed'):
            status_filter.append('LISTED')
            
        if not status_filter:
            status_filter = ['UPCOMING', 'ONGOING']
        
        ipos = IPO.objects.filter(status__in=status_filter)
        
        optimizer = PortfolioOptimizer(profile)
        portfolio_data = optimizer.optimize_portfolio(ipos, allocation_amount=allocation, diversification=diversification)
        
        if portfolio_data['success']:
            portfolio_obj, _ = PortfolioRecommendation.objects.get_or_create(
                investor_profile=profile
            )
            
            portfolio_obj.top_recommendations.clear()
            for item in portfolio_data['portfolio']:
                ipo = item['recommendation']['ipo']
                
                rec, _ = Recommendation.objects.update_or_create(
                    investor_profile=profile,
                    ipo=ipo,
                    defaults={
                        'rating': item['recommendation']['rating'],
                        'confidence_score': item['recommendation']['confidence_score'],
                        'financial_score': item['recommendation']['financial_score'],
                        'risk_score': item['recommendation']['risk_score'],
                        'growth_score': item['recommendation']['growth_score'],
                        'overall_score': item['recommendation']['overall_score'],
                        'weight': item['weight'],
                        'allocated_amount': item['allocated_amount'],
                        'rationale': item['recommendation']['rationale'],
                        'human_insight': item['recommendation'].get('human_insight', '')
                    }
                )
                portfolio_obj.top_recommendations.add(rec)
            
            portfolio_obj.total_allocation = allocation
            portfolio_obj.expected_return = portfolio_data['metrics']['expected_return']
            portfolio_obj.portfolio_risk = portfolio_data['metrics']['portfolio_risk']
            portfolio_obj.diversification_score = portfolio_data['metrics']['diversification_score']
            portfolio_obj.save()
            
            messages.success(request, "Portfolio generated successfully!")
            return redirect('portfolio')
        else:
            messages.error(request, portfolio_data.get('error', 'Failed to generate portfolio'))
    
    context = {
        'profile': profile,
        'strategy': profile.get_persona_strategy(),
    }
    
    return render(request, 'ipo/generate_portfolio.html', context)


@login_required
def risk_dashboard(request):
    """Risk assessment dashboard."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        return redirect('create_profile')
    
    # Get all IPOs with risk assessments
    ipos = IPO.objects.all()
    assessor = RiskAssessor()
    comparison = assessor.compare_risk(ipos)
    
    # Get portfolio risk if exists
    try:
        portfolio = PortfolioRecommendation.objects.get(investor_profile=profile)
        top_recs = portfolio.top_recommendations.all()
        total_recs = top_recs.count()
        
        weights = [float(rec.weight) for rec in top_recs]
        if not any(weights):
            weights = [1.0 / total_recs] * total_recs if total_recs else []
        
        holdings = []
        for idx, rec in enumerate(top_recs):
            ipo = rec.ipo
            weight = weights[idx] if idx < len(weights) else (1.0 / total_recs)
            holdings.append({
                'symbol': getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
                'company_name': ipo.company_name,
                'sector': ipo.sector,
                'weight': weight,
                'volatility': float(ipo.volatility) if ipo.volatility else 30,
                # No beta is stored in the schema; PortfolioRiskAnalyzer uses an explicit neutral fallback.
            })
        
        analyzer = PortfolioRiskAnalyzer()
        portfolio_risk = analyzer.analyze_portfolio_risk(holdings, float(profile.max_investment))
    except PortfolioRecommendation.DoesNotExist:
        portfolio_risk = None
    
    context = {
        'profile': profile,
        'risk_rankings': comparison['ranked_ipos'],
        'lowest_risk': comparison['lowest_risk'],
        'highest_risk': comparison['highest_risk'],
        'portfolio_risk': portfolio_risk
    }
    
    return render(request, 'ipo/risk_dashboard.html', context)


@login_required
def sentiment_dashboard(request):
    """Sentiment analysis dashboard."""
    try:
        profile = InvestorProfile.objects.get(user=request.user)
    except InvestorProfile.DoesNotExist:
        return redirect('create_profile')
    
    # Get market sentiment
    sentiment_analyzer = SentimentAnalyzer()
    market_sentiment = sentiment_analyzer.get_market_sentiment_index()
    
    # Get trending symbols
    social_analyzer = SocialMediaAnalyzer()
    trending = social_analyzer.get_trending_symbols()
    
    # Get IPOs with sentiment
    ipos = IPO.objects.all()[:10]
    ipo_sentiments = []
    for ipo in ipos:
        symbol = getattr(ipo, 'symbol', ipo.company_name[:4].upper())
        sentiment = sentiment_analyzer.analyze_sentiment(symbol)
        trend = sentiment_analyzer.get_sentiment_trend(symbol)
        ipo_sentiments.append({
            'company_name': ipo.company_name,
            'symbol': symbol,
            'sentiment': sentiment.overall_sentiment,
            'score': sentiment.sentiment_score,
            'confidence': sentiment.confidence,
            'trend': trend[:7]
        })
    
    context = {
        'profile': profile,
        'market_sentiment': market_sentiment,
        'trending': trending,
        'ipo_sentiments': ipo_sentiments
    }
    
    return render(request, 'ipo/sentiment_dashboard.html', context)


@login_required
def watchlist(request):
    """User watchlist."""
    watchlist_obj, created = Watchlist.objects.get_or_create(user=request.user)
    ipos = watchlist_obj.ipos.all().order_by('-open_date')
    
    context = {
        'ipos': ipos,
        'total_count': ipos.count(),
    }
    return render(request, 'ipo/watchlist.html', context)


@login_required
@require_POST
def add_to_watchlist(request, pk):
    """Add IPO to watchlist."""
    ipo = get_object_or_404(IPO, pk=pk)
    watchlist_obj, created = Watchlist.objects.get_or_create(user=request.user)
    
    watchlist_obj.ipos.add(ipo)
    messages.success(request, f'{ipo.company_name} added to watchlist!')
    
    return redirect('ipo_detail', pk=pk)


@login_required
@require_POST
def remove_from_watchlist(request, pk):
    """Remove IPO from watchlist."""
    ipo = get_object_or_404(IPO, pk=pk)
    watchlist_obj, created = Watchlist.objects.get_or_create(user=request.user)
    
    watchlist_obj.ipos.remove(ipo)
    messages.success(request, f'{ipo.company_name} removed from watchlist!')
    
    return redirect('watchlist')


@login_required
@require_POST
def save_current_portfolio(request):
    """Persist the current user's allocation as an immutable JSON snapshot."""
    profile = get_object_or_404(InvestorProfile, user=request.user)
    current = get_object_or_404(PortfolioRecommendation, investor_profile=profile)
    recommendations = current.top_recommendations.select_related('ipo').all()
    allocations = [{
        'ipo_id': rec.ipo_id, 'company_name': rec.ipo.company_name, 'symbol': rec.ipo.symbol,
        'sector': rec.ipo.sector, 'weight': rec.weight, 'allocated_amount': float(rec.allocated_amount),
    } for rec in recommendations]
    SavedPortfolio.objects.create(
        user=request.user,
        name=request.POST.get('name', '').strip() or f"Portfolio {timezone.localdate()}",
        investor_persona=profile.persona,
        optimization_method=request.POST.get('optimization_method', 'current_allocation'),
        allocations=allocations,
        metrics={'expected_return': current.expected_return, 'portfolio_risk': current.portfolio_risk, 'diversification_score': current.diversification_score},
    )
    messages.success(request, 'Portfolio saved to your account.')
    return redirect('saved_portfolios')


@login_required
def saved_portfolios(request):
    return render(request, 'ipo/saved_portfolios.html', {'saved_portfolios': SavedPortfolio.objects.filter(user=request.user)})


@login_required
def saved_portfolio_detail(request, pk):
    portfolio = get_object_or_404(SavedPortfolio, pk=pk, user=request.user)
    return render(request, 'ipo/saved_portfolio_detail.html', {'saved_portfolio': portfolio})


@login_required
@require_POST
def delete_saved_portfolio(request, pk):
    get_object_or_404(SavedPortfolio, pk=pk, user=request.user).delete()
    messages.success(request, 'Saved portfolio deleted.')
    return redirect('saved_portfolios')


@login_required
@require_POST
def delete_account(request):
    if request.POST.get('confirmation') != 'DELETE':
        messages.error(request, 'Type DELETE to confirm account deletion.')
        return redirect('create_profile')
    request.user.delete()
    messages.success(request, 'Your account and personal data were deleted. Global IPO data was retained.')
    return redirect('index')


def terms(request):
    return render(request, 'legal/terms.html')


def privacy(request):
    return render(request, 'legal/privacy.html')


def disclaimer(request):
    return render(request, 'legal/disclaimer.html')


def contact(request):
    return render(request, 'legal/contact.html')


def about(request):
    return render(request, 'legal/about.html')


def how_it_works(request):
    return render(request, 'legal/how_it_works.html')


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


def search_suggestions(request):
    """Search autocomplete suggestions."""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    ipos = IPO.objects.filter(
        Q(company_name__icontains=query) |
        Q(sector__icontains=query)
    ).values('id', 'company_name', 'sector')[:10]
    
    return JsonResponse({
        'results': list(ipos)
    })


@login_required
def refresh_market_data(request):
    """Refresh market data for all IPOs."""
    if request.method == 'POST':
        ipos = IPO.objects.all()
        result = MarketDataService.update_ipo_data(ipos)
        
        messages.success(request, 
            f"Updated: {result['success']}, Failed: {result['failed']}, Skipped: {result['skipped']}")
        
        return redirect('dashboard')
    
    return redirect('dashboard')
