from rest_framework import serializers
from .models import MarketCenter, CardamomPrice, CropDiagnosis, VoiceConsultation


class MarketCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCenter
        fields = ['id', 'name', 'district', 'location_notes', 'is_active']


class CardamomPriceSerializer(serializers.ModelSerializer):
    market_name = serializers.CharField(source='market.name', read_only=True)
    district = serializers.CharField(source='market.district', read_only=True)

    class Meta:
        model = CardamomPrice
        fields = [
            'id',
            'market',
            'market_name',
            'district',
            'variety',
            'price_per_kg',
            'price_per_man',
            'trend',
            'change_percentage',
            'recorded_date',
        ]


class CropDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropDiagnosis
        fields = [
            'id',
            'image',
            'annotated_image',
            'disease_name',
            'disease_name_nepali',
            'scientific_name',
            'confidence',
            'severity',
            'treatment_plan',
            'prevention_tips',
            'expected_recovery',
            'bounding_boxes',
            'lesion_count',
            'affected_area_percentage',
            'detection_model',
            'alert_sent',
            'created_at',
        ]
        read_only_fields = [
            'annotated_image',
            'disease_name',
            'disease_name_nepali',
            'scientific_name',
            'confidence',
            'severity',
            'treatment_plan',
            'prevention_tips',
            'expected_recovery',
            'bounding_boxes',
            'lesion_count',
            'affected_area_percentage',
            'detection_model',
            'alert_sent',
            'created_at',
        ]


class VoiceConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceConsultation
        fields = [
            'id',
            'audio',
            'transcribed_text',
            'ai_response',
            'response_audio',
            'created_at',
        ]
        read_only_fields = [
            'transcribed_text',
            'ai_response',
            'response_audio',
            'created_at',
        ]
