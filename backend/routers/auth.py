from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from database.types.user import User
from dependencies import get_current_user, get_user_service
from services.user import ACCESS_TOKEN_TTL_SECONDS, UserService

router = APIRouter(prefix = "/auth", tags = ["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class PublicUser(BaseModel):
    id: int
    username: str

@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    token = await user_service.login(body.username, body.password)
    if token is None:
        raise HTTPException(status_code = 401, detail = "Invalid username or password")
    response.set_cookie(
        key = "access_token",
        value = token,
        max_age = ACCESS_TOKEN_TTL_SECONDS,
        httponly = True,
        samesite = "lax",
        path = "/",
    )
    return {"access_token": token}

@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> PublicUser:
    return PublicUser(id = user.id, username = user.username)

class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(
    body: RegisterRequest,
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    token = await user_service.create_user(body.username, body.password)
    if token is None:
        raise HTTPException(status_code = 400, detail = "Username is already taken")
    response.set_cookie(
        key = "access_token",
        value = token,
        max_age = ACCESS_TOKEN_TTL_SECONDS,
        httponly = True,
        samesite = "lax",
        path = "/",
    )
    return {"access_token": token}
