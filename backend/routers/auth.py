from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from database.types.user import User
from dependencies import get_current_user, get_user_service
from services.user import REFRESH_TOKEN_TTL_SECONDS, TokenPair, UserService

router = APIRouter(prefix = "/auth", tags = ["auth"])

REFRESH_COOKIE_NAME = "refresh_token"


class LoginRequest(BaseModel):
    username: str
    password: str


class PublicUser(BaseModel):
    id: int
    username: str


class AccessTokenResponse(BaseModel):
    access_token: str


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key = REFRESH_COOKIE_NAME,
        value = refresh_token,
        max_age = REFRESH_TOKEN_TTL_SECONDS,
        httponly = True,
        samesite = "lax",
        path = "/auth",
    )


def _issue_auth_response(response: Response, tokens: TokenPair) -> AccessTokenResponse:
    _set_refresh_cookie(response, tokens.refresh_token)
    return AccessTokenResponse(access_token = tokens.access_token)


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AccessTokenResponse:
    tokens = await user_service.login(body.username, body.password)
    if tokens is None:
        raise HTTPException(status_code = 401, detail = "Invalid username or password")
    return _issue_auth_response(response, tokens)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AccessTokenResponse:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code = 401, detail = "Missing refresh token")
    tokens = await user_service.refresh(refresh_token)
    if tokens is None:
        raise HTTPException(status_code = 401, detail = "Invalid refresh token")
    return _issue_auth_response(response, tokens)


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
) -> AccessTokenResponse:
    tokens = await user_service.create_user(body.username, body.password)
    if tokens is None:
        raise HTTPException(status_code = 400, detail = "Username is already taken")
    return _issue_auth_response(response, tokens)
