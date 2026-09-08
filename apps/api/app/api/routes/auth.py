import secrets

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.get("/github")
async def github_login() -> RedirectResponse:
    if not settings.github_client_id:
        raise HTTPException(
            503, "GitHub OAuth is not configured. Use Demo Mode or configure GITHUB_CLIENT_ID."
        )
    state = secrets.token_urlsafe(32)
    response = RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={settings.github_client_id}&scope=read:user%20user:email&state={state}"
    )
    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/github/callback")
async def github_callback(
    request: Request, code: str, state: str, session: AsyncSession = Depends(get_session)
) -> RedirectResponse:
    expected_state = request.cookies.get("oauth_state")
    if not expected_state or not secrets.compare_digest(state, expected_state):
        raise HTTPException(400, "Invalid OAuth state")
    if not settings.github_client_secret:
        raise HTTPException(503, "GitHub OAuth is not configured")
    async with httpx.AsyncClient(timeout=20) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            json={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
        )
        access_token = token_response.json().get("access_token")
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
    if not access_token or user_response.status_code >= 400:
        raise HTTPException(401, "GitHub authentication failed")
    profile = user_response.json()
    user = (
        await session.execute(select(User).where(User.github_user_id == str(profile["id"])))
    ).scalar_one_or_none()
    if not user:
        user = User(
            github_user_id=str(profile["id"]),
            username=profile["login"],
            display_name=profile.get("name"),
            avatar_url=profile.get("avatar_url"),
            email=profile.get("email"),
        )
        session.add(user)
    else:
        user.username, user.display_name, user.avatar_url, user.email = (
            profile["login"],
            profile.get("name"),
            profile.get("avatar_url"),
            profile.get("email"),
        )
    await session.commit()
    token = jwt.encode({"sub": user.id}, settings.secret_key, algorithm="HS256")
    response = RedirectResponse(f"{settings.app_url}/dashboard")
    response.set_cookie(
        "codesage_session",
        token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
    response.delete_cookie("oauth_state")
    return response


@router.get("/me")
async def me() -> dict:
    return {
        "id": "demo-user",
        "username": "somil",
        "display_name": "Somil",
        "avatar_url": None,
        "demo": settings.demo_mode,
    }
