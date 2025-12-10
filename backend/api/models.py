from django.db import models

class CropHealthCheck(models.Model):
    image_url = models.URLField()
    diagnosis = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=100, default="anonymous")

    def __str__(self):
        return f"Check {self.id} - {self.created_at}"

class VoiceQuery(models.Model):
    audio_url = models.URLField()
    transcribed_text = models.TextField(null=True, blank=True)
    ai_response = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
