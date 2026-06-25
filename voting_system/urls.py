"""Root URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('elections/', include('elections.urls', namespace='elections')),
    path('candidates/', include('candidates.urls', namespace='candidates')),
    path('votes/', include('votes.urls', namespace='votes')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('api/', include('dashboard.api_urls', namespace='api')),
    path('', include('accounts.urls', namespace='accounts_root')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
