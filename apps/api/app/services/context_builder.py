from dataclasses import dataclass
from fnmatch import fnmatch

DEFAULT_IGNORES = ("node_modules/**", "dist/**", ".next/**", "*.lock", "*.min.js", "*.map")
SUPPORTED_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".java",
    ".rb",
    ".rs",
    ".cs",
    ".php",
    ".sql",
    ".yml",
    ".yaml",
}


@dataclass
class PreparedContext:
    text: str
    analyzed_files: int
    total_files: int
    partial: bool


def _is_relevant(path: str, patch: str | None, ignored: tuple[str, ...] = DEFAULT_IGNORES) -> bool:
    if not patch or any(fnmatch(path, pattern) for pattern in ignored):
        return False
    extension = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return extension in SUPPORTED_EXTENSIONS and len(patch) <= 30_000


def prepare_review_context(
    files: list[dict], max_files: int = 37, max_chars: int = 90_000
) -> PreparedContext:
    """Build a bounded diff-first context without executing or cloning untrusted code."""
    eligible = [f for f in files if _is_relevant(f.get("filename", ""), f.get("patch"))]
    parts: list[str] = []
    used = 0
    for file in eligible[:max_files]:
        patch = file["patch"]
        part = f"\n--- FILE: {file['filename']} ---\n{patch}\n"
        if used + len(part) > max_chars:
            break
        parts.append(part)
        used += len(part)
    return PreparedContext(
        text="".join(parts),
        analyzed_files=len(parts),
        total_files=len(eligible),
        partial=len(parts) < len(eligible),
    )
