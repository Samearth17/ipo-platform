import os
import subprocess
import sys
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from django.test import SimpleTestCase, TestCase, override_settings
from django.contrib.auth.models import User
from datetime import date
from .models import IPO

from .analytics.scoring import IPOScorer
from .prediction import train_and_predict
from .risk_assessment import RiskAssessor
from .portfolio_optimization import PortfolioOptimizer

def ipo(**overrides):
    values = dict(company_name="Test Co", symbol="TEST", roe=15, roa=8, revenue_growth=20,
                  debt_to_equity=.5, pe_ratio=20, market_cap=1000, issue_size=100,
                  volatility=20, listing_price=100, current_price=110, esg_score=70,
                  management_quality=70, brand_moat=60, lead_manager="N/A", listing_at="NSE")
    return SimpleNamespace(**{**values, **overrides})

class ScoringTests(SimpleTestCase):
    def test_scores_are_bounded_and_weighted(self):
        scores = IPOScorer(ipo()).get_all_scores()
        self.assertTrue(all(0 <= value <= 100 for key, value in scores.items() if key.endswith("score")))
        self.assertAlmostEqual(scores["overall_score"], 20*scores["financial_score"]*.01 + 15*scores["growth_score"]*.01 + 15*scores["valuation_score"]*.01 + 15*scores["risk_score"]*.01 + 10*scores["quality_score"]*.01 + 10*scores["momentum_score"]*.01 + 5*scores["esg_score"]*.01 + 10*scores["management_score"]*.01, places=1)
    def test_higher_volatility_reduces_risk_score(self):
        self.assertGreater(IPOScorer(ipo(volatility=10)).get_all_scores()["risk_score"], IPOScorer(ipo(volatility=70)).get_all_scores()["risk_score"])

class RiskTests(SimpleTestCase):
    def test_historical_metrics(self):
        assessment = RiskAssessor().assess_risk(ipo(), prices=[100, 102, 98, 101, 99, 103], market_prices=[100, 101, 99, 100, 98, 101])
        self.assertGreaterEqual(assessment.metrics.volatility, 0)
        self.assertGreaterEqual(assessment.metrics.VaR_99, assessment.metrics.VaR_95)
        self.assertGreaterEqual(assessment.metrics.max_drawdown, 0)

class PredictionTests(SimpleTestCase):
    def test_small_dataset_is_explicitly_experimental(self):
        self.assertFalse(train_and_predict([ipo()] * 3, ipo()).available)
    def test_held_out_metrics_are_generated(self):
        rows = [ipo(roe=10+i, current_price=105+i*2) for i in range(8)]
        result = train_and_predict(rows, rows[0])
        self.assertTrue(result.available)
        self.assertIn("mae", result.metrics)

class PortfolioTests(SimpleTestCase):
    def test_long_only_weights_sum_to_one(self):
        profile = SimpleNamespace(persona="moderate", max_investment=100000)
        result = PortfolioOptimizer(profile).optimize_portfolio([ipo(symbol="A"), ipo(symbol="B", volatility=35)], method="min_volatility")
        self.assertTrue(result["success"])
        weights = [item["weight"] for item in result["portfolio"]]
        self.assertAlmostEqual(sum(weights), 1, places=4)
        self.assertTrue(all(weight >= 0 for weight in weights))

