from __future__ import annotations

import smtplib
import ssl
from fastapi import APIRouter

from ..schemas import SMTPVerifyIn, SMTPVerifyOut

router = APIRouter(prefix="/smtp", tags=["smtp"])


@router.post("/verify", response_model=SMTPVerifyOut)
def smtp_verify(payload: SMTPVerifyIn) -> SMTPVerifyOut:
    try:
        if payload.smtp_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(payload.smtp_host, payload.smtp_port, context=context, timeout=15) as server:
                server.login(payload.smtp_username, payload.smtp_password)
        else:
            if payload.smtp_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(payload.smtp_host, payload.smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(payload.smtp_username, payload.smtp_password)
            else:
                with smtplib.SMTP(payload.smtp_host, payload.smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.login(payload.smtp_username, payload.smtp_password)
        return SMTPVerifyOut(ok=True)
    except Exception as e:  # noqa: BLE001
        return SMTPVerifyOut(ok=False, detail=str(e))
