from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from database.types.user import User
from dependencies import get_current_user, get_user_service
from services.user import REFRESH_TOKEN_TTL_SECONDS, TokenPair, UserService

router = APIRouter(prefix = "/auth", tags = ["auth"])

REFRESH_COOKIE_NAME = "refresh_token"
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_BYTES = 72  # bcrypt's limit


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


def _clear_refresh_cookie(response: Response) -> None:
    # Must use the same path and flags as _set_refresh_cookie, or the browser keeps the cookie.
    response.delete_cookie(
        key = REFRESH_COOKIE_NAME,
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


@router.post("/logout", status_code = 204)
async def logout(response: Response) -> None:
    # No login required, so it still works after the access token has expired.
    # This only clears the browser's cookie. The refresh token itself is not revoked server-side.
    _clear_refresh_cookie(response)


@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> PublicUser:
    return PublicUser(id = user.id, username = user.username)


class RegisterRequest(BaseModel):
    # Same rules the signup form shows, enforced here so the API does not depend on the UI.
    username: str = Field(pattern = r"^[A-Za-z0-9_]{3,20}$")
    password: str = Field(min_length = MIN_PASSWORD_LENGTH)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt rejects anything over 72 bytes, which would otherwise surface as a 500.
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"Password must be at most {MAX_PASSWORD_BYTES} bytes")
        return value


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
