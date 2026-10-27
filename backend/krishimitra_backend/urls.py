from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    return JsonResponse({
        "name": "KrishiMitra API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/api/health/",
            "disease_detect": "/api/disease-detect/",
            "voice_query": "/api/voice-query/",
            "market_prices": "/api/market-prices/",
            "admin": "/admin/",
        }
    })

urlpatterns = [
    path('', home, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
