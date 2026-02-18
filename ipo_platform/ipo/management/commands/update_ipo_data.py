from django.core.management.base import BaseCommand
from ipo.market_data_service import MarketDataService

class Command(BaseCommand):
    help = 'Update IPO data with real-time market data from Alpha Vantage'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating IPO data...')
        MarketDataService.update_ipo_data()
        self.stdout.write('IPO data update complete.')