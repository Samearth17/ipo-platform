from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('ipo.urls')),
]

handler404 = 'ipo.views.error_404'
handler403 = 'ipo.views.error_403'
handler500 = 'ipo.views.error_500'
