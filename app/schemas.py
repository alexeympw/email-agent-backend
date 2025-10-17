from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class SMTPSettings(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_tls: bool = True
    smtp_ssl: bool = False


class RecipientIn(BaseModel):
    to_email: EmailStr
    to_name: Optional[str] = None


class CampaignCreate(BaseModel):
    name: str
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None

    subject: str
    body: str

    limits_count: int = Field(1, ge=1)
    limits_window_seconds: int = Field(3600, ge=1)

    smtp: SMTPSettings
    recipients: List[RecipientIn]


class CampaignOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CampaignStatusOut(BaseModel):
    id: int
    status: str
    total: int
    sent: int
    failed: int
    pending: int
    progress_pct: float


class SMTPVerifyIn(SMTPSettings):
    pass


class SMTPVerifyOut(BaseModel):
    ok: bool
    detail: Optional[str] = None
