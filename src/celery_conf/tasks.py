import resend
from twilio.rest import Client
from celery import shared_task
from src.config.settings import settings

import logging


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, params: dict):
    """Задача для отправки email через Celery"""
    try:
        resend.api_key = settings.resend_api_key
        response = resend.Emails.send(params)
        logger.info(f"Email sent to {params['to']}, response: {response}")
        return {"status": "success", "email": params['to']}
        
    except Exception as e:
        logger.error(f"Failed to send email from celery to {params['to']}: {e}")
        self.retry(exc=e, countdown=30)


@shared_task(bind=True, max_retries=3)
def send_sms_task(self, params: dict):
    """Задача для отправки SMS через Celery"""
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        message = client.messages.create(**params)
        
        logger.info(f"SMS sent to {params['to']}, message SID: {message.sid}")
        return {"status": "success", "phone": params['to']}
        
    except Exception as e:
        logger.error(f"Failed to send SMS to {params['to']}: {e}")
        self.retry(exc=e, countdown=30)