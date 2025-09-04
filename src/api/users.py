from typing import Annotated, List
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from src.api.dependecies import user_service, oauth2_scheme
from src.services.users import UserService
from src.schemas.users import PhoneConfirmation, Token, UserSchema, UserSchemaLogin
from src.utils.security import verify_token


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/register")
async def add_user(user: UserSchemaLogin, user_service: Annotated[UserService, Depends(user_service)]):
    try:
        user = await user_service.add(user)
        if user.email:
            register_message = "User registered successfully. Check your email for confirmation."
        elif user.phone:
            register_message = "User registered successfully. Check your phone for confirmation."
        return {
            "user": user,
            "message": register_message
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    

@router.get("/confirm-email")
async def confirm_email(
    token: Annotated[str, Query(..., description="Email confirmation token")],
    user_service: UserService = Depends(user_service)
):
    success = await user_service.confirm_email(token)
    
    if success:
        return {
            "message": "Email successfully confirmed",
            "status": "success"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to confirm email. Token may be invalid or expired."
        )
    

@router.post("/confirm-phone")
async def confirm_phone(
    confirmation: PhoneConfirmation,
    user_service: Annotated[UserService, Depends(user_service)]
):
    success = await user_service.confirm_phone(confirmation.phone, confirmation.code)
    
    if success:
        return {
            "message": "Phone successfully confirmed",
            "status": "success"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to confirm phone. Code may be invalid or expired."
        )


@router.get("")
async def get_users(user_service: Annotated[UserService, Depends(user_service)]) -> List[UserSchema]:
    users = await user_service.get_all()
    return users


@router.post("/login")
async def login(
    user_service: Annotated[UserService, Depends(user_service)],
    username: str = Form(...),
    password: str = Form(...),
) -> Token:
    if "@" in username:
        login_data = UserSchemaLogin(email=username, password=password)
    else:
        login_data = UserSchemaLogin(phone=username, password=password)

    user = await user_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await user_service.create_access_token_for_user(user)
    return Token(access_token=access_token)


@router.get("/me")
async def read_users_me(
    user_service: Annotated[UserService, Depends(user_service)],
    token: Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]
) -> UserSchema:
    payload = verify_token(token)
    user_id = int(payload.get("sub"))
    user = await user_service.get_one(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
