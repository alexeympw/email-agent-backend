from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..crypto import encrypt_str
from ..db import get_db
from ..models import Campaign, CampaignStatus, Recipient, RecipientStatus
from ..schemas import (
    CampaignCreate,
    CampaignOut,
    CampaignStatusOut,
)
from ..tasks import send_next_email

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post("/", response_model=CampaignOut)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> CampaignOut:
    if payload.limits_count < 1 or payload.limits_window_seconds < 1:
        raise HTTPException(status_code=400, detail="Invalid limits")

    c = Campaign(
        name=payload.name,
        smtp_host=payload.smtp.smtp_host,
        smtp_port=payload.smtp.smtp_port,
        smtp_username_enc=encrypt_str(payload.smtp.smtp_username),
        smtp_password_enc=encrypt_str(payload.smtp.smtp_password),
        smtp_tls=payload.smtp.smtp_tls,
        smtp_ssl=payload.smtp.smtp_ssl,
        from_email=payload.from_email,
        from_name=payload.from_name,
        subject=payload.subject,
        body=payload.body,
        limit_count=payload.limits_count,
        limit_window_seconds=payload.limits_window_seconds,
        status=CampaignStatus.draft,
    )
    db.add(c)
    db.flush()

    recipients = [
        Recipient(campaign_id=c.id, to_email=r.to_email, to_name=r.to_name, status=RecipientStatus.pending)
        for r in payload.recipients
    ]
    db.add_all(recipients)
    db.commit()
    return CampaignOut(id=c.id, name=c.name)


@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: int, db: Session = Depends(get_db)) -> dict:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status not in (CampaignStatus.draft, CampaignStatus.failed):
        raise HTTPException(status_code=400, detail="Campaign already running or completed")

    has_any = db.execute(
        select(func.count()).select_from(Recipient).where(Recipient.campaign_id == campaign.id)
    ).scalar_one()
    if has_any == 0:
        raise HTTPException(status_code=400, detail="No recipients")

    campaign.status = CampaignStatus.running
    db.commit()

    send_next_email.apply_async(args=[campaign.id], countdown=0)
    return {"status": "started", "id": campaign.id}


@router.get("/{campaign_id}/status", response_model=CampaignStatusOut)
def campaign_status(campaign_id: int, db: Session = Depends(get_db)) -> CampaignStatusOut:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    total = db.execute(
        select(func.count()).select_from(Recipient).where(Recipient.campaign_id == campaign.id)
    ).scalar_one()
    sent = db.execute(
        select(func.count()).select_from(Recipient).where(
            Recipient.campaign_id == campaign.id, Recipient.status == RecipientStatus.sent
        )
    ).scalar_one()
    failed = db.execute(
        select(func.count()).select_from(Recipient).where(
            Recipient.campaign_id == campaign.id, Recipient.status == RecipientStatus.failed
        )
    ).scalar_one()
    pending = total - sent - failed
    progress_pct = (sent / total * 100.0) if total > 0 else 0.0

    return CampaignStatusOut(
        id=campaign.id,
        status=campaign.status.value,
        total=total,
        sent=sent,
        failed=failed,
        pending=pending,
        progress_pct=round(progress_pct, 2),
    )
