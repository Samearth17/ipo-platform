"""
Enhanced API Views
Provides REST API endpoints for all platform features.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import IPO, InvestorProfile, Recommendation, PortfolioRecommendation
from .recommendation_engine import RecommendationEngine, PortfolioOptimizer
from .personalization import effective_method, effective_profile
from .market_data_service import MarketDataService, TechnicalIndicatorService
from .sentiment_analysis import SentimentAnalyzer, SocialMediaAnalyzer
from .risk_assessment import RiskAssessor, PortfolioRiskAnalyzer
from .analytics.scoring import AdvancedScorer, PeerComparator

import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class RealTimeMarketDataAPI(APIView):
    """Fetch real-time market data for IPOs."""
    
    def get(self, request):
        """Get real-time market data."""
        symbol = request.GET.get('symbol')
        
        if symbol:
            data = MarketDataService.fetch_ipo_data(symbol)
            return Response({"data": data})
        else:
            # Get data for all IPOs
            ipos = IPO.objects.all()
            data = []
            for ipo in ipos:
                ipo_symbol = getattr(ipo, 'symbol', ipo.company_name[:4].upper())
                market_data = MarketDataService.fetch_ipo_data(ipo_symbol)
                data.append({
                    'id': ipo.id,
                    'company_name': ipo.company_name,
                    'symbol': ipo_symbol,
                    'current_price': market_data.get('current_price'),
                    'market_cap': market_data.get('market_cap'),
                    'pe_ratio': market_data.get('pe_ratio'),
                    'roe': market_data.get('roe'),
                    'roa': market_data.get('roa'),
                    'volatility': market_data.get('volatility'),
                    'revenue_growth': market_data.get('revenue_growth'),
                })
            
            return Response({"ipos": data})


@method_decorator(login_required, name='dispatch')
class MarketIndicesAPI(APIView):
    """Get current market index values."""
    
    def get(self, request):
        """Get market indices."""
        indices = MarketDataService.get_market_indices()
        sectors = MarketDataService.get_sector_performance()
        return Response({
            "indices": indices,
            "sectors": sectors
        })


@method_decorator(login_required, name='dispatch')
class RecommendationAPI(APIView):
    """Fetch personalized IPO recommendations."""
    
    def get(self, request):
        """Get recommendations for logged-in user."""
        try:
            profile = request.user.investor_profile
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found. Please create your profile first."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get filters from request
        min_score = int(request.GET.get('min_score', 50))
        max_volatility = float(request.GET.get('max_volatility', 100))
        only_compatible = request.GET.get('only_compatible', 'false').lower() == 'true'
        
        recommendation_profile, effective_persona = effective_profile(profile, request.GET.get('persona'))
        engine = RecommendationEngine(recommendation_profile)
        recommendations = engine.get_filtered_recommendations(
            IPO.objects.all(),
            filters={
                'min_score': min_score,
                'max_volatility': max_volatility,
                'only_compatible': only_compatible
            }
        )
        
        # Format response
        data = []
        for rec in recommendations[:20]:
            data.append({
                'id': rec['ipo'].id,
                'company_name': rec['ipo'].company_name,
                'symbol': getattr(rec['ipo'], 'symbol', rec['ipo'].company_name[:4].upper()),
                'sector': rec['ipo'].sector,
                'rating': rec['rating'],
                'overall_score': rec['overall_score'],
                'financial_score': rec['financial_score'],
                'growth_score': rec['growth_score'],
                'risk_score': rec['risk_score'],
                'valuation_score': rec.get('valuation_score'),
                'quality_score': rec.get('quality_score'),
                'is_compatible': rec['is_compatible'],
                'risk_level': rec['risk_level'],
                'predicted_return': rec.get('predicted_return'),
                'rationale': rec['rationale']
            })
        
        return Response({
            "recommendations": data,
            "count": len(data),
            "persona": effective_persona
        })


@method_decorator(login_required, name='dispatch')
class TopRecommendationsAPI(APIView):
    """Get top N recommendations."""
    
    def get(self, request):
        """Get top recommendations."""
        try:
            profile = request.user.investor_profile
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        limit = int(request.GET.get('limit', 5))
        
        recommendation_profile, effective_persona = effective_profile(profile, request.GET.get('persona'))
        engine = RecommendationEngine(recommendation_profile)
        top_recs = engine.get_top_recommendations(IPO.objects.all(), limit=limit)
        
        data = [{
            'company_name': rec['ipo'].company_name,
            'rating': rec['rating'],
            'overall_score': rec['overall_score'],
            'expected_return': rec.get('predicted_return', rec['overall_score'] * 0.8)
        } for rec in top_recs]
        
        return Response({"top_recommendations": data, "persona": effective_persona})


@method_decorator(login_required, name='dispatch')
class PortfolioOptimizationAPI(APIView):
    """Portfolio optimization API."""
    
    def get(self, request):
        """Get optimized portfolio."""
        try:
            profile = request.user.investor_profile
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        allocation = float(request.GET.get('allocation', profile.max_investment))
        portfolio_profile, effective_persona = effective_profile(profile, request.GET.get('persona'))
        optimization_method = effective_method(request.GET.get('optimization_method'), effective_persona)

        optimizer = PortfolioOptimizer(portfolio_profile)
        result = optimizer.optimize_portfolio(allocation_amount=allocation, method=optimization_method)
        
        if result['success']:
            portfolio_data = [{
                'company_name': item['company_name'],
                'sector': item['sector'],
                'allocated_amount': item['allocated_amount'],
                'weight': item['weight'],
                'expected_return': item.get('expected_return'),
                'rating': item.get('rating')
            } for item in result['portfolio']]
            
            return Response({
                "success": True,
                "portfolio": portfolio_data,
                "metrics": result['metrics'],
                "strategy": result['strategy'],
                "persona": effective_persona,
                "capital": allocation,
            })
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """Generate new portfolio."""
        try:
            profile = request.user.investor_profile
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        request_data = request.data if hasattr(request, 'data') else request.POST
        allocation = float(request_data.get('allocation', profile.max_investment))
        portfolio_profile, effective_persona = effective_profile(profile, request_data.get('persona'))
        optimization_method = effective_method(request_data.get('optimization_method'), effective_persona)

        optimizer = PortfolioOptimizer(portfolio_profile)
        result = optimizer.optimize_portfolio(allocation_amount=allocation, method=optimization_method)
        
        if result['success']:
            # Save to database
            portfolio_obj, _ = PortfolioRecommendation.objects.get_or_create(
                investor_profile=profile
            )
            portfolio_obj.top_recommendations.clear()
            
            for item in result['portfolio']:
                rec_data = item['recommendation']
                ipo = rec_data['ipo']
                rec, _ = Recommendation.objects.get_or_create(
                    investor_profile=profile,
                    ipo=ipo,
                    defaults={
                        'rating': rec_data['rating'],
                        'confidence_score': rec_data['confidence_score'],
                        'financial_score': rec_data['financial_score'],
                        'risk_score': rec_data['risk_score'],
                        'growth_score': rec_data['growth_score'],
                        'overall_score': rec_data['overall_score'],
                        'rationale': rec_data['rationale']
                    }
                )
                portfolio_obj.top_recommendations.add(rec)
            
            portfolio_obj.expected_return = result['metrics']['expected_return']
            portfolio_obj.portfolio_risk = result['metrics']['portfolio_risk']
            portfolio_obj.diversification_score = result['metrics']['diversification_score']
            portfolio_obj.save()
            
            return Response({
                "success": True,
                "message": "Portfolio generated successfully",
                "portfolio_id": portfolio_obj.id,
                "persona": effective_persona,
                "capital": allocation,
                "strategy": result['strategy'],
            })
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class SentimentAnalysisAPI(APIView):
    """Sentiment analysis API."""
    
    def get(self, request, symbol):
        """Get sentiment analysis for a symbol."""
        analyzer = SentimentAnalyzer()
        sentiment = analyzer.analyze_sentiment(symbol)
        trend = analyzer.get_sentiment_trend(symbol)
        market_sentiment = analyzer.get_market_sentiment_index()
        
        return Response({
            "symbol": symbol,
            "sentiment": {
                "overall": sentiment.overall_sentiment,
                "score": sentiment.sentiment_score,
                "confidence": sentiment.confidence,
                "positive_count": sentiment.positive_count,
                "negative_count": sentiment.negative_count,
                "neutral_count": sentiment.neutral_count,
                "key_topics": sentiment.key_topics,
                "news_count": sentiment.news_count
            },
            "trend": trend,
            "market_sentiment": market_sentiment
        })


@method_decorator(login_required, name='dispatch')
class SocialSentimentAPI(APIView):
    """Social media sentiment API."""
    
    def get(self, request, symbol):
        """Get social media sentiment for a symbol."""
        analyzer = SocialMediaAnalyzer()
        sentiment = analyzer.analyze_social_sentiment(symbol)
        trending = analyzer.get_trending_symbols()
        
        return Response({
            "symbol": symbol,
            "social_sentiment": sentiment,
            "trending_symbols": trending
        })


@method_decorator(login_required, name='dispatch')
class RiskAssessmentAPI(APIView):
    """Risk assessment API."""
    
    def get(self, request, symbol=None):
        """Get risk assessment for a symbol or all IPOs."""
        if symbol:
            try:
                ipo = IPO.objects.get(symbol=symbol)
            except IPO.DoesNotExist:
                return Response(
                    {"error": f"IPO with symbol {symbol} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            assessor = RiskAssessor()
            assessment = assessor.assess_risk(ipo, request.user.investor_profile)
            
            return Response({
                "symbol": symbol,
                "overall_risk_score": assessment.overall_risk_score,
                "risk_level": assessment.risk_level,
                "risk_rating": assessment.risk_rating,
                "risk_factors": assessment.risk_factors,
                "metrics": {
                    "volatility": assessment.metrics.volatility,
                    "beta": assessment.metrics.beta,
                    "Sharpe_ratio": assessment.metrics.Sharpe_ratio,
                    "VaR_95": assessment.metrics.VaR_95,
                    "VaR_99": assessment.metrics.VaR_99,
                    "max_drawdown": assessment.metrics.max_drawdown,
                    "sortino_ratio": assessment.metrics.sortino_ratio
                }
            })
        else:
            # Return risk comparison for all IPOs
            ipos = IPO.objects.all()
            assessor = RiskAssessor()
            comparison = assessor.compare_risk(ipos)
            
            return Response({
                "ranked_ipos": comparison['ranked_ipos'],
                "lowest_risk": comparison['lowest_risk'],
                "highest_risk": comparison['highest_risk']
            })


@method_decorator(login_required, name='dispatch')
class PortfolioRiskAPI(APIView):
    """Portfolio risk analysis API."""
    
    def get(self, request):
        """Get portfolio risk analysis."""
        try:
            profile = request.user.investor_profile
        except InvestorProfile.DoesNotExist:
            return Response(
                {"error": "Investor profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get current portfolio
        try:
            portfolio = PortfolioRecommendation.objects.get(investor_profile=profile)
            holdings = []
            for rec in portfolio.top_recommendations.all():
                ipo = rec.ipo
                holdings.append({
                    'symbol': getattr(ipo, 'symbol', ipo.company_name[:4].upper()),
                    'company_name': ipo.company_name,
                    'sector': ipo.sector,
                    'weight': 0.2,  # Simplified
                    'volatility': float(ipo.volatility) if ipo.volatility else 30,
                    # Beta is only returned when calculated from aligned historical returns.
                })
        except PortfolioRecommendation.DoesNotExist:
            holdings = []
        
        if holdings:
            analyzer = PortfolioRiskAnalyzer()
            portfolio_value = float(profile.max_investment)
            risk_analysis = analyzer.analyze_portfolio_risk(holdings, portfolio_value)
            
            # Stress test
            scenarios = {
                "market_crash": {"market_drop": -20, "sector_impacts": {}},
                "rate_hike": {"market_drop": -10, "sector_impacts": {"Finance": -5}},
                "tech_crash": {"market_drop": -15, "sector_impacts": {"Technology": -10}}
            }
            stress_results = analyzer.stress_test_portfolio(holdings, scenarios)
            
            return Response({
                "risk_analysis": risk_analysis,
                "stress_tests": stress_results
            })
        else:
            return Response({
                "error": "No portfolio found",
                "risk_analysis": None
            })


@method_decorator(login_required, name='dispatch')
class IPOAnalysisAPI(APIView):
    """Advanced IPO analysis API."""
    
    def get(self, request, pk=None):
        """Get detailed IPO analysis."""
        if pk:
            try:
                ipo = IPO.objects.get(pk=pk)
            except IPO.DoesNotExist:
                return Response(
                    {"error": "IPO not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            scorer = AdvancedScorer(IPO.objects.all())
            analysis = scorer.analyze_ipo(ipo, IPO.objects.all())
            
            # Get peer comparison
            comparator = PeerComparator(IPO.objects.all())
            rankings = comparator.get_rankings()[:10]
            
            my_rank = next((i for i, r in enumerate(rankings, 1) 
                          if r['ipo'].id == ipo.id), None)
            
            return Response({
                "analysis": {
                    "symbol": analysis.symbol,
                    "financial_score": analysis.financial_score,
                    "growth_score": analysis.growth_score,
                    "risk_score": analysis.risk_score,
                    "momentum_score": analysis.momentum_score,
                    "valuation_score": analysis.valuation_score,
                    "quality_score": analysis.quality_score,
                    "overall_score": analysis.overall_score,
                    "percentiles": analysis.percentiles,
                    "strengths": analysis.strengths,
                    "weaknesses": analysis.weaknesses,
                    "recommendations": analysis.recommendations
                },
                "rank": my_rank,
                "total_ipos": len(rankings)
            })
        else:
            # Return all IPOs with rankings
            scorer = AdvancedScorer(IPO.objects.all())
            rankings = scorer.get_rankings()[:20]
            
            data = [{
                'id': r['ipo'].id,
                'company_name': r['ipo'].company_name,
                'sector': r['ipo'].sector,
                'overall_score': r['analysis'].overall_score,
                'financial_score': r['analysis'].financial_score,
                'growth_score': r['analysis'].growth_score
            } for r in rankings]
            
            return Response({"rankings": data})


@method_decorator(login_required, name='dispatch')
class TechnicalIndicatorsAPI(APIView):
    """Technical indicators API."""
    
    def get(self, request, symbol):
        """Get technical indicators for a symbol."""
        # Get historical data
        period = request.GET.get('period', '1Y')
        historical = MarketDataService.fetch_historical_data(symbol, period)
        
        if not historical:
            return Response({
                "error": "No historical data available",
                "symbol": symbol
            })
        
        # Extract prices
        prices = [h['close'] for h in historical]
        dates = [h['date'] for h in historical]
        
        # Calculate indicators
        sma_20 = TechnicalIndicatorService.calculate_sma(prices, 20)
        sma_50 = TechnicalIndicatorService.calculate_sma(prices, 50)
        ema_12 = TechnicalIndicatorService.calculate_ema(prices, 12)
        ema_26 = TechnicalIndicatorService.calculate_ema(prices, 26)
        rsi = TechnicalIndicatorService.calculate_rsi(prices)
        macd = TechnicalIndicatorService.calculate_macd(prices)
        bollinger = TechnicalIndicatorService.calculate_bollinger_bands(prices)
        
        # Format response
        indicator_data = []
        for i, date in enumerate(dates):
            indicator_data.append({
                'date': date,
                'close': prices[i],
                'sma_20': sma_20[i] if i < len(sma_20) else None,
                'sma_50': sma_50[i] if i < len(sma_50) else None,
                'ema_12': ema_12[i] if i < len(ema_12) else None,
                'ema_26': ema_26[i] if i < len(ema_26) else None,
                'rsi': rsi[i] if i < len(rsi) else None,
                'macd': macd['macd'][i] if i < len(macd['macd']) else None,
                'macd_signal': macd['signal'][i] if i < len(macd['signal']) else None,
                'macd_histogram': macd['histogram'][i] if i < len(macd['histogram']) else None,
                'bb_upper': bollinger['upper'][i] if i < len(bollinger['upper']) else None,
                'bb_middle': bollinger['middle'][i] if i < len(bollinger['middle']) else None,
                'bb_lower': bollinger['lower'][i] if i < len(bollinger['lower']) else None
            })
        
        return Response({
            "symbol": symbol,
            "period": period,
            "indicators": indicator_data[-100:]  # Last 100 points
        })


@method_decorator(login_required, name='dispatch')
class RefreshMarketDataAPI(APIView):
    """Refresh market data for all IPOs."""
    
    def post(self, request):
        """Trigger market data refresh."""
        ipos = IPO.objects.all()
        result = MarketDataService.update_ipo_data(ipos)
        
        return Response({
            "success": result['success'],
            "failed": result['failed'],
            "skipped": result['skipped'],
            "message": "Market data refresh completed"
        })
