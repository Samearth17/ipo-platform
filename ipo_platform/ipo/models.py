from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class IPO(models.Model):
    STATUS_CHOICES = [('UPCOMING', 'Upcoming'), ('ONGOING', 'Ongoing'), ('LISTED', 'Listed')]
    company_name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=20, blank=True, null=True, help_text="Stock symbol/ticker")
    price_band = models.CharField(max_length=50)
    open_date = models.DateField()
    close_date = models.DateField()
    listing_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    issue_size = models.DecimalField(max_digits=12, decimal_places=2)
    sector = models.CharField(max_length=100)
    lead_manager = models.CharField(max_length=255, default='N/A')
    listing_at = models.CharField(max_length=50, default='NSE')
    listing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    roa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volatility = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    revenue_growth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True)
    price_band_lower = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_band_upper = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Human Traits / Qualitative Metrics
    esg_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    management_quality = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    brand_moat = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.company_name
    class Meta:
        ordering = ['-open_date']

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    lead_manager = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class InvestorProfile(models.Model):
    PERSONA_CHOICES = [('conservative', 'Conservative'), ('moderate', 'Moderate / Balanced'), ('balanced', 'Balanced'), ('growth', 'Growth'), ('aggressive', 'Aggressive')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')
    persona = models.CharField(max_length=20, choices=PERSONA_CHOICES, default='moderate')
    min_investment = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    max_investment = models.DecimalField(max_digits=12, decimal_places=2, default=1000000)
    preferred_sectors = models.CharField(max_length=500, blank=True)
    risk_tolerance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=5)
    investment_horizon = models.CharField(max_length=20, choices=[('short', 'Short-term'), ('medium', 'Medium-term'), ('long', 'Long-term')], default='medium')
    portfolio_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    years_investing = models.IntegerField(default=0)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.username} - {self.persona}"
    def get_risk_parameters(self):
        if self.persona == 'conservative':
            return {'max_volatility': 15.0, 'max_debt_to_equity': 0.5, 'min_roe': 10.0}
        elif self.persona in ('moderate', 'balanced'):
            return {'max_volatility': 25.0, 'max_debt_to_equity': 1.5, 'min_roe': 8.0}
        elif self.persona == 'growth':
            return {'max_volatility': 35.0, 'max_debt_to_equity': 2.5, 'min_roe': 6.0}
        else:
            return {'max_volatility': 40.0, 'max_debt_to_equity': 3.0, 'min_roe': 5.0}
    def get_persona_strategy(self):
        strategies = {
            'conservative': {'name': 'Conservative Growth', 'target_allocation': {'blue_chip': 60, 'mid_cap': 30, 'emerging': 10}, 'min_rating_threshold': 70},
            'moderate': {'name': 'Balanced Growth', 'target_allocation': {'blue_chip': 40, 'mid_cap': 40, 'emerging': 20}, 'min_rating_threshold': 55},
            'balanced': {'name': 'Balanced Risk-Adjusted', 'target_allocation': {'blue_chip': 40, 'mid_cap': 40, 'emerging': 20}, 'min_rating_threshold': 55},
            'growth': {'name': 'Growth with Risk Guardrails', 'target_allocation': {'blue_chip': 25, 'mid_cap': 40, 'emerging': 35}, 'min_rating_threshold': 50},
            'aggressive': {'name': 'Growth Maximization', 'target_allocation': {'blue_chip': 20, 'mid_cap': 40, 'emerging': 40}, 'min_rating_threshold': 40}
        }
        return strategies.get(self.persona, strategies['moderate'])
    def get_persona_display_custom(self):
        return self.get_persona_display()
    def update_persona(self):
        # Dynamically update persona based on risk tolerance and years of investing
        if self.risk_tolerance <= 3 and self.years_investing < 3:
            self.persona = 'conservative'
        elif self.risk_tolerance >= 7 or self.years_investing > 5:
            self.persona = 'aggressive'
        else:
            self.persona = 'moderate'
        self.save()

class Recommendation(models.Model):
    RATING_CHOICES = [('STRONG_BUY', 'Strong Buy'), ('BUY', 'Buy'), ('HOLD', 'Hold'), ('SELL', 'Sell'), ('STRONG_SELL', 'Strong Sell')]
    investor_profile = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name='recommendations')
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name='recommendations')
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    financial_score = models.FloatField()
    risk_score = models.FloatField()
    growth_score = models.FloatField()
    overall_score = models.FloatField()
    weight = models.FloatField(default=0.0)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    rationale = models.TextField()
    human_insight = models.TextField(blank=True, null=True, help_text="A more personal, advisor-like explanation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.ipo.company_name} - {self.rating}"
    class Meta:
        unique_together = ('investor_profile', 'ipo')
        ordering = ['-overall_score']

class PortfolioRecommendation(models.Model):
    investor_profile = models.OneToOneField(InvestorProfile, on_delete=models.CASCADE, related_name='portfolio_recommendation')
    top_recommendations = models.ManyToManyField(Recommendation, related_name='in_portfolios')
    total_allocation = models.DecimalField(max_digits=12, decimal_places=2, default=100000)
    expected_return = models.FloatField(default=0.0)
    portfolio_risk = models.FloatField(default=0.0)
    diversification_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Portfolio - {self.investor_profile.user.username}"

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='watchlist')
    ipos = models.ManyToManyField(IPO, related_name='watchlisted_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Watchlist - {self.user.username}"
    class Meta:
        verbose_name_plural = "Watchlists"


class SavedPortfolio(models.Model):
    """A user-owned snapshot of a generated portfolio, safe to retain over time."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_portfolios')
    name = models.CharField(max_length=120)
    investor_persona = models.CharField(max_length=20, choices=InvestorProfile.PERSONA_CHOICES)
    optimization_method = models.CharField(max_length=40)
    allocations = models.JSONField(default=list)
    metrics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.user.username}"
