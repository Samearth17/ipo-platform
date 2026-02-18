from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import IPO, Watchlist
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=IPO)
def notify_new_ipo(sender, instance, created, **kwargs):
    if created:
        subject = f"New IPO Alert: {instance.company_name}"
        message = f"New IPO: {instance.company_name}\nStatus: {instance.get_status_display()}\nOpen Date: {instance.open_date}"
        
        users = User.objects.exclude(email='').values_list('email', flat=True)
        if users:
            send_mail(subject, message, 'noreply@ipoplatform.com', list(users), fail_silently=True)

@receiver(post_save, sender=IPO)
def notify_update(sender, instance, created, **kwargs):
    if not created:
        watchlists = Watchlist.objects.filter(ipos=instance).select_related('user')
        emails = [w.user.email for w in watchlists if w.user.email]
        if emails:
            subject = f"IPO Update: {instance.company_name}"
            message = f"Update for {instance.company_name}.\nNew Status: {instance.get_status_display()}"
            send_mail(subject, message, 'noreply@ipoplatform.com', emails, fail_silently=True)
