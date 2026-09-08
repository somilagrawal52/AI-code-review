from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import ReviewOrchestrator
from app.models import PullRequest, Repository, Review, ReviewIssue
from app.schemas.review import ReviewResponse
from app.services.context_builder import prepare_review_context
from app.services.demo_data import demo_result
from app.services.scoring import calculate_scores


def serialize_review(review: Review, issues: list[ReviewIssue] | None = None) -> ReviewResponse:
    issues = issues or []
    return ReviewResponse(
        id=review.id,
        status=review.status,
        summary=review.summary,
        overall_score=review.overall_score,
        scores=review.scores or {},
        partial=review.partial,
        analyzed_files=review.analyzed_files,
        total_files=review.total_files,
        issues=[
            {
                "title": issue.title,
                "description": issue.description,
                "category": issue.category,
                "severity": issue.severity,
                "file_path": issue.file_path,
                "start_line": issue.start_line,
                "end_line": issue.end_line,
                "code_snippet": issue.code_snippet,
                "explanation": issue.explanation,
                "suggested_fix": issue.suggested_fix,
                "confidence": issue.confidence,
                "agent": issue.agent,
                "can_auto_fix": issue.can_auto_fix,
            }
            for issue in issues
        ],
    )


async def create_review(
    session: AsyncSession,
    repository: Repository,
    pull: PullRequest | None,
    files: list[dict],
    use_demo: bool,
) -> Review:
    context = prepare_review_context(files)
    review = Review(
        repository_id=repository.id,
        pull_request_id=pull.id if pull else None,
        status="preparing",
        partial=context.partial,
        analyzed_files=context.analyzed_files,
        total_files=context.total_files,
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)
    try:
        review.status = "analyzing"
        await session.commit()
        result = demo_result() if use_demo else await ReviewOrchestrator().review(context.text)
        review.status = "aggregating"
        await session.commit()
        overall, scores = calculate_scores(result.issues)
        review.summary, review.overall_score, review.scores, review.status = (
            result.summary,
            overall,
            scores,
            "completed",
        )
        for finding in result.issues:
            session.add(ReviewIssue(review_id=review.id, **finding.model_dump()))
        await session.commit()
        await session.refresh(review)
    except Exception:
        review.status = "failed"
        await session.commit()
        raise
    return review


async def get_review(session: AsyncSession, review_id: str) -> ReviewResponse | None:
    review = await session.get(Review, review_id)
    if not review:
        return None
    issues = list(
        (
            await session.execute(select(ReviewIssue).where(ReviewIssue.review_id == review.id))
        ).scalars()
    )
    return serialize_review(review, issues)
