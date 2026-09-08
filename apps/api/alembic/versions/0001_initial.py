"""initial CodeSage schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-07
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("github_user_id", sa.String(64), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255)),
        sa.Column("avatar_url", sa.String(2048)),
        sa.Column("email", sa.String(320)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("github_user_id"),
    )
    op.create_table(
        "github_installations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("github_installation_id", sa.String(64), nullable=False),
        sa.Column("account_login", sa.String(255), nullable=False),
        sa.Column("account_type", sa.String(32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("github_installation_id"),
    )
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("installation_id", sa.String(36), sa.ForeignKey("github_installations.id")),
        sa.Column("github_repo_id", sa.String(64), nullable=False),
        sa.Column("owner", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("language", sa.String(80)),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("default_branch", sa.String(255), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.Column("open_pull_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("github_repo_id"),
        sa.UniqueConstraint("owner", "name", name="ix_repository_owner_name"),
    )
    op.create_table(
        "pull_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("github_pr_id", sa.String(64), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("base_branch", sa.String(255), nullable=False),
        sa.Column("head_branch", sa.String(255), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False),
        sa.Column("deletions", sa.Integer(), nullable=False),
        sa.Column("changed_files", sa.Integer(), nullable=False),
        sa.Column("commits", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("github_pr_id"),
    )
    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("pull_request_id", sa.String(36), sa.ForeignKey("pull_requests.id")),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("overall_score", sa.Integer()),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("partial", sa.Boolean(), nullable=False),
        sa.Column("analyzed_files", sa.Integer(), nullable=False),
        sa.Column("total_files", sa.Integer(), nullable=False),
        sa.Column("usage", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_table(
        "review_issues",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("review_id", sa.String(36), sa.ForeignKey("reviews.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("start_line", sa.Integer()),
        sa.Column("end_line", sa.Integer()),
        sa.Column("code_snippet", sa.Text()),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("suggested_fix", sa.Text()),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("agent", sa.String(64), nullable=False),
        sa.Column("can_auto_fix", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_table(
        "webhook_deliveries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("delivery_id", sa.String(128), nullable=False),
        sa.Column("event", sa.String(80), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("delivery_id"),
    )
    op.create_table(
        "repository_settings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repository_id", sa.String(36), sa.ForeignKey("repositories.id"), nullable=False),
        sa.Column("auto_review", sa.Boolean(), nullable=False),
        sa.Column("review_new_commits", sa.Boolean(), nullable=False),
        sa.Column("publish_summary", sa.Boolean(), nullable=False),
        sa.Column("allow_inline_comments", sa.Boolean(), nullable=False),
        sa.Column("severity_threshold", sa.String(16), nullable=False),
        sa.Column("ignored_paths", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("repository_id"),
    )
    op.create_index("ix_users_github_user_id", "users", ["github_user_id"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_repositories_github_repo_id", "repositories", ["github_repo_id"])
    op.create_index("ix_repositories_owner", "repositories", ["owner"])
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"])
    op.create_index("ix_reviews_repository_id", "reviews", ["repository_id"])
    op.create_index("ix_reviews_pull_request_id", "reviews", ["pull_request_id"])
    op.create_index("ix_reviews_status", "reviews", ["status"])
    op.create_index("ix_review_issues_review_id", "review_issues", ["review_id"])
    op.create_index("ix_review_issues_category", "review_issues", ["category"])
    op.create_index("ix_review_issues_severity", "review_issues", ["severity"])
    op.create_index("ix_webhook_deliveries_delivery_id", "webhook_deliveries", ["delivery_id"])


def downgrade() -> None:
    for index in (
        "ix_webhook_deliveries_delivery_id",
        "ix_review_issues_severity",
        "ix_review_issues_category",
        "ix_review_issues_review_id",
        "ix_reviews_status",
        "ix_reviews_pull_request_id",
        "ix_reviews_repository_id",
        "ix_pull_requests_repository_id",
        "ix_repositories_owner",
        "ix_repositories_github_repo_id",
        "ix_users_username",
        "ix_users_github_user_id",
    ):
        op.drop_index(index)
    for table in (
        "repository_settings",
        "webhook_deliveries",
        "review_issues",
        "reviews",
        "pull_requests",
        "repositories",
        "github_installations",
        "users",
    ):
        op.drop_table(table)
