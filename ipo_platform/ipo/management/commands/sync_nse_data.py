"""
Django management command to sync IPO data from NSE India.
Usage: python manage.py sync_nse_data [--current] [--upcoming] [--past] [--all]
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from ipo.models import IPO
from ipo.nse_service import NSEIPOService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync IPO data from NSE India API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--current',
            action='store_true',
            help='Sync only current/ongoing IPOs',
        )
        parser.add_argument(
            '--upcoming',
            action='store_true',
            help='Sync only upcoming IPOs',
        )
        parser.add_argument(
            '--past',
            action='store_true',
            help='Sync only past/listed IPOs',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all IPO categories (default)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting NSE IPO data sync...'))
        
        nse_service = NSEIPOService()
        
        # Determine which categories to sync
        sync_current = options['current'] or options['all'] or not any([
            options['current'], options['upcoming'], options['past']
        ])
        sync_upcoming = options['upcoming'] or options['all'] or not any([
            options['current'], options['upcoming'], options['past']
        ])
        sync_past = options['past'] or options['all'] or not any([
            options['current'], options['upcoming'], options['past']
        ])
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        # Sync current IPOs
        if sync_current:
            self.stdout.write('Fetching current IPOs...')
            created, updated, errors = self._sync_category(nse_service.fetch_current_ipos())
            total_created += created
            total_updated += updated
            total_errors += errors
        
        # Sync upcoming IPOs
        if sync_upcoming:
            self.stdout.write('Fetching upcoming IPOs...')
            created, updated, errors = self._sync_category(nse_service.fetch_upcoming_ipos())
            total_created += created
            total_updated += updated
            total_errors += errors
        
        # Sync past IPOs
        if sync_past:
            self.stdout.write('Fetching past IPOs...')
            created, updated, errors = self._sync_category(nse_service.fetch_past_ipos())
            total_created += created
            total_updated += updated
            total_errors += errors
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Sync complete!'))
        self.stdout.write(f'  Created: {total_created}')
        self.stdout.write(f'  Updated: {total_updated}')
        if total_errors > 0:
            self.stdout.write(self.style.WARNING(f'  Errors: {total_errors}'))

    def _sync_category(self, ipos_data):
        """Sync a category of IPOs to database."""
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for ipo_data in ipos_data:
            try:
                with transaction.atomic():
                    # Try to find existing IPO by company name or symbol
                    existing_ipo = IPO.objects.filter(
                        company_name__iexact=ipo_data['company_name']
                    ).first()
                    
                    if existing_ipo:
                        # Update existing IPO
                        self._update_ipo(existing_ipo, ipo_data)
                        updated_count += 1
                        self.stdout.write(f'  ↻ Updated: {ipo_data["company_name"]}')
                    else:
                        # Create new IPO
                        self._create_ipo(ipo_data)
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {ipo_data["company_name"]}')
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error with {ipo_data.get("company_name", "Unknown")}: {e}')
                )
                logger.error(f'Error syncing IPO: {e}', exc_info=True)
        
        return created_count, updated_count, error_count

    def _create_ipo(self, data):
        """Create new IPO from NSE data."""
        IPO.objects.create(
            company_name=data['company_name'],
            symbol=data.get('symbol'),
            status=data['status'],
            open_date=data.get('open_date'),
            close_date=data.get('close_date'),
            listing_date=data.get('listing_date'),
            price_band_lower=data.get('price_band_lower'),
            price_band_upper=data.get('price_band_upper'),
            issue_size=data.get('issue_size'),
            listing_at=data.get('listing_at', 'NSE'),
            lead_manager=data.get('lead_manager', ''),
            registrar=data.get('registrar', ''),
            sector=data.get('sector', 'General'),
            lot_size=data.get('lot_size'),
            listing_price=data.get('listing_price'),
            # Set reasonable defaults for financial metrics
            pe_ratio=15.0,
            roe=12.0,
            debt_to_equity=0.5,
            volatility=25.0,
        )

    def _update_ipo(self, ipo, data):
        """Update existing IPO with NSE data."""
        # Update fields that might have changed
        if data.get('status'):
            ipo.status = data['status']
        if data.get('open_date'):
            ipo.open_date = data['open_date']
        if data.get('close_date'):
            ipo.close_date = data['close_date']
        if data.get('listing_date'):
            ipo.listing_date = data['listing_date']
        if data.get('price_band_lower'):
            ipo.price_band_lower = data['price_band_lower']
        if data.get('price_band_upper'):
            ipo.price_band_upper = data['price_band_upper']
        if data.get('listing_price'):
            ipo.listing_price = data['listing_price']
        if data.get('lot_size'):
            ipo.lot_size = data['lot_size']
        
        ipo.save()
