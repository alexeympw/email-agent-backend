from __future__ import annotations

import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Optional, Tuple


def send_email_smtp(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    use_starttls: bool,
    from_email: str,
    from_name: Optional[str],
    to_email: str,
    subject: str,
    body: str,
    use_ssl: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    msg = MIMEText(body, _charset="utf-8")
    sender = formataddr((from_name or "", from_email))
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host=smtp_host, port=smtp_port, context=context, timeout=30) as server:
            server.login(smtp_username, smtp_password)
            resp = server.sendmail(from_addr=from_email, to_addrs=[to_email], msg=msg.as_string())
            return None, str(resp) if resp else "250 OK"

    if use_starttls:
        context = ssl.create_default_context()
        with smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            resp = server.sendmail(from_addr=from_email, to_addrs=[to_email], msg=msg.as_string())
            return None, str(resp) if resp else "250 OK"
    else:
        with smtplib.SMTP(host=smtp_host, port=smtp_port, timeout=30) as server:
            server.ehlo()
            server.login(smtp_username, smtp_password)
            resp = server.sendmail(from_addr=from_email, to_addrs=[to_email], msg=msg.as_string())
            return None, str(resp) if resp else "250 OK"
