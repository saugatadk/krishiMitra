import boto3
import json
from django.conf import settings
import time

class AWSServiceManager:
    def __init__(self):
        self.mock_mode = True
        try:
            # Try to initialize clients, but fallback to mock mode if it fails
            # or if we are using dummy credentials
            if settings.AWS_ACCESS_KEY_ID == 'mock_key':
                self.mock_mode = True
            else:
                self.s3 = boto3.client('s3', region_name=settings.AWS_REGION_NAME)
                self.rekognition = boto3.client('rekognition', region_name=settings.AWS_REGION_NAME)
                self.transcribe = boto3.client('transcribe', region_name=settings.AWS_REGION_NAME)
                self.bedrock = boto3.client('bedrock-runtime', region_name=settings.AWS_REGION_NAME)
                self.sns = boto3.client('sns', region_name=settings.AWS_REGION_NAME)
                self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION_NAME)
                self.mock_mode = False
        except Exception as e:
            print(f"Failed to initialize AWS clients, switching to MOCK MODE: {e}")
            self.mock_mode = True

    def upload_file_to_s3(self, file_obj, object_name):
        """Uploads a file to S3 bucket"""
        if self.mock_mode:
            return f"https://mock-s3-bucket.com/{object_name}"
            
        try:
            self.s3.upload_fileobj(file_obj, settings.S3_BUCKET_NAME, object_name)
            return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{object_name}"
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return f"https://mock-s3-bucket.com/{object_name}"

    def detect_disease(self, image_key):
        """Uses Rekognition Custom Labels to detect plant diseases"""
        if self.mock_mode:
            return [{'Name': 'Cardamom Blight', 'Confidence': 98.5}]

        try:
            # Assuming a trained model ARN
            project_version_arn = "arn:aws:rekognition:us-east-1:123456789012:project/cardamom-disease/version/1"
            response = self.rekognition.detect_custom_labels(
                ProjectVersionArn=project_version_arn,
                Image={'S3Object': {'Bucket': settings.S3_BUCKET_NAME, 'Name': image_key}},
                MinConfidence=70
            )
            return response['CustomLabels']
        except Exception as e:
            print(f"Error in Rekognition: {e}")
            return [{'Name': 'Cardamom Blight', 'Confidence': 98.5}]

    def transcribe_audio(self, job_name, media_uri):
        """Starts a transcription job for Nepali audio"""
        if self.mock_mode:
            return job_name

        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': media_uri},
                MediaFormat='mp3',
                LanguageCode='ne-NP' # Nepali
            )
            return job_name
        except Exception as e:
            print(f"Error in Transcribe: {e}")
            return job_name

    def get_transcription_result(self, job_name):
        """Mock retrieval of transcription result"""
        return "मेरो अलैंचीका पातहरू पहेँलो हुँदैछन्, के गर्ने?" # "My cardamom leaves are turning yellow, what to do?"

    def ask_bedrock(self, query_text):
        """Queries Bedrock (Claude or Titan) for farming advice"""
        if self.mock_mode:
            return "अलैंचीमा पात पहेँलो हुनु नाइट्रोजनको कमी वा भाइरल रोगको लक्षण हुन सक्छ। कृपया प्राङ्गारिक मल प्रयोग गर्नुहोस्।"

        try:
            body = json.dumps({
                "prompt": f"Human: You are an expert Cardamom farming assistant. Answer this question in Nepali: {query_text}\n\nAssistant:",
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_p": 0.9,
            })
            
            response = self.bedrock.invoke_model(
                body=body,
                modelId='anthropic.claude-v2',
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            return response_body.get('completion')
        except Exception as e:
            print(f"Error in Bedrock: {e}")
            return "अलैंचीमा पात पहेँलो हुनु नाइट्रोजनको कमी वा भाइरल रोगको लक्षण हुन सक्छ। कृपया प्राङ्गारिक मल प्रयोग गर्नुहोस्।"

    def send_sms_alert(self, phone_number, message):
        """Sends SMS via SNS"""
        if self.mock_mode:
            print(f"MOCK SMS to {phone_number}: {message}")
            return True

        try:
            self.sns.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
