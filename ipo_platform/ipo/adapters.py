from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class IPOAccountAdapter(DefaultAccountAdapter):
    """Send first-time OAuth users to persona onboarding."""

    def get_login_redirect_url(self, request):
        profile = getattr(request.user, 'investor_profile', None)
        if profile is not None and not profile.onboarding_completed:
            return reverse('create_profile')
        return reverse('dashboard')
