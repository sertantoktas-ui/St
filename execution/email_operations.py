#!/usr/bin/env python3
"""Email CRUD ve gönderme — deterministik execution katmanı"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AssistantDatabase
from email_service import EmailService

_db = AssistantDatabase()

try:
    _email_svc = EmailService()
    _smtp_available = True
except Exception:
    _email_svc = None
    _smtp_available = False


def save_email(recipient: str, subject: str, body: str, tone: str = "formal") -> dict:
    email_id = _db.save_email(recipient, subject, body, tone)
    return {"success": True, "email_id": email_id, "sent": False}


def send_email(email_id: int, recipient: str, subject: str, body: str) -> dict:
    if not _smtp_available:
        return {"success": False, "error": "SMTP yapılandırılmamış (.env kontrol edin)"}
    ok = _email_svc.send_email(recipient, subject, body)
    if ok:
        _db.mark_email_sent(email_id)
    return {"success": ok, "email_id": email_id}


def save_and_send(recipient: str, subject: str, body: str, tone: str = "formal") -> dict:
    result = save_email(recipient, subject, body, tone)
    if _smtp_available:
        send_result = send_email(result["email_id"], recipient, subject, body)
        result["sent"] = send_result["success"]
        result["send_error"] = send_result.get("error")
    return result


def get_emails(sent_only: bool = False) -> list:
    return _db.get_emails(sent_only)


def smtp_available() -> bool:
    return _smtp_available
