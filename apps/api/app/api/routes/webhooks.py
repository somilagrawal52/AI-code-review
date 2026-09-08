import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import verify_github_signature
from app.db.session import get_session
from app.models import WebhookDelivery

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
settings = get_settings()


@router.post("/github", status_code=202)
async def github_webhook(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    payload = await request.body()
    if not verify_github_signature(
        payload, request.headers.get("x-hub-signature-256"), settings.github_webhook_secret
    ):
        raise HTTPException(401, "Invalid GitHub webhook signature")
    delivery_id = request.headers.get("x-github-delivery")
    event = request.headers.get("x-github-event", "unknown")
    if not delivery_id:
        raise HTTPException(400, "Missing GitHub delivery id")
    existing = (
        await session.execute(
            select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
        )
    ).scalar_one_or_none()
    if existing:
        return {"accepted": True, "duplicate": True}
    delivery = WebhookDelivery(delivery_id=delivery_id, event=event)
    session.add(delivery)
    await session.commit()
    data = json.loads(payload)
    action = data.get("action")
    should_review = event == "pull_request" and action in {"opened", "reopened", "synchronize"}
    delivery.processed = True
    await session.commit()
    return {"accepted": True, "queued_for_review": should_review}
