import hashlib
import hmac

from fastapi import HTTPException, status


def verify_github_signature(payload: bytes, signature: str | None, secret: str | None) -> bool:
    """Verify GitHub's sha256 webhook signature using a timing-safe comparison."""
    if not signature or not secret or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def require_owner(user_id: str | None, expected_user_id: str) -> None:
    if user_id != expected_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this resource"
        )
