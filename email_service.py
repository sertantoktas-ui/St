#!/usr/bin/env python3
"""
SMTP Email Service - Gerçek Email Gönderme
Desteklenen: Gmail, Outlook, Custom SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Email gönderme servisi"""

    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 sender_email: str = None, sender_password: str = None):
        """
        Email servisi başlat

        Args:
            smtp_server: SMTP sunucu adresi (default: Gmail)
            smtp_port: SMTP portu (default: 587)
            sender_email: Gönderici email
            sender_password: Gönderici şifresi/app password
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", 587))
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD")

        if not self.sender_email or not self.sender_password:
            raise ValueError("SMTP bilgileri eksik. .env dosyasını kontrol edin.")

    def send_email(self, recipient: str, subject: str, body: str,
                   html: bool = False, attachments: List[str] = None) -> bool:
        """
        Email gönder

        Args:
            recipient: Alıcı email adresi
            subject: Email konusu
            body: Email içeriği
            html: HTML format mı?
            attachments: Dosya yolları

        Returns:
            Başarı durumu
        """
        try:
            # Email mesajı oluştur
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient

            # Body ekle
            mime_type = "html" if html else "plain"
            message.attach(MIMEText(body, mime_type))

            # Ekleri ekle
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._attach_file(message, file_path)

            # Gönder
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, message.as_string())

            return True

        except Exception as e:
            print(f"❌ Email gönderme hatası: {str(e)}")
            return False

    def send_bulk_emails(self, recipients: List[dict]) -> dict:
        """
        Toplu email gönder

        Args:
            recipients: [{"email": "...", "subject": "...", "body": "..."}, ...]

        Returns:
            {"sent": 5, "failed": 1}
        """
        results = {"sent": 0, "failed": 0}

        for recipient_info in recipients:
            success = self.send_email(
                recipient_info["email"],
                recipient_info["subject"],
                recipient_info["body"],
                recipient_info.get("html", False)
            )
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1

        return results

    @staticmethod
    def _attach_file(message: MIMEMultipart, file_path: str):
        """Dosyayı email'e ekle"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            message.attach(part)
        except Exception as e:
            print(f"❌ Dosya ekleme hatası ({file_path}): {str(e)}")

    @staticmethod
    def create_professional_email(name: str, subject: str, content: str,
                                   tone: str = "formal") -> str:
        """Profesyonel email şablonu oluştur"""

        greetings = {
            "formal": f"Sayın {name},",
            "casual": f"Merhaba {name},",
            "friendly": f"Hi {name}! 👋"
        }

        closings = {
            "formal": "Saygılarımla,\n[Adınız]",
            "casual": "İyi günler,\n[Adınız]",
            "friendly": "Selamlar! 😊\n[Adınız]"
        }

        email_template = f"""{greetings.get(tone, greetings['formal'])}

{content}

{closings.get(tone, closings['formal'])}"""

        return email_template

    @staticmethod
    def create_html_email(subject: str, content: str, company_name: str = "Personal Assistant") -> str:
        """HTML email şablonu oluştur"""

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{subject}</h2>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>&copy; 2024 {company_name}. Tüm hakları saklıdır.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_template


# Test fonksiyonu
def test_email_service():
    """Email servisi testi"""
    try:
        service = EmailService()

        # Test email oluştur
        test_email = EmailService.create_professional_email(
            name="Test",
            subject="Test",
            content="Bu bir test emailidir.",
            tone="friendly"
        )

        print("✅ Email servisi başlatıldı!")
        print(f"\n📧 Test Email:\n{test_email}")

        # Not: Gerçek email göndermek için SMTP bilgileri gerekli
        print("\n💡 Gerçek email göndermek için .env dosyasında ayarla:")
        print("   SMTP_SERVER=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SENDER_EMAIL=your-email@gmail.com")
        print("   SENDER_PASSWORD=your-app-password")

    except Exception as e:
        print(f"❌ Hata: {str(e)}")

if __name__ == "__main__":
    test_email_service()
