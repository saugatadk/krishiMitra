from django.db import models


class MarketCenter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    district = models.CharField(max_length=100)
    location_notes = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.district})"


class CardamomPrice(models.Model):
    TREND_CHOICES = [
        ('up', 'Up'),
        ('down', 'Down'),
        ('stable', 'Stable'),
    ]

    market = models.ForeignKey(MarketCenter, on_delete=models.CASCADE, related_name='prices')
    variety = models.CharField(max_length=50, default='Jhirse')
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_man = models.DecimalField(max_digits=10, decimal_places=2, help_text="40kg rate in NPR")
    trend = models.CharField(max_length=10, choices=TREND_CHOICES, default='stable')
    change_percentage = models.CharField(max_length=20, default='0.0%')
    recorded_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_date', 'market__name']

    def __str__(self):
        return f"{self.market.name} - {self.variety}: NPR {self.price_per_kg}/kg ({self.recorded_date})"


class CropDiagnosis(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ]

    image = models.ImageField(upload_to='crops/%Y/%m/%d/')
    disease_name = models.CharField(max_length=150)
    disease_name_nepali = models.CharField(max_length=150)
    scientific_name = models.CharField(max_length=150, blank=True)
    confidence = models.FloatField(default=0.0)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Moderate')
    treatment_plan = models.JSONField(default=list)
    prevention_tips = models.JSONField(default=list)
    expected_recovery = models.CharField(max_length=100, default='2-3 weeks')
    alert_sent = models.BooleanField(default=False)
    annotated_image = models.ImageField(upload_to='crops/annotated/%Y/%m/%d/', blank=True, null=True)
    bounding_boxes = models.JSONField(default=list)
    lesion_count = models.IntegerField(default=0)
    affected_area_percentage = models.FloatField(default=0.0)
    detection_model = models.CharField(max_length=50, default='YOLOv8n-Cardamom')
    user_id = models.CharField(max_length=100, default='farmer-local')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.disease_name} ({self.confidence:.1f}%) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class VoiceConsultation(models.Model):
    audio = models.FileField(upload_to='voice/%Y/%m/%d/')
    transcribed_text = models.TextField(blank=True)
    ai_response = models.TextField(blank=True)
    response_audio = models.FileField(upload_to='audio_responses/%Y/%m/%d/', blank=True, null=True)
    user_id = models.CharField(max_length=100, default='farmer-local')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        snippet = self.transcribed_text[:30] if self.transcribed_text else "Audio Query"
        return f"{snippet} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
