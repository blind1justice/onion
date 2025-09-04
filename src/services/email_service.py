from abc import ABC, abstractmethod
import resend
import logging
from src.config.settings import settings
from src.celery_conf.tasks import send_email_task

logger = logging.getLogger(__name__)

class AbstractEmailService(ABC):
    @abstractmethod
    def send_confirmation_email(self, email: str, confirmation_token: str) -> bool:
        raise NotImplementedError()

class ResendEmailService(AbstractEmailService):
    def __init__(self, api_key: str, from_email: str):
        resend.api_key = api_key
        self.from_email = from_email

    def send_confirmation_email(self, email: str, confirmation_token: str) -> bool:
        try:
            confirmation_link = f"{settings.base_url}/api/users/confirm-email?token={confirmation_token}"

            html_content = f"""
            <h2>Подтверждение email</h2>
            <p>Для завершения регистрации, перейдите по ссылке:</p>
            <a href="{confirmation_link}">Подтвердить email</a>
            <p>Ссылка действительна 24 часа.</p>
            """

            params = {
                "from": self.from_email,
                "to": [email],
                "subject": "Подтверждение email",
                "html": html_content,
            }

            send_email_task.delay(params)
            #response = resend.Emails.send(params)
            #logger.info(f"Email sent to {email}, response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            return False

class MockEmailService(AbstractEmailService):
    def send_confirmation_email(self, email: str, confirmation_token: str) -> bool:
        logger.info(f"Mock: Would send confirmation email to {email} with token {confirmation_token}")
        logger.info(f"Confirmation link: {settings.base_url}/confirm-email?token={confirmation_token}")
        return True