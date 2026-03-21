#!/usr/bin/env python3
"""
Tam Özellikli Claude AI Kişisel Asistan
- Database ile kalıcı depolama
- SMTP ile gerçek email gönderme
- PDF rapor oluşturma
- Tool Use desteği
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from database import AssistantDatabase
from email_service import EmailService
from pdf_generator import PDFReportGenerator

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
db = AssistantDatabase()
pdf_gen = PDFReportGenerator()

# Email servisi (opsiyonel - .env'de ayarlanmışsa)
try:
    email_service = EmailService()
    email_available = True
except:
    email_service = None
    email_available = False

# Tanımlı araçlar
TOOLS = [
    {
        "name": "create_email",
        "description": "Profesyonel bir email metni oluşturur ve veritabanına kaydeder",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "Alıcının adı veya email adresi"},
                "subject": {"type": "string", "description": "Email konusu"},
                "body": {"type": "string", "description": "Email gövdesi"},
                "tone": {"type": "string", "enum": ["formal", "casual", "friendly"]},
                "send_now": {"type": "boolean", "description": "Hemen gönder?"}
            },
            "required": ["recipient", "subject", "body", "tone"]
        }
    },
    {
        "name": "create_report",
        "description": "Detaylı rapor oluşturur ve PDF olarak kaydeder",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Rapor başlığı"},
                "content": {"type": "string", "description": "Rapor içeriği"},
                "format": {"type": "string", "enum": ["markdown", "text", "html"]},
                "export_pdf": {"type": "boolean", "description": "PDF olarak dışa aktar?"}
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "manage_task",
        "description": "Görevleri yönet (ekle, listele, tamamla)",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "complete"]},
                "title": {"type": "string", "description": "Görev başlığı"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_statistics",
        "description": "Asistan istatistiklerini al",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Araç fonksiyonlarını çalıştır"""

    if tool_name == "create_email":
        return create_email(tool_input)

    elif tool_name == "create_report":
        return create_report(tool_input)

    elif tool_name == "manage_task":
        return manage_task(tool_input)

    elif tool_name == "get_statistics":
        return get_statistics()

    return f"Bilinmeyen araç: {tool_name}"

def create_email(tool_input: dict) -> str:
    """Email oluştur ve kaydet"""
    recipient = tool_input["recipient"]
    subject = tool_input["subject"]
    body = tool_input["body"]
    tone = tool_input["tone"]
    send_now = tool_input.get("send_now", False)

    # Veritabanına kaydet
    email_id = db.save_email(recipient, subject, body, tone)

    result = f"""
    📧 EMAIL OLUŞTURULDU
    {'=' * 50}
    Alıcı: {recipient}
    Konu: {subject}
    Ton: {tone}
    Email ID: {email_id}
    Oluşturulma: {datetime.now().strftime('%H:%M:%S')}

    İçerik:
    {body}
    {'=' * 50}
    """

    # Gönder (eğer istenirse)
    if send_now and email_available:
        success = email_service.send_email(recipient, subject, body)
        if success:
            db.mark_email_sent(email_id)
            result += "\n✅ Email başarıyla gönderildi!"
        else:
            result += "\n❌ Email gönderme başarısız oldu."
    else:
        result += "\n💾 Email veritabanında kaydedildi (henüz gönderilmedi)"

    return result

def create_report(tool_input: dict) -> str:
    """Rapor oluştur"""
    title = tool_input["title"]
    content = tool_input["content"]
    format_type = tool_input.get("format", "text")
    export_pdf = tool_input.get("export_pdf", True)

    # Veritabanına kaydet
    report_id = db.save_report(title, content, format_type)

    pdf_path = None
    if export_pdf:
        try:
            pdf_path = pdf_gen.generate_from_text(title, content)
        except Exception as e:
            print(f"❌ PDF oluşturma hatası: {str(e)}")

    result = f"""
    📄 RAPOR OLUŞTURULDU
    {'=' * 50}
    Başlık: {title}
    Format: {format_type}
    Rapor ID: {report_id}
    Oluşturulma: {datetime.now().strftime('%H:%M:%S')}

    İçerik:
    {content[:500]}{'...' if len(content) > 500 else ''}
    {'=' * 50}
    """

    if export_pdf and pdf_path:
        result += f"\n✅ PDF dosyası oluşturuldu: {pdf_path}"
    else:
        result += "\n💾 Rapor veritabanında kaydedildi"

    return result

def manage_task(tool_input: dict) -> str:
    """Görevleri yönet"""
    action = tool_input["action"]

    if action == "add":
        title = tool_input.get("title", "Başlık yok")
        priority = tool_input.get("priority", "medium")
        task_id = db.add_task(title, priority=priority)
        return f"✅ Görev eklendi (ID: {task_id}): {title}"

    elif action == "list":
        tasks = db.get_tasks("pending")
        if not tasks:
            return "📋 Beklemede görev yok"

        task_list = "📋 Görevler:\n"
        for task in tasks:
            task_list += f"\n  ⭕ [{task['priority'].upper()}] {task['title']}"
            task_list += f"\n     Oluşturulma: {task['created_at']}"

        return task_list

    elif action == "complete":
        title = tool_input.get("title", "")
        # Görev başlığına göre ID'yi bul ve tamamla
        tasks = db.get_tasks("pending")
        for task in tasks:
            if task['title'].lower() == title.lower():
                if db.complete_task(task['id']):
                    return f"✅ Görev tamamlandı: {title}"

        return f"❌ Görev bulunamadı: {title}"

    return "❌ Bilinmeyen işlem"

def get_statistics() -> str:
    """İstatistikleri al"""
    stats = db.get_statistics()

    result = f"""
    📊 ASISTAN İSTATİSTİKLERİ
    {'=' * 40}
    ✅ Tamamlanan Görevler: {stats['completed_tasks']}
    ⭕ Beklemede Görevler: {stats['pending_tasks']}

    📧 EMAIL
    ✉️  Gönderilen: {stats['sent_emails']}
    📬 Gönderilmeyen: {stats['unsent_emails']}

    📄 RAPORLAR
    📋 Toplam: {stats['total_reports']}
    {'=' * 40}
    """

    return result

def run_full_assistant():
    """Tam özellikli asistanı çalıştır"""
    conversation_history = []

    system_prompt = """
    Sen bir tam özellikli yapay zeka kişisel asistansısın. Aşağıdaki özellikleri kullanabilirsin:

    1. EMAIL OLUŞTURMA: create_email aracını kullanarak profesyonel emailler oluştur
    2. RAPOR OLUŞTURMA: create_report aracını kullanarak PDF raporları oluştur
    3. GÖREV YÖNETİMİ: manage_task aracını kullanarak görevleri yönet
    4. İSTATİSTİKLER: get_statistics aracını kullanarak istatistikleri göster

    Her işlem için uygun aracı kullan ve sonuçları açıkla.
    Veritabanında kalıcı olarak bilgiler depolanır.
    """

    print("=" * 60)
    print("🤖 Tam Özellikli Personal Asistan")
    print("=" * 60)
    print("\n✨ Özellikler:")
    print("  📧 Email yazma ve gönderme")
    print("  📄 PDF rapor oluşturma")
    print("  ✅ Görev yönetimi (veritabanı)")
    print("  📊 İstatistikler")
    print("  💾 Kalıcı depolama")

    if email_available:
        print("  📮 Email gönderme: ✅ Aktif")
    else:
        print("  📮 Email gönderme: ⚠️  Yapılandırılmadı (.env'i kontrol et)")

    print("\n" + "-" * 60)
    print("\n📝 Örnek Komutlar:")
    print("  'Email yaz: Müşteriye proje tamamlandı'")
    print("  'Rapor yap: 2024 Satış Özeti'")
    print("  'Görev ekle: Sunum hazırla'")
    print("  'İstatistikleri göster'")
    print("  'Görevleri listele'")
    print("  'cikis' - Çıkış")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n📝 Siz: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'cikis':
                print("\n👋 Hoşça kalın!")
                break

            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # API'ye istek gönder
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=conversation_history
            )

            # Yanıtı işle
            if response.stop_reason == "tool_use":
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"\n🔧 {tool_name} çalıştırılıyor...")

                        tool_result = execute_tool(tool_name, tool_input)
                        print(tool_result)

                        conversation_history.append({
                            "role": "assistant",
                            "content": response.content
                        })

                        conversation_history.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": tool_result
                                }
                            ]
                        })

                        # Sonuç hakkında açıklama iste
                        final_response = client.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=1024,
                            system=system_prompt,
                            tools=TOOLS,
                            messages=conversation_history
                        )

                        final_text = next(
                            (b.text for b in final_response.content if hasattr(b, 'text')),
                            ""
                        )

                        if final_text:
                            print(f"\n🤖 Asistan: {final_text}")

                        conversation_history.append({
                            "role": "assistant",
                            "content": final_response.content
                        })
            else:
                assistant_message = next(
                    (b.text for b in response.content if hasattr(b, 'text')),
                    ""
                )

                if assistant_message:
                    print(f"\n🤖 Asistan: {assistant_message}")

                conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })

        except KeyboardInterrupt:
            print("\n\n⌨️  Çıkış yapılıyor...")
            break
        except Exception as e:
            print(f"\n❌ Hata: {str(e)}")

if __name__ == "__main__":
    run_full_assistant()
