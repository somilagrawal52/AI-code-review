from collections import defaultdict

from app.schemas.review import ReviewIssueOutput

DEDUCTIONS = {"critical": 30, "high": 15, "medium": 7, "low": 3, "info": 0}


def calculate_scores(issues: list[ReviewIssueOutput]) -> tuple[int, dict[str, int]]:
    """Deterministic, transparent scoring: score starts at 100 and validated findings deduct weight."""
    groups: dict[str, list[ReviewIssueOutput]] = defaultdict(list)
    for issue in issues:
        groups[issue.category.value].append(issue)

    def score(items: list[ReviewIssueOutput]) -> int:
        return max(0, 100 - sum(DEDUCTIONS[item.severity.value] for item in items))

    overall = score(issues)
    aliases = {
        "security": "security",
        "bug": "reliability",
        "performance": "performance",
        "maintainability": "maintainability",
        "testing": "testing",
    }
    scores = {target: score(groups.get(source, [])) for source, target in aliases.items()}
    return overall, scores
