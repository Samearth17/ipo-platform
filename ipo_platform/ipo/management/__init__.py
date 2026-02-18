from django.core.management.base import BaseCommand
from django.test import Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        client = Client()
        
        # Test GET
        response = client.get('/signup/')
        self.stdout.write(f"GET /signup/ Status: {response.status_code}")
        
        # Test POST
        response = client.post('/signup/', {
            'username': 'testuser999',
            'email': 'test999@example.com',
            'password1': 'Testpass123!@#',
            'password2': 'Testpass123!@#',
        })
        
        self.stdout.write(f"POST /signup/ Status: {response.status_code}")
        if response.status_code == 302:
            self.stdout.write(self.style.SUCCESS(f"✓ Redirect to: {response.url}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ No redirect (status {response.status_code})"))
