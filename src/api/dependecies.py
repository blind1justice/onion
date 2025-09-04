from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.services.sms_service import TwilioSMSService
from src.schemas.users import UserSchema
from src.services.posts import PostService
from src.config.settings import settings
from src.services.email_service import ResendEmailService
from src.services.users import UserService
from src.utils.security import verify_token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def user_service():
    email_service = ResendEmailService(
        api_key=settings.resend_api_key,
        from_email=settings.resend_from_email
    )

    sms_service = TwilioSMSService(
        account_sid=settings.twilio_account_sid,
        auth_token=settings.twilio_auth_token,
        from_phone=settings.twilio_phone_number
    )

    return UserService(email_service, sms_service)

def post_service():
    return PostService()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(user_service)
) -> UserSchema:
    payload = verify_token(token)
    user_id = int(payload.get("sub"))
    user = await user_service.get_one(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
