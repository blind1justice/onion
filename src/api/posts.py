from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from src.api.dependecies import get_current_user, post_service, oauth2_scheme
from src.services.posts import PostService
from src.schemas.posts import PostSchema, PostSchemaAdd
from src.utils.security import verify_token


router = APIRouter(prefix="/api/posts", tags=["Posts"])


@router.get("")
async def get_posts(post_service: Annotated[PostService, Depends(post_service)]) -> List[PostSchema]:
    posts = await post_service.get_all()
    return posts


@router.post("")
async def add_post(
    post: PostSchemaAdd, 
    post_service: Annotated[PostService, Depends(post_service)],
    token: Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]
) -> PostSchema:
    payload = verify_token(token)
    user_id = int(payload.get("sub"))
    post = await post_service.add(post, user_id)
    return post
