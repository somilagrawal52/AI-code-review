from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.services.demo_data import DEMO_PULLS, DEMO_REPOSITORIES

router = APIRouter(prefix="/api/repositories", tags=["repositories"])
settings = get_settings()


def demo_repository(owner: str, repo: str) -> dict:
    item = next(
        (item for item in DEMO_REPOSITORIES if item["owner"] == owner and item["name"] == repo),
        None,
    )
    if not item:
        raise HTTPException(404, "Repository not found")
    return item


@router.get("")
async def list_repositories(
    query: str | None = Query(default=None), visibility: str | None = None
) -> dict:
    if not settings.demo_mode:
        raise HTTPException(501, "Connect a GitHub App installation to list live repositories")
    rows = DEMO_REPOSITORIES
    if query:
        search = query.lower()
        rows = [r for r in rows if search in f"{r['owner']}/{r['name']}".lower()]
    if visibility in {"public", "private"}:
        wanted = visibility == "private"
        rows = [r for r in rows if r["private"] == wanted]
    return {"items": rows, "demo": True}


@router.get("/{owner}/{repo}")
async def get_repository(owner: str, repo: str) -> dict:
    return {**demo_repository(owner, repo), "health": None, "demo": settings.demo_mode}


@router.get("/{owner}/{repo}/pulls")
async def list_pull_requests(owner: str, repo: str) -> dict:
    demo_repository(owner, repo)
    return {"items": DEMO_PULLS.get(f"{owner}/{repo}", []), "demo": settings.demo_mode}


@router.get("/{owner}/{repo}/pulls/{number}")
async def get_pull_request(owner: str, repo: str, number: int) -> dict:
    pull = next((p for p in DEMO_PULLS.get(f"{owner}/{repo}", []) if p["number"] == number), None)
    if not pull:
        raise HTTPException(404, "Pull request not found")
    return {**pull, "repository": demo_repository(owner, repo), "demo": settings.demo_mode}
