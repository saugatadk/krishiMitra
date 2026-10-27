from django.urls import path
from .views import (
    HealthCheckView,
    DiseaseDetectionView,
    DiseaseSyncView,
    VoiceQueryView,
    MarketPriceView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('disease-detect/', DiseaseDetectionView.as_view(), name='disease-detect'),
    path('disease-detect/sync/', DiseaseSyncView.as_view(), name='disease-detect-sync'),
    path('voice-query/', VoiceQueryView.as_view(), name='voice-query'),
    path('market-prices/', MarketPriceView.as_view(), name='market-prices'),
]
