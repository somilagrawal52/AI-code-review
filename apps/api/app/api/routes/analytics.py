from fastapi import APIRouter

from app.services.demo_data import demo_review_payload

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/dashboard")
async def dashboard() -> dict:
    review = demo_review_payload()
    issues = review["issues"]
    return {
        "demo": True,
        "metrics": {"repositories": 3, "reviews": 12, "issues": 41, "critical": 2},
        "reviews_over_time": [
            {"date": "Mon", "reviews": 2},
            {"date": "Tue", "reviews": 4},
            {"date": "Wed", "reviews": 3},
            {"date": "Thu", "reviews": 6},
            {"date": "Fri", "reviews": 5},
            {"date": "Sat", "reviews": 2},
            {"date": "Sun", "reviews": 4},
        ],
        "recent_reviews": [review],
        "findings": {
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"]),
        },
    }
