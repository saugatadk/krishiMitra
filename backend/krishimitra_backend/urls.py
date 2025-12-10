from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        "message": "Welcome to Krishimitra API",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/"
        }
    })

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
