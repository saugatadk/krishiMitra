import io
from PIL import Image
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import MarketCenter, CardamomPrice, CropDiagnosis, VoiceConsultation


class BackendAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Seed test market center and price
        self.market = MarketCenter.objects.create(name='Birtamod', district='Jhapa')
        self.price = CardamomPrice.objects.create(
            market=self.market,
            variety='Jhirse',
            price_per_kg=1050.00,
            price_per_man=42000.00,
            trend='up',
            change_percentage='+2.5%',
            recorded_date='2026-10-27'
        )

    def test_health_check(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'ok')
        self.assertEqual(response.data.get('database'), 'ok')

    def test_market_prices(self):
        response = self.client.get('/api/market-prices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        item = response.data[0]
        self.assertEqual(item['market'], 'Birtamod')
        self.assertEqual(item['price'], 1050.0)
        self.assertEqual(item['trend'], 'up')

    def test_disease_detection_no_image(self):
        response = self.client.post('/api/disease-detect/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disease_detection_yolo_success(self):
        # Create a synthetic test leaf image with blight patch
        img = Image.new('RGB', (160, 160), color=(40, 140, 40))
        # Draw prominent brown necrotic lesion patch
        for x in range(20, 140):
            for y in range(20, 140):
                img.putpixel((x, y), (160, 80, 20))

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        img_bytes.name = 'cardamom_blight_leaf.jpg'

        response = self.client.post(
            '/api/disease-detect/',
            {'image': img_bytes},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('diagnosis', response.data)
        self.assertIn('treatment', response.data)
        self.assertIn('disease_name', response.data)
        self.assertIn('disease_name_nepali', response.data)
        self.assertIn('bounding_boxes', response.data)
        self.assertIn('lesion_summary', response.data)
        self.assertIn('annotated_image_url', response.data)
        self.assertTrue(CropDiagnosis.objects.exists())
        record = CropDiagnosis.objects.first()
        self.assertTrue(len(record.bounding_boxes) >= 1)

    def test_disease_offline_sync(self):
        payload = {
            "inspections": [
                {
                    "disease_name": "Cardamom Leaf Blight",
                    "disease_name_nepali": "अलैंची पात डढुवा",
                    "confidence": 89.5,
                    "severity": "Moderate",
                    "treatment_plan": ["कपर अक्सिक्लोराइड २ ग्राम छर्कनुहोस्"],
                    "prevention_tips": ["पानी जम्न नदिनुहोस्"],
                    "bounding_boxes": [{"x1": 50, "y1": 50, "x2": 120, "y2": 120}],
                    "lesion_count": 1,
                    "affected_area_percentage": 14.5,
                    "user_id": "farmer-offline"
                }
            ]
        }
        response = self.client.post('/api/disease-detect/sync/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('synced_count'), 1)
        self.assertEqual(response.data.get('status'), 'success')

    def test_voice_query_no_audio(self):
        response = self.client.post('/api/voice-query/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_voice_query_success(self):
        audio_bytes = io.BytesIO(b'RIFF....WAVEfmt ....data....')
        audio_bytes.name = 'query.wav'

        response = self.client.post(
            '/api/voice-query/',
            {'audio': audio_bytes},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('query_text', response.data)
        self.assertIn('response', response.data)
        self.assertTrue(VoiceConsultation.objects.exists())
