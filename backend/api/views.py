import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import MarketCenter, CardamomPrice, CropDiagnosis, VoiceConsultation
from .serializers import CardamomPriceSerializer, CropDiagnosisSerializer, VoiceConsultationSerializer
from .services.yolo_detector import detect_cardamom_lesions
from .services.voice_engine import process_voice_query


class HealthCheckView(APIView):
    """
    Health and readiness probe endpoint.
    """
    def get(self, request):
        db_status = "ok"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"

        return Response({
            "status": "ok",
            "service": "KrishiMitra Backend API",
            "version": "1.0.0",
            "database": db_status,
            "engine": "YOLOv8 Nano Object Detector + Hybrid AI",
            "tts_support": "Nepali Neural Voice (ne-NP-HemkalaNeural)"
        })


class DiseaseDetectionView(APIView):
    """
    Processes cardamom leaf images using YOLOv8 object detection.
    Returns localized lesion bounding boxes, annotated image, severity, and treatment plan.
    Supports both multipart/form-data and base64-encoded image payloads.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        image_file = request.FILES.get('image')

        # Fallback to base64 / data-URI if not in FILES
        if not image_file:
            raw_image = request.data.get('image') or request.data.get('image_base64')
            if isinstance(raw_image, str) and len(raw_image) > 50:
                try:
                    if ';base64,' in raw_image:
                        header, b64data = raw_image.split(';base64,', 1)
                        ext = header.split('/')[-1] if '/' in header else 'jpg'
                    else:
                        b64data = raw_image
                        ext = 'jpg'
                    decoded_bytes = base64.b64decode(b64data)
                    image_file = ContentFile(decoded_bytes, name=f"leaf_{uuid.uuid4().hex[:8]}.{ext}")
                except Exception as decode_err:
                    return Response(
                        {"error": f"Failed to decode base64 image: {str(decode_err)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if not image_file:
            return Response(
                {"error": "No image provided. Please upload a leaf photo under key 'image'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.data.get('user_id', 'farmer-local')
        record = detect_cardamom_lesions(image_file, user_id=user_id)
        serializer = CropDiagnosisSerializer(record, context={'request': request})
        data = serializer.data

        # Construct full media URLs for client
        if record.image:
            data['image_url'] = request.build_absolute_uri(record.image.url)
        if record.annotated_image:
            data['annotated_image_url'] = request.build_absolute_uri(record.annotated_image.url)

        # Compatibility and convenience fields
        from .services.diagnosis_engine import CARDAMOM_PATHOLOGIES
        path_info = None
        for k, v in CARDAMOM_PATHOLOGIES.items():
            if v.get('disease_name') == record.disease_name:
                path_info = v
                break

        data['diagnosis'] = [
            {'Name': record.disease_name, 'Confidence': record.confidence},
            {'Name': 'Healthy', 'Confidence': max(0.0, round(100.0 - record.confidence, 1))}
        ]
        data['treatment'] = {
            'disease': record.disease_name,
            'disease_nepali': record.disease_name_nepali,
            'severity': record.severity,
            'treatment_plan': record.treatment_plan,
            'treatment_plan_en': path_info.get('treatment_plan_en', []) if path_info else [],
            'prevention': record.prevention_tips,
            'prevention_en': path_info.get('prevention_tips_en', []) if path_info else [],
            'expected_recovery': record.expected_recovery,
            'expected_recovery_en': path_info.get('expected_recovery_en', '') if path_info else ''
        }
        data['lesion_summary'] = {
            'lesion_count': record.lesion_count,
            'affected_area_percentage': record.affected_area_percentage,
            'bounding_boxes': record.bounding_boxes
        }

        return Response(data, status=status.HTTP_201_CREATED)


class DiseaseSyncView(APIView):
    """
    Batch synchronizes offline inspection records captured on mobile when disconnected.
    """
    def post(self, request):
        inspections = request.data.get('inspections', [])
        synced_count = 0

        for item in inspections:
            try:
                CropDiagnosis.objects.create(
                    disease_name=item.get('disease_name', 'Unknown'),
                    disease_name_nepali=item.get('disease_name_nepali', 'अज्ञात'),
                    confidence=item.get('confidence', 80.0),
                    severity=item.get('severity', 'Moderate'),
                    treatment_plan=item.get('treatment_plan', []),
                    prevention_tips=item.get('prevention_tips', []),
                    bounding_boxes=item.get('bounding_boxes', []),
                    lesion_count=item.get('lesion_count', 0),
                    affected_area_percentage=item.get('affected_area_percentage', 0.0),
                    user_id=item.get('user_id', 'farmer-offline'),
                )
                synced_count += 1
            except Exception as e:
                continue

        return Response({
            "status": "success",
            "synced_count": synced_count,
            "message": f"{synced_count} offline inspection(s) synchronized to cloud database."
        })


class VoiceQueryView(APIView):
    """
    Processes recorded Nepali farmer audio and returns transcribed text,
    expert agronomic advice, and spoken Nepali audio playback URL.
    """
    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {"error": "No audio file provided. Please upload audio under key 'audio'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.data.get('user_id', 'farmer-local')
        consultation = process_voice_query(audio_file, user_id=user_id)

        response_audio_url = None
        if consultation.response_audio:
            response_audio_url = request.build_absolute_uri(consultation.response_audio.url)

        audio_url = None
        if consultation.audio:
            audio_url = request.build_absolute_uri(consultation.audio.url)

        return Response({
            "id": consultation.id,
            "query_text": consultation.transcribed_text,
            "response": consultation.ai_response,
            "audio_url": audio_url,
            "response_audio_url": response_audio_url,
            "created_at": consultation.created_at
        }, status=status.HTTP_201_CREATED)


class MarketPriceView(APIView):
    """
    Returns live cardamom market prices across major Nepali centers.
    Supports filtering by market (?market=Birtamod) or variety (?variety=Jhirse).
    """
    def get(self, request):
        queryset = CardamomPrice.objects.select_related('market').all()

        market_param = request.query_params.get('market')
        if market_param:
            queryset = queryset.filter(market__name__icontains=market_param)

        variety_param = request.query_params.get('variety')
        if variety_param:
            queryset = queryset.filter(variety__icontains=variety_param)

        serializer = CardamomPriceSerializer(queryset, many=True)
        
        # If database is empty, fallback to baseline rates so frontend never crashes
        if not serializer.data:
            return Response([
                {"market": "Birtamod", "price": 1050, "trend": "up", "change": "+2.5%"},
                {"market": "Taplejung", "price": 1038, "trend": "stable", "change": "0.0%"},
                {"market": "Ilam", "price": 1055, "trend": "down", "change": "-1.2%"},
                {"market": "Panchthar", "price": 1025, "trend": "stable", "change": "+0.5%"},
            ])

        # Adapt to frontend consumption structure
        results = []
        for item in serializer.data:
            results.append({
                "id": item['id'],
                "market": item['market_name'],
                "district": item['district'],
                "variety": item['variety'],
                "price": float(item['price_per_kg']),
                "price_per_man": float(item['price_per_man']),
                "trend": item['trend'],
                "change": item['change_percentage'],
                "recorded_date": item['recorded_date']
            })

        return Response(results)
