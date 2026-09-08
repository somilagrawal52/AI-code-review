import hashlib
import hmac

import pytest
from pydantic import ValidationError

from app.core.security import verify_github_signature
from app.schemas.review import ReviewIssueOutput
from app.services.context_builder import prepare_review_context
from app.services.scoring import calculate_scores


def test_webhook_signature_verification() -> None:
    payload, secret = b'{"action":"opened"}', "top-secret"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_github_signature(payload, signature, secret)
    assert not verify_github_signature(payload, signature, "wrong")
    assert not verify_github_signature(payload, None, secret)


def test_context_skips_lockfiles_and_marks_partial() -> None:
    files = [
        {"filename": "package-lock.json", "patch": "x"},
        {"filename": "src/app.ts", "patch": "+const value = 1"},
        {"filename": "dist/app.js", "patch": "x"},
    ]
    context = prepare_review_context(files)
    assert context.analyzed_files == 1
    assert context.total_files == 1
    assert "src/app.ts" in context.text


def test_review_line_range_is_validated() -> None:
    with pytest.raises(ValidationError):
        ReviewIssueOutput(
            title="x",
            description="x",
            category="bug",
            severity="low",
            file_path="a.py",
            start_line=8,
            end_line=4,
            explanation="x",
            confidence=60,
            agent="bug",
        )


def test_scores_are_deterministic_and_clamped() -> None:
    issue = ReviewIssueOutput(
        title="x",
        description="x",
        category="security",
        severity="critical",
        file_path="a.py",
        explanation="x",
        confidence=100,
        agent="security",
    )
    overall, scores = calculate_scores([issue] * 4)
    assert overall == 0
    assert scores["security"] == 0
