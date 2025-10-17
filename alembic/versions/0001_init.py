from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("smtp_host", sa.String(length=255), nullable=False),
        sa.Column("smtp_port", sa.Integer(), nullable=False),
        sa.Column("smtp_username_enc", sa.Text(), nullable=False),
        sa.Column("smtp_password_enc", sa.Text(), nullable=False),
        sa.Column("smtp_tls", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("from_email", sa.String(length=320), nullable=True),
        sa.Column("from_name", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=998), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("limit_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("limit_window_seconds", sa.Integer(), nullable=False, server_default=sa.text("3600")),
        sa.Column("status", sa.Enum("draft", "running", "completed", "failed", name="campaignstatus"), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "recipients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_email", sa.String(length=320), nullable=False),
        sa.Column("to_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.Enum("pending", "sent", "failed", name="recipientstatus"), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_recipients_campaign_status", "recipients", ["campaign_id", "status"]) 

    op.create_table(
        "sent_emails",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(length=998), nullable=False),
        sa.Column("message_id", sa.String(length=255), nullable=True),
        sa.Column("smtp_response", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sent_emails")
    op.drop_index("ix_recipients_campaign_status", table_name="recipients")
    op.drop_table("recipients")
    op.drop_table("campaigns")
