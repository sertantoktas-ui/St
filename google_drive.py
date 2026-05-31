#!/usr/bin/env python3
"""
Google Drive entegrasyonu — Obsidian export zip'ini Drive'a yükler.

Kurulum:
1. https://console.cloud.google.com adresinden proje oluşturun
2. Google Drive API'yi etkinleştirin
3. OAuth 2.0 Credentials → Desktop app oluşturun
4. credentials.json dosyasını bu klasöre koyun
"""

import io
import os
import json
import pickle
from pathlib import Path
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_PATH = Path("token.pickle")
CREDENTIALS_PATH = Path("credentials.json")
DRIVE_FOLDER_NAME = "claude"


def _get_service():
    """Kimlik doğrulanmış Drive servisi döner."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json bulunamadı. "
                    "Google Cloud Console'dan indirip projenin klasörüne koyun."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return build("drive", "v3", credentials=creds)


def _get_or_create_folder(service, folder_name: str) -> str:
    """Drive'da klasör bul ya da oluştur, ID döner."""
    query = (
        f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' "
        f"and trashed=false"
    )
    result = service.files().list(q=query, fields="files(id, name)").execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"]

    meta = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=meta, fields="id").execute()
    return folder["id"]


def upload_zip(zip_bytes: bytes, filename: str = None) -> str:
    """
    zip_bytes: ZIP içeriği (bytes)
    filename:  Drive'da görünecek dosya adı (None → otomatik)
    Döner: Drive dosya URL'i
    """
    from googleapiclient.http import MediaIoBaseUpload

    if filename is None:
        filename = f"obsidian_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    service = _get_service()
    folder_id = _get_or_create_folder(service, DRIVE_FOLDER_NAME)

    media = MediaIoBaseUpload(
        io.BytesIO(zip_bytes),
        mimetype="application/zip",
        resumable=True,
    )
    meta = {"name": filename, "parents": [folder_id]}
    file = service.files().create(
        body=meta, media_body=media, fields="id, webViewLink"
    ).execute()

    return file.get("webViewLink", f"https://drive.google.com/file/d/{file['id']}/view")


def is_authenticated() -> bool:
    """Token mevcut ve geçerli mi?"""
    if not TOKEN_PATH.exists():
        return False
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
        if creds and creds.valid:
            return True
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "wb") as f:
                pickle.dump(creds, f)
            return True
    except Exception:
        pass
    return False


def revoke_auth():
    """Oturumu kapat."""
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
