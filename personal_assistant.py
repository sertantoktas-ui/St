#!/usr/bin/env python3
"""
Claude API ile destekli kişisel asistan uygulaması
Özellikler:
- Email yazma
- Rapor oluşturma
- Web arama
- Görev yönetimi
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# .env dosyasından API anahtarını yükle
load_dotenv()

# Anthropic istemcisini başlat
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Sistem istemi - Asistanın davranışını tanımla
SYSTEM_PROMPT = """
Sen bir kişisel asistansın. Kullanıcıya aşağıdaki konularda yardım edersin:

1. **Email Yazma**: Profesyonel ve kişisel emailler yazmasına yardım et
2. **Rapor Oluşturma**: Detaylı raporlar ve özetler hazırla
3. **Web Arama**: İnternet'ten bilgi topla ve özetle
4. **Görev Yönetimi**: Görevleri planla, organize et ve takip et

Kullanıcı her bir özellik için seni şu şekilde kullanabilir:
- "Email yaz: [konu ve detaylar]" → Profesyonel bir email taslağı oluştur
- "Rapor yap: [konu]" → Detaylı bir rapor hazırla
- "Ara: [konu]" → Web'den bilgi topla
- "Görev: [görev tanımı]" → Görev planlaması yap

Her zaman yapılandırılmış, kullanımı kolay yanıtlar ver.
"""

def create_assistant():
    """Asistan konuşması başlat"""
    conversation_history = []

    print("=" * 60)
    print("🤖 Kişisel Asistan - Claude AI Destekli")
    print("=" * 60)
    print("\nKullanılabilir komutlar:")
    print("  'email' - Email yazma")
    print("  'rapor' - Rapor oluşturma")
    print("  'ara' - Web arama")
    print("  'gorev' - Görev yönetimi")
    print("  'cikis' - Çıkış")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n📝 Siz: ").strip()

            if not user_input:
                print("⚠️  Lütfen bir komut girin.")
                continue

            if user_input.lower() == 'cikis':
                print("\n👋 Hoşça kalın!")
                break

            # Konuşma geçmişine kullanıcı mesajını ekle
            conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # Claude API'ye istek gönder
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=conversation_history
            )

            # Yanıtı al
            assistant_message = response.content[0].text

            # Konuşma geçmişine asistan yanıtını ekle
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Yanıtı göster
            print(f"\n🤖 Asistan:\n{assistant_message}")

        except KeyboardInterrupt:
            print("\n\n⌨️  Çıkış yapılıyor...")
            break
        except Exception as e:
            print(f"\n❌ Hata oluştu: {str(e)}")

if __name__ == "__main__":
    create_assistant()
