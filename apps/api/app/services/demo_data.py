from datetime import UTC, datetime, timedelta

from app.schemas.review import Category, ReviewIssueOutput, ReviewResult, Severity
from app.services.scoring import calculate_scores

DEMO_REPOSITORIES = [
    {
        "id": "demo-storefront",
        "github_repo_id": "101",
        "owner": "acme",
        "name": "storefront",
        "description": "Modern checkout and inventory experience.",
        "language": "TypeScript",
        "private": True,
        "default_branch": "main",
        "stars": 142,
        "open_pull_count": 3,
        "updated_at": "2026-09-06T09:14:00Z",
    },
    {
        "id": "demo-api",
        "github_repo_id": "102",
        "owner": "somil",
        "name": "payments-api",
        "description": "Payment orchestration service.",
        "language": "Python",
        "private": True,
        "default_branch": "main",
        "stars": 24,
        "open_pull_count": 2,
        "updated_at": "2026-09-05T16:30:00Z",
    },
    {
        "id": "demo-design",
        "github_repo_id": "103",
        "owner": "somil",
        "name": "design-system",
        "description": "Shared accessible UI primitives.",
        "language": "TypeScript",
        "private": False,
        "default_branch": "main",
        "stars": 67,
        "open_pull_count": 0,
        "updated_at": "2026-09-01T13:00:00Z",
    },
]

DEMO_PULLS = {
    "acme/storefront": [
        {
            "id": "demo-pr-142",
            "github_pr_id": "142",
            "number": 142,
            "title": "Improve checkout validation",
            "author": "maya-chen",
            "state": "open",
            "base_branch": "main",
            "head_branch": "fix/checkout-validation",
            "additions": 189,
            "deletions": 41,
            "changed_files": 8,
            "commits": 3,
        }
    ],
    "somil/payments-api": [
        {
            "id": "demo-pr-17",
            "github_pr_id": "17",
            "number": 17,
            "title": "Add payment retry policy",
            "author": "somil",
            "state": "open",
            "base_branch": "main",
            "head_branch": "feature/retries",
            "additions": 284,
            "deletions": 18,
            "changed_files": 6,
            "commits": 2,
        }
    ],
    "somil/design-system": [],
}

DEMO_PATCHES = [
    {
        "filename": "src/server/checkout.ts",
        "patch": "@@ -44,8 +44,12 @@ export async function createCheckout(input: CheckoutInput) {\n-  const total = input.items.reduce((sum, item) => sum + item.price, 0);\n+  const total = input.items.reduce((sum, item) => sum + item.price, 0);\n+  await db.orders.create({ data: { userId: input.userId, total } });\n+  await paymentProvider.charge({ amount: total, token: input.paymentToken });\n }",
    },
    {
        "filename": "src/client/CheckoutForm.tsx",
        "patch": "@@ -22,6 +22,8 @@ export function CheckoutForm() {\n+  const [submitting, setSubmitting] = useState(false);\n   const submit = async () => {\n+    await api.post('/checkout', values);\n   };\n }",
    },
]


def demo_result() -> ReviewResult:
    issues = [
        ReviewIssueOutput(
            title="Missing server-side price validation",
            description="The request-provided item price is used to compute the charge total.",
            category=Category.security,
            severity=Severity.high,
            file_path="src/server/checkout.ts",
            start_line=45,
            end_line=45,
            code_snippet="sum + item.price",
            explanation="A client can alter a request before it reaches this handler and lower the total.",
            suggested_fix="Look up authoritative product prices server-side and compute totals from those records.",
            confidence=94,
            agent="security",
            can_auto_fix=True,
        ),
        ReviewIssueOutput(
            title="Possible duplicate database query",
            description="Order creation occurs before the payment authorization result is known.",
            category=Category.performance,
            severity=Severity.medium,
            file_path="src/server/checkout.ts",
            start_line=46,
            end_line=47,
            code_snippet="await db.orders.create(...)",
            explanation="A failed charge can create records that require cleanup and may cause retry-driven duplicate work.",
            suggested_fix="Authorize payment first or use an idempotency key and a transaction-aware order state.",
            confidence=79,
            agent="performance",
            can_auto_fix=False,
        ),
        ReviewIssueOutput(
            title="Unhandled payment-provider timeout",
            description="The payment call has no explicit timeout or recovery path.",
            category=Category.bug,
            severity=Severity.medium,
            file_path="src/server/checkout.ts",
            start_line=47,
            end_line=47,
            code_snippet="await paymentProvider.charge(...) ",
            explanation="A provider outage can leave the request hanging or return an ambiguous outcome.",
            suggested_fix="Set a timeout, handle provider-specific errors, and persist an idempotency key.",
            confidence=88,
            agent="bug",
            can_auto_fix=True,
        ),
        ReviewIssueOutput(
            title="Complex conditional should be extracted",
            description="Checkout validation is becoming difficult to test as branches accumulate.",
            category=Category.maintainability,
            severity=Severity.low,
            file_path="src/client/CheckoutForm.tsx",
            start_line=23,
            end_line=25,
            code_snippet="const submit = async () => ...",
            explanation="Extracting validation and submission orchestration makes failure paths explicit.",
            suggested_fix="Move validation to a dedicated schema and submit through a small mutation hook.",
            confidence=71,
            agent="maintainability",
            can_auto_fix=True,
        ),
    ]
    return ReviewResult(
        summary="The checkout change improves the user flow but should validate prices on the server and make payment processing resilient before merge.",
        issues=issues,
        positive_findings=["The flow keeps payment token handling on the server boundary."],
        recommended_actions=[
            "Validate prices from the catalog before charging.",
            "Add timeout and idempotency coverage for payment failures.",
        ],
    )


def demo_review_payload() -> dict:
    result = demo_result()
    score, scores = calculate_scores(result.issues)
    return {
        "id": "demo-review-142",
        "status": "completed",
        "summary": result.summary,
        "overall_score": score,
        "scores": scores,
        "issues": [issue.model_dump() for issue in result.issues],
        "partial": False,
        "analyzed_files": 2,
        "total_files": 2,
        "created_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
    }
