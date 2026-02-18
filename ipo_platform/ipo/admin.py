from django.contrib import admin
from .models import IPO, Company, InvestorProfile, Recommendation, PortfolioRecommendation, Watchlist

@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'sector', 'status', 'listing_date', 'lead_manager')
    list_filter = ('status', 'sector', 'created_at')
    search_fields = ('company_name', 'sector', 'lead_manager')
    ordering = ('-open_date',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead_manager', 'created_at')
    search_fields = ('name', 'lead_manager')

@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'persona', 'risk_tolerance', 'portfolio_value')
    list_filter = ('persona', 'risk_tolerance')
    search_fields = ('user__username',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('ipo', 'investor_profile', 'rating', 'overall_score')
    list_filter = ('rating', 'created_at')
    search_fields = ('ipo__company_name', 'investor_profile__user__username')
    ordering = ('-overall_score',)

@admin.register(PortfolioRecommendation)
class PortfolioRecommendationAdmin(admin.ModelAdmin):
    list_display = ('investor_profile', 'total_allocation', 'diversification_score')
    list_filter = ('created_at',)
    search_fields = ('investor_profile__user__username',)

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
