from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import IPO, Watchlist, InvestorProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_investor_profile(sender, instance, created, **kwargs):
    """Every account, including Google OAuth accounts, gets an isolated profile."""
    if created:
        InvestorProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=IPO)
def notify_new_ipo(sender, instance, created, **kwargs):
    if created:
        subject = f"New IPO Alert: {instance.company_name}"
        message = f"New IPO: {instance.company_name}\nStatus: {instance.get_status_display()}\nOpen Date: {instance.open_date}"
        
        emails = sorted(set(User.objects.exclude(email='').values_list('email', flat=True)))
        for email in emails:
            send_mail(subject, message, 'noreply@ipoplatform.com', [email], fail_silently=True)

@receiver(post_save, sender=IPO)
def notify_update(sender, instance, created, **kwargs):
    if not created:
        watchlists = Watchlist.objects.filter(ipos=instance).select_related('user')
        emails = sorted({w.user.email for w in watchlists if w.user.email})
        if emails:
            subject = f"IPO Update: {instance.company_name}"
            message = f"Update for {instance.company_name}.\nNew Status: {instance.get_status_display()}"
            for email in emails:
                send_mail(subject, message, 'noreply@ipoplatform.com', [email], fail_silently=True)
