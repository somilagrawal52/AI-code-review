import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    github_user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    email: Mapped[str | None] = mapped_column(String(320))


class GitHubInstallation(TimestampMixin, Base):
    __tablename__ = "github_installations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    github_installation_id: Mapped[str] = mapped_column(String(64), unique=True)
    account_login: Mapped[str] = mapped_column(String(255))
    account_type: Mapped[str] = mapped_column(String(32))


class Repository(TimestampMixin, Base):
    __tablename__ = "repositories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    installation_id: Mapped[str | None] = mapped_column(
        ForeignKey("github_installations.id"), index=True
    )
    github_repo_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    owner: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(80))
    private: Mapped[bool] = mapped_column(Boolean, default=True)
    default_branch: Mapped[str] = mapped_column(String(255), default="main")
    stars: Mapped[int] = mapped_column(Integer, default=0)
    open_pull_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (Index("ix_repository_owner_name", "owner", "name", unique=True),)


class PullRequest(TimestampMixin, Base):
    __tablename__ = "pull_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id: Mapped[str] = mapped_column(ForeignKey("repositories.id"), index=True)
    github_pr_id: Mapped[str] = mapped_column(String(64), unique=True)
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(32), default="open")
    base_branch: Mapped[str] = mapped_column(String(255))
    head_branch: Mapped[str] = mapped_column(String(255))
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, default=0)
    commits: Mapped[int] = mapped_column(Integer, default=0)


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id: Mapped[str] = mapped_column(ForeignKey("repositories.id"), index=True)
    pull_request_id: Mapped[str | None] = mapped_column(ForeignKey("pull_requests.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[int | None] = mapped_column(Integer)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    partial: Mapped[bool] = mapped_column(Boolean, default=False)
    analyzed_files: Mapped[int] = mapped_column(Integer, default=0)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    usage: Mapped[dict] = mapped_column(JSON, default=dict)


class ReviewIssue(TimestampMixin, Base):
    __tablename__ = "review_issues"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id: Mapped[str] = mapped_column(ForeignKey("reviews.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    file_path: Mapped[str] = mapped_column(String(1024))
    start_line: Mapped[int | None] = mapped_column(Integer)
    end_line: Mapped[int | None] = mapped_column(Integer)
    code_snippet: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    suggested_fix: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[int] = mapped_column(Integer)
    agent: Mapped[str] = mapped_column(String(64))
    can_auto_fix: Mapped[bool] = mapped_column(Boolean, default=False)


class WebhookDelivery(TimestampMixin, Base):
    __tablename__ = "webhook_deliveries"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    delivery_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    event: Mapped[str] = mapped_column(String(80))
    processed: Mapped[bool] = mapped_column(Boolean, default=False)


class RepositorySettings(TimestampMixin, Base):
    __tablename__ = "repository_settings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id: Mapped[str] = mapped_column(ForeignKey("repositories.id"), unique=True)
    auto_review: Mapped[bool] = mapped_column(Boolean, default=False)
    review_new_commits: Mapped[bool] = mapped_column(Boolean, default=True)
    publish_summary: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_inline_comments: Mapped[bool] = mapped_column(Boolean, default=False)
    severity_threshold: Mapped[str] = mapped_column(String(16), default="high")
    ignored_paths: Mapped[list] = mapped_column(JSON, default=list)
