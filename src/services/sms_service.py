import logging
from abc import ABC, abstractmethod
from twilio.rest import Client
from src.config.settings import settings
from src.celery_conf.tasks import send_sms_task

logger = logging.getLogger(__name__)

class AbstractSMSService(ABC):
    @abstractmethod
    def send_confirmation_sms(self, phone: str, confirmation_code: str) -> bool:
        raise NotImplementedError()

class TwilioSMSService(AbstractSMSService):
    def __init__(self, account_sid: str, auth_token: str, from_phone: str):
        self.client = Client(account_sid, auth_token)
        self.from_phone = from_phone

    def send_confirmation_sms(self, phone: str, confirmation_code: str) -> bool:
        try:
            params = {
                "body": f"Ваш код подтверждения: {confirmation_code}. Код действителен 10 минут.",
                "from_": self.from_phone,
                "to": phone
            }
            # message = self.client.messages.create(**params)
            # logger.info(f"SMS sent to {phone}, message SID: {message.sid}")
            send_sms_task.delay(params)
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
            return False

class MockSMSService(AbstractSMSService):
    def send_confirmation_sms(self, phone: str, confirmation_code: str) -> bool:
        logger.info(f"Mock: Would send confirmation SMS to {phone} with code {confirmation_code}")
        logger.info(f"Confirmation code: {confirmation_code}")
        return True
