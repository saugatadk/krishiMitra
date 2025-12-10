from django.urls import path
from .views import DiseaseDetectionView, VoiceQueryView, MarketPriceView

urlpatterns = [
    path('disease-detect/', DiseaseDetectionView.as_view(), name='disease-detect'),
    path('voice-query/', VoiceQueryView.as_view(), name='voice-query'),
    path('market-prices/', MarketPriceView.as_view(), name='market-prices'),
]
