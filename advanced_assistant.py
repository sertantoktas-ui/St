#!/usr/bin/env python3
"""
İleri Özellikleri ile Claude API Kişisel Asistan
- Tool Use (Araç Kullanımı)
- Web Arama
- Email Oluşturma
- Rapor Üretme
"""

import os
import json
import requests
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# .env dosyasından yükle
load_dotenv()

# İstemci başlat
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Tanımlı araçlar
TOOLS = [
    {
        "name": "create_email",
        "description": "Profesyonel bir email metni oluşturur",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {
                    "type": "string",
                    "description": "Alıcının adı veya email adresi"
                },
                "subject": {
                    "type": "string",
                    "description": "Email konusu"
                },
                "body": {
                    "type": "string",
                    "description": "Email gövdesi"
                },
                "tone": {
                    "type": "string",
                    "enum": ["formal", "casual", "friendly"],
                    "description": "Email tonu"
                }
            },
            "required": ["recipient", "subject", "body", "tone"]
        }
    },
    {
        "name": "create_report",
        "description": "Bir konu hakkında detaylı rapor oluşturur",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Rapor başlığı"
                },
                "content": {
                    "type": "string",
                    "description": "Rapor içeriği"
                },
                "format": {
                    "type": "string",
                    "enum": ["markdown", "text", "html"],
                    "description": "Rapor formatı"
                }
            },
            "required": ["title", "content", "format"]
        }
    },
    {
        "name": "search_web",
        "description": "Web'de bir konu hakkında bilgi arar",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak konu"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "manage_task",
        "description": "Görev ekle, kaldır veya listele",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "remove", "list", "complete"],
                    "description": "Yapılacak işlem"
                },
                "task": {
                    "type": "string",
                    "description": "Görev açıklaması"
                }
            },
            "required": ["action"]
        }
    }
]

# Görev veritabanı (basit)
tasks = []

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Araç fonksiyonlarını çalıştır"""

    if tool_name == "create_email":
        return create_email(
            tool_input["recipient"],
            tool_input["subject"],
            tool_input["body"],
            tool_input["tone"]
        )

    elif tool_name == "create_report":
        return create_report(
            tool_input["title"],
            tool_input["content"],
            tool_input["format"]
        )

    elif tool_name == "search_web":
        return search_web(tool_input["query"])

    elif tool_name == "manage_task":
        return manage_task(
            tool_input["action"],
            tool_input.get("task", "")
        )

    else:
        return f"Bilinmeyen araç: {tool_name}"

def create_email(recipient: str, subject: str, body: str, tone: str) -> str:
    """Email oluştur"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    email_content = f"""
📧 EMAIL OLUŞTURULDU
{'=' * 50}
Alıcı: {recipient}
Konu: {subject}
Ton: {tone}
Oluşturma Zamanı: {timestamp}

İçerik:
{body}

{'=' * 50}
✅ Email hazır, gönderilebilir durumda.
"""
    return email_content

def create_report(title: str, content: str, format_type: str) -> str:
    """Rapor oluştur"""
    timestamp = datetime.now().strftime("%Y-%m-%d")

    if format_type == "markdown":
        report = f"# {title}\n\n**Oluşturulma Tarihi:** {timestamp}\n\n{content}"
    elif format_type == "html":
        report = f"<h1>{title}</h1><p><em>Oluşturulma Tarihi: {timestamp}</em></p><div>{content}</div>"
    else:
        report = f"{title}\n{'=' * len(title)}\nTarih: {timestamp}\n\n{content}"

    return f"📄 Rapor Oluşturuldu:\n\n{report}"

def search_web(query: str) -> str:
    """Web'de arama yap (simüle)"""
    # Not: Gerçek bir web arama için DuckDuckGo, Google API vb. kullanabilirsiniz
    return f"""
🔍 Web Arama Sonuçları: "{query}"
{'=' * 50}

[Simüle Edilmiş Sonuçlar]
- Sonuç 1: {query} hakkında detaylı bilgi
- Sonuç 2: {query} ile ilgili güncel haberler
- Sonuç 3: {query} tutoriyalleri ve kılavuzları

💡 İpucu: Gerçek web araması için DuckDuckGo veya Google API
entegrasyonu ekleyebilirsiniz.
"""

def manage_task(action: str, task: str = "") -> str:
    """Görevleri yönet"""
    global tasks

    if action == "add" and task:
        tasks.append({"task": task, "completed": False, "created": datetime.now()})
        return f"✅ Görev eklendi: {task}"

    elif action == "remove" and task:
        tasks = [t for t in tasks if t["task"] != task]
        return f"🗑️  Görev kaldırıldı: {task}"

    elif action == "complete" and task:
        for t in tasks:
            if t["task"] == task:
                t["completed"] = True
                return f"✔️  Görev tamamlandı: {task}"
        return f"❌ Görev bulunamadı: {task}"

    elif action == "list":
        if not tasks:
            return "📋 Görev yok"
        task_list = "\n".join([
            f"{'✔️' if t['completed'] else '⭕'} {t['task']}"
            for t in tasks
        ])
        return f"📋 Görevler:\n{task_list}"

    return "❌ Bilinmeyen işlem"

def run_assistant():
    """Asistanı çalıştır - Tool Use döngüsü ile"""
    conversation_history = []

    system_prompt = """
    Sen bir yapay zeka kişisel asistansısın. Aşağıdaki araçları kullanabilirsin:
    - create_email: Profesyonel emailler oluştur
    - create_report: Detaylı raporlar hazırla
    - search_web: Web'den bilgi ara
    - manage_task: Görevleri yönet

    Kullanıcının isteklerine göre uygun araçları kullanarak yardımcı ol.
    """

    print("=" * 60)
    print("🤖 İleri Kişisel Asistan (Tool Use Destekli)")
    print("=" * 60)
    print("\nÖrnekler:")
    print("  'Email yaz: Müşteriye proje tamamlandı raporu'")
    print("  'Rapor yap: 2024 Yıl Sonu Özeti'")
    print("  'Ara: Yapay zeka trendleri 2024'")
    print("  'Görev ekle: Sunuyu hazırla'")
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

            # Konuşma geçmişine ekle
            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # API'ye istek gönder (Tool Use ile)
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=conversation_history
            )

            # Yanıtı işle
            if response.stop_reason == "tool_use":
                # Araç kullanım bloğunu bul
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input

                        print(f"\n🔧 Araç kullanılıyor: {tool_name}")
                        print(f"   Parametreler: {json.dumps(tool_input, ensure_ascii=False)}")

                        # Aracı çalıştır
                        tool_result = execute_tool(tool_name, tool_input)

                        # Sonuçları göster
                        print(f"\n{tool_result}")

                        # Konuşma geçmişine araç sonucunu ekle
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

                        # Sonuç hakkında asistandan yorum iste
                        final_response = client.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=1024,
                            system=system_prompt,
                            tools=TOOLS,
                            messages=conversation_history
                        )

                        final_text = next(
                            (b.text for b in final_response.content if hasattr(b, 'text')),
                            "İşlem tamamlandı."
                        )

                        print(f"\n🤖 Asistan: {final_text}")

                        conversation_history.append({
                            "role": "assistant",
                            "content": final_response.content
                        })
            else:
                # Normal yanıt
                assistant_message = next(
                    (b.text for b in response.content if hasattr(b, 'text')),
                    "Yanıt alınamadı."
                )

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
    run_assistant()
