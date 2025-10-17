from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .worker import celery
from .db import SessionLocal
from .models import Campaign, CampaignStatus, Recipient, RecipientStatus, SentEmail
from .crypto import decrypt_str
from .email_sender import send_email_smtp


def _get_delay_seconds(campaign: Campaign) -> int:
    # round up to be safe for provider limits
    return max(0, math.ceil(campaign.limit_window_seconds / max(1, campaign.limit_count)))


@celery.task(name="send_next_email")
def send_next_email(campaign_id: int) -> None:
    db: Session = SessionLocal()
    try:
        campaign: Optional[Campaign] = db.get(Campaign, campaign_id)
        if campaign is None:
            return
        if campaign.status != CampaignStatus.running:
            return

        # next pending recipient
        recipient: Optional[Recipient] = db.execute(
            select(Recipient).where(
                Recipient.campaign_id == campaign.id,
                Recipient.status == RecipientStatus.pending,
            ).order_by(Recipient.id.asc()).limit(1)
        ).scalar_one_or_none()

        if recipient is None:
            # complete campaign
            campaign.status = CampaignStatus.completed
            db.commit()
            return

        # decrypt SMTP creds
        username = decrypt_str(campaign.smtp_username_enc)
        password = decrypt_str(campaign.smtp_password_enc)

        recipient.last_attempt_at = datetime.now(timezone.utc)
        db.commit()

        try:
            message_id, smtp_response = send_email_smtp(
                smtp_host=campaign.smtp_host,
                smtp_port=campaign.smtp_port,
                smtp_username=username,
                smtp_password=password,
                use_starttls=campaign.smtp_tls,
                from_email=campaign.from_email or username,
                from_name=campaign.from_name,
                to_email=recipient.to_email,
                subject=campaign.subject,
                body=campaign.body,
                use_ssl=campaign.smtp_ssl,
            )

            recipient.status = RecipientStatus.sent
            recipient.sent_at = datetime.now(timezone.utc)
            recipient.last_error = None

            se = SentEmail(
                campaign_id=campaign.id,
                recipient_id=recipient.id,
                subject=campaign.subject,
                message_id=message_id,
                smtp_response=smtp_response,
                status="sent",
                attempts=1,
                delivered_at=recipient.sent_at,
                error=None,
            )
            db.add(se)
            db.commit()
        except Exception as e:  # noqa: BLE001
            err = str(e)
            recipient.status = RecipientStatus.failed
            recipient.last_error = err

            se = SentEmail(
                campaign_id=campaign.id,
                recipient_id=recipient.id,
                subject=campaign.subject,
                message_id=None,
                smtp_response=None,
                status="failed",
                attempts=1,
                delivered_at=None,
                error=err,
            )
            db.add(se)
            db.commit()

        # schedule next if pending remain
        remaining = db.execute(
            select(Recipient).where(
                Recipient.campaign_id == campaign.id,
                Recipient.status == RecipientStatus.pending,
            ).limit(1)
        ).scalar_one_or_none()

        if remaining is not None and campaign.status == CampaignStatus.running:
            delay = _get_delay_seconds(campaign)
            send_next_email.apply_async(args=[campaign.id], countdown=delay)
        else:
            # No remaining -> mark completed if not already
            if campaign.status == CampaignStatus.running:
                campaign.status = CampaignStatus.completed
                db.commit()
    finally:
        db.close()
