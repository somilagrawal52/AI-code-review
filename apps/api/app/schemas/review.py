from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Severity(StrEnum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class Category(StrEnum):
    security = "security"
    bug = "bug"
    performance = "performance"
    maintainability = "maintainability"
    testing = "testing"
    style = "style"


class ReviewIssueOutput(BaseModel):
    title: str = Field(max_length=500)
    description: str
    category: Category
    severity: Severity
    file_path: str
    start_line: int | None = Field(default=None, ge=1)
    end_line: int | None = Field(default=None, ge=1)
    code_snippet: str | None = None
    explanation: str
    suggested_fix: str | None = None
    confidence: int = Field(ge=0, le=100)
    agent: str
    can_auto_fix: bool = False

    @field_validator("end_line")
    @classmethod
    def valid_range(cls, value: int | None, info):
        start = info.data.get("start_line")
        if value is not None and start is not None and value < start:
            raise ValueError("end_line must not precede start_line")
        return value


class SpecialistOutput(BaseModel):
    findings: list[ReviewIssueOutput] = Field(default_factory=list)


class ReviewResult(BaseModel):
    summary: str
    issues: list[ReviewIssueOutput] = Field(default_factory=list)
    positive_findings: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    id: str
    status: str
    summary: str | None = None
    overall_score: int | None = None
    scores: dict[str, int] = Field(default_factory=dict)
    issues: list[ReviewIssueOutput] = Field(default_factory=list)
    partial: bool = False
    analyzed_files: int = 0
    total_files: int = 0


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class GenerateRequest(BaseModel):
    instruction: str | None = Field(default=None, max_length=1000)
