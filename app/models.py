from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class CampaignStatus(str, Enum):
    draft = "draft"
    running = "running"
    completed = "completed"
    failed = "failed"


class RecipientStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # SMTP (encrypted)
    smtp_host: Mapped[str] = mapped_column(String(255), nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, nullable=False)
    smtp_username_enc: Mapped[str] = mapped_column(Text, nullable=False)
    smtp_password_enc: Mapped[str] = mapped_column(Text, nullable=False)
    smtp_tls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    smtp_ssl: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    from_email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Content
    subject: Mapped[str] = mapped_column(String(998), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Limits
    limit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    limit_window_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=3600)

    status: Mapped[CampaignStatus] = mapped_column(
        SAEnum(CampaignStatus), nullable=False, default=CampaignStatus.draft
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    recipients: Mapped[list[Recipient]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    sent_emails: Mapped[list[SentEmail]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class Recipient(Base):
    __tablename__ = "recipients"
    __table_args__ = (
        Index("ix_recipients_campaign_status", "campaign_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    to_email: Mapped[str] = mapped_column(String(320), nullable=False)
    to_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[RecipientStatus] = mapped_column(
        SAEnum(RecipientStatus), nullable=False, default=RecipientStatus.pending
    )
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="recipients")
    sent_emails: Mapped[list[SentEmail]] = relationship(back_populates="recipient")


class SentEmail(Base):
    __tablename__ = "sent_emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False)

    subject: Mapped[str] = mapped_column(String(998), nullable=False)
    message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    smtp_response: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    campaign: Mapped[Campaign] = relationship(back_populates="sent_emails")
    recipient: Mapped[Recipient] = relationship(back_populates="sent_emails")