class DjangoEndpointTests(TestCase):
    def setUp(self):
        self.ipo = IPO.objects.create(company_name="Endpoint Co", symbol="END", price_band="90-100", open_date=date.today(), close_date=date.today(), status="UPCOMING", issue_size=100, sector="Technology")
        self.user = User.objects.create_user(username="tester", password="password123")
        from .models import InvestorProfile
        InvestorProfile.objects.get_or_create(user=self.user)
    def test_public_pages_load(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/browse/").status_code, 200)
    def test_authenticated_detail_loads(self):
        self.client.login(username="tester", password="password123")
        self.assertEqual(self.client.get(f"/ipo/{self.ipo.pk}/").status_code, 200)

class MultiUserProductTests(TestCase):
    def setUp(self):
        self.ipo = IPO.objects.create(company_name='Research Co', symbol='RSCH', price_band='90-100', open_date=date.today(), close_date=date.today(), status='UPCOMING', issue_size=100, sector='Technology')
        self.user_a = User.objects.create_user(username='alice', password='password123', email='a@example.com')
        self.user_b = User.objects.create_user(username='bob', password='password123', email='b@example.com')
        self.profile_a = self.user_a.investor_profile
        self.profile_a.onboarding_completed = True; self.profile_a.save()

    def test_protected_dashboard_and_profile_onboarding(self):
        self.assertEqual(self.client.get('/dashboard/').status_code, 302)
        self.client.login(username='alice', password='password123')
        self.assertEqual(self.client.get('/dashboard/').status_code, 200)
        self.client.post('/profile/', {'persona':'growth', 'investment_horizon':'medium', 'risk_tolerance':5, 'min_investment':10000, 'max_investment':100000})
        self.profile_a.refresh_from_db(); self.assertEqual(self.profile_a.persona, 'growth')

    def test_watchlist_mutation_and_isolation(self):
        self.client.login(username='alice', password='password123')
        self.assertEqual(self.client.post(f'/watchlist/add/{self.ipo.pk}/').status_code, 302)
        self.assertEqual(self.user_a.watchlist.ipos.count(), 1)
        self.client.post(f'/watchlist/add/{self.ipo.pk}/')
        self.assertEqual(self.user_a.watchlist.ipos.count(), 1)
        self.client.logout(); self.client.login(username='bob', password='password123')
        self.assertEqual(self.client.get('/watchlist/').status_code, 200)
        self.assertEqual(self.client.post(f'/watchlist/remove/{self.ipo.pk}/').status_code, 302)
        self.assertEqual(self.user_a.watchlist.ipos.count(), 1)

    def test_saved_portfolio_isolation_and_deletion(self):
        from .models import SavedPortfolio
        portfolio = SavedPortfolio.objects.create(user=self.user_a, name='Alice only', investor_persona='balanced', optimization_method='equal_weight', allocations=[], metrics={})
        self.client.login(username='bob', password='password123')
        self.assertEqual(self.client.get(f'/portfolio/saved/{portfolio.pk}/').status_code, 404)
        self.assertEqual(self.client.post(f'/portfolio/saved/{portfolio.pk}/delete/').status_code, 404)
        self.assertTrue(SavedPortfolio.objects.filter(pk=portfolio.pk).exists())
        self.client.logout(); self.client.login(username='alice', password='password123')
        self.assertEqual(self.client.post(f'/portfolio/saved/{portfolio.pk}/delete/').status_code, 302)
        self.assertFalse(SavedPortfolio.objects.filter(pk=portfolio.pk).exists())

    def test_legal_pages_are_public(self):
        for url in ('/about/', '/how-it-works/', '/terms/', '/privacy/', '/disclaimer/', '/contact/'):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_login_page_and_google_route_load_without_credentials(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="google-login"')
        self.assertContains(response, 'href="/accounts/google/login/"')
        self.assertNotContains(response, 'action="/accounts/google/login/"')
        self.assertContains(response, 'id="password-login-form"')
        self.assertEqual(self.client.get('/accounts/google/login/').status_code, 200)

    @override_settings(SOCIALACCOUNT_PROVIDERS={'google': {'APP': {'client_id': 'test-client-id', 'secret': 'test-secret', 'key': ''}, 'SCOPE': ['openid', 'email', 'profile']}})
    def test_google_provider_credentials_are_used_to_build_authorization_url(self):
        from django.conf import settings
        provider = settings.SOCIALACCOUNT_PROVIDERS['google']
        self.assertIn('client_id', provider['APP'])
        self.assertTrue(provider['APP']['client_id'])
        self.client.get('/accounts/google/login/', HTTP_HOST='127.0.0.1:8000')
        response = self.client.post('/accounts/google/login/', HTTP_HOST='127.0.0.1:8000')
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlparse(response['Location']).query)
        self.assertEqual(query['client_id'], ['test-client-id'])
        self.assertEqual(query['redirect_uri'], ['http://127.0.0.1:8000/accounts/google/login/callback/'])

    def test_production_settings_populate_google_provider_from_environment(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env.update({
            'DJANGO_SETTINGS_MODULE': 'ipo_platform.settings_production',
            'SECRET_KEY': 'test-production-secret-key',
            'DATABASE_URL': 'postgresql://user:password@localhost/ipo_test',
            'ALLOWED_HOSTS': 'test.onrender.com',
            'GOOGLE_CLIENT_ID': 'test-production-client-id',
            'GOOGLE_CLIENT_SECRET': 'test-production-client-secret',
        })
        script = (
            'from ipo_platform import settings_production as s; '
            "assert s.GOOGLE_CLIENT_ID == 'test-production-client-id'; "
            "assert s.GOOGLE_CLIENT_SECRET == 'test-production-client-secret'; "
            "assert s.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'] == s.GOOGLE_CLIENT_ID; "
            "assert s.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'] == s.GOOGLE_CLIENT_SECRET"
        )
        result = subprocess.run(
            [sys.executable, '-c', script], cwd=project_root, env=env,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('test-production-client-secret', result.stdout + result.stderr)

    def test_production_settings_fail_clearly_when_google_credentials_are_missing(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env.update({
            'DJANGO_SETTINGS_MODULE': 'ipo_platform.settings_production',
            'SECRET_KEY': 'test-production-secret-key',
            'DATABASE_URL': 'postgresql://user:password@localhost/ipo_test',
            'ALLOWED_HOSTS': 'test.onrender.com',
            'GOOGLE_CLIENT_ID': '',
            'GOOGLE_CLIENT_SECRET': '',
        })
        result = subprocess.run(
            [sys.executable, '-c', 'import ipo_platform.settings_production'],
            cwd=project_root, env=env, capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('GOOGLE_CLIENT_ID', result.stderr)
        self.assertIn('GOOGLE_CLIENT_SECRET', result.stderr)

    def test_signup_exposes_independent_google_link_and_light_theme(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="google-signup"')
        self.assertContains(response, 'href="/accounts/google/login/"')
        self.assertNotContains(response, 'theme-toggle')
        self.assertNotContains(response, 'ipo-theme')
