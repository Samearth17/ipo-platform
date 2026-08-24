"""Insert the existing sample dataset with an explicit DEMO label."""
from .populate_db import Command as PopulateCommand

class Command(PopulateCommand):
    help = "Insert DEMO/SAMPLE IPO records from the bundled fixture."
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("DEMO/SAMPLE DATA ONLY — not live market data."))
        return super().handle(*args, **options)
