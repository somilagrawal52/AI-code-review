from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models import PullRequest, Repository, Review
from app.schemas.review import ChatRequest, GenerateRequest
from app.services.demo_data import demo_review_payload
from app.services.review_service import create_review, get_review, serialize_review

router = APIRouter(prefix="/api", tags=["reviews"])
settings = get_settings()


@router.post("/repositories/{owner}/{repo}/pulls/{number}/review")
async def run_review(
    owner: str, repo: str, number: int, session: AsyncSession = Depends(get_session)
) -> dict:
    if settings.demo_mode:
        return demo_review_payload()
    repository = (
        await session.execute(
            select(Repository).where(Repository.owner == owner, Repository.name == repo)
        )
    ).scalar_one_or_none()
    if not repository:
        raise HTTPException(404, "Repository is not connected")
    pull = (
        await session.execute(
            select(PullRequest).where(
                PullRequest.repository_id == repository.id, PullRequest.number == number
            )
        )
    ).scalar_one_or_none()
    if not pull:
        raise HTTPException(404, "Pull request not found")
    # In production this file list is fetched with the installation token after authorization.
    review = await create_review(session, repository, pull, [], use_demo=False)
    response = await get_review(session, review.id)
    return response.model_dump() if response else {"id": review.id, "status": review.status}


@router.get("/reviews")
async def list_reviews(session: AsyncSession = Depends(get_session)) -> dict:
    if settings.demo_mode:
        return {"items": [demo_review_payload()], "demo": True}
    rows = list(
        (await session.execute(select(Review).order_by(Review.created_at.desc()))).scalars()
    )
    return {"items": [serialize_review(item).model_dump() for item in rows]}


@router.get("/reviews/{review_id}")
async def review_detail(review_id: str, session: AsyncSession = Depends(get_session)) -> dict:
    if settings.demo_mode and review_id == "demo-review-142":
        return demo_review_payload()
    review = await get_review(session, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    return review.model_dump()


@router.post("/reviews/{review_id}/publish")
async def publish_review(review_id: str) -> dict:
    if settings.demo_mode:
        return {
            "published": False,
            "message": "Demo Mode: GitHub publishing is intentionally disabled.",
        }
    raise HTTPException(
        501, "Connect a GitHub installation and enable pull request write permission to publish"
    )


@router.post("/reviews/{review_id}/issues/{issue_id}/fix")
async def generate_fix(review_id: str, issue_id: str, payload: GenerateRequest) -> dict:
    return {
        "review_id": review_id,
        "issue_id": issue_id,
        "kind": "fix",
        "content": "Demo suggestion: validate authoritative server-side product prices and retain an idempotency key for the charge.",
        "demo": settings.demo_mode,
    }


@router.post("/reviews/{review_id}/issues/{issue_id}/test")
async def generate_test(review_id: str, issue_id: str, payload: GenerateRequest) -> dict:
    return {
        "review_id": review_id,
        "issue_id": issue_id,
        "kind": "test",
        "content": "it('uses the catalog price rather than the client price', async () => { /* arrange catalog, submit altered price, assert charge amount */ })",
        "demo": settings.demo_mode,
    }


@router.post("/reviews/{review_id}/chat")
async def chat(review_id: str, payload: ChatRequest) -> dict:
    return {
        "answer": "This finding matters because the server trusts a client-controlled monetary value. A safer implementation resolves each product from the catalog, calculates the total server-side, and applies an idempotency key before charging.",
        "review_id": review_id,
        "demo": settings.demo_mode,
    }
