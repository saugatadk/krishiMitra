from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .aws_services import AWSServiceManager
from .models import CropHealthCheck, VoiceQuery
import uuid

aws_manager = AWSServiceManager()

class DiseaseDetectionView(APIView):
    def post(self, request):
        # In a real app, handle file upload properly
        # Here we assume the file is sent in request.FILES
        file_obj = request.FILES.get('image')
        if not file_obj:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Upload to S3
        file_name = f"crops/{uuid.uuid4()}.jpg"
        s3_url = aws_manager.upload_file_to_s3(file_obj, file_name)

        # 2. Call Rekognition
        diagnosis = aws_manager.detect_disease(file_name)

        # 3. Save to DB
        check = CropHealthCheck.objects.create(image_url=s3_url, diagnosis=diagnosis)

        # 4. Send SMS if critical (Mock logic)
        is_critical = any(d['Name'] == 'Severe Blight' and d['Confidence'] > 80 for d in diagnosis)
        if is_critical:
            aws_manager.send_sms_alert("+9779800000000", "Alert: Severe blight detected in your crop.")

        return Response({
            "id": check.id,
            "image_url": s3_url,
            "diagnosis": diagnosis,
            "alert_sent": is_critical
        })

class VoiceQueryView(APIView):
    def post(self, request):
        file_obj = request.FILES.get('audio')
        if not file_obj:
            return Response({"error": "No audio provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Upload Audio
        file_name = f"voice/{uuid.uuid4()}.mp3"
        s3_url = aws_manager.upload_file_to_s3(file_obj, file_name)

        # 2. Transcribe (Mocking the async flow for prototype)
        job_name = f"transcribe-{uuid.uuid4()}"
        aws_manager.transcribe_audio(job_name, s3_url)
        
        # In real life, we wait or use a callback. Here we mock the result immediately.
        transcribed_text = aws_manager.get_transcription_result(job_name)

        # 3. Ask Bedrock
        ai_response = aws_manager.ask_bedrock(transcribed_text)

        # 4. Save
        query = VoiceQuery.objects.create(
            audio_url=s3_url,
            transcribed_text=transcribed_text,
            ai_response=ai_response
        )

        return Response({
            "query_text": transcribed_text,
            "response": ai_response,
            "audio_url": s3_url
        })

class MarketPriceView(APIView):
    def get(self, request):
        # Mock data for market prices
        data = [
            {"market": "Birtamod", "price": 42000, "trend": "up"},
            {"market": "Taplejung", "price": 41500, "trend": "stable"},
            {"market": "Ilam", "price": 42200, "trend": "down"},
        ]
        return Response(data)
