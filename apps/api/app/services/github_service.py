import time

import httpx
import jwt
from fastapi import HTTPException

from app.core.config import get_settings

GITHUB_API = "https://api.github.com"


class GitHubService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _app_jwt(self) -> str:
        if not self.settings.github_app_id or not self.settings.github_app_private_key:
            raise HTTPException(503, "GitHub App credentials are not configured")
        now = int(time.time())
        return jwt.encode(
            {"iat": now - 60, "exp": now + 540, "iss": self.settings.github_app_id},
            self.settings.github_app_private_key,
            algorithm="RS256",
        )

    async def installation_token(self, installation_id: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._app_jwt()}",
            "Accept": "application/vnd.github+json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{GITHUB_API}/app/installations/{installation_id}/access_tokens", headers=headers
            )
        if response.status_code >= 400:
            raise HTTPException(
                response.status_code, "Unable to obtain a GitHub installation token"
            )
        return response.json()["token"]

    async def request(
        self, token: str, path: str, accept: str = "application/vnd.github+json"
    ) -> dict | list:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{GITHUB_API}{path}", headers=headers)
        if response.status_code == 403 and response.headers.get("x-ratelimit-remaining") == "0":
            raise HTTPException(429, "GitHub rate limit reached; retry after reset")
        if response.status_code >= 400:
            raise HTTPException(response.status_code, "GitHub request failed")
        return response.json()

    async def pull_request_files(
        self, token: str, owner: str, repo: str, number: int
    ) -> list[dict]:
        data = await self.request(token, f"/repos/{owner}/{repo}/pulls/{number}/files?per_page=100")
        return data if isinstance(data, list) else []
