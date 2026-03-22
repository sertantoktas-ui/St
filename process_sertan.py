#!/usr/bin/env python3
"""
SERTAN Dosyasını NotebookLM Entegrasyonuyla İşle
"""

import os
from dotenv import load_dotenv
from notebooklm_integration import (
    summarize_notes,
    extract_key_points,
    generate_qa,
    create_study_guide
)

# .env dosyasından yükle
load_dotenv()

# SERTAN.md dosyasını oku
with open("SERTAN.md", "r", encoding="utf-8") as f:
    sertan_content = f.read()


def process_sertan():
    """SERTAN dosyasını entegrasyon fonksiyonlarıyla işle"""

    print("\n" + "="*80)
    print("📚 SERTAN - NotebookLM Entegrasyonu ile İşleme")
    print("="*80)

    # 1. ÖZET YAPMA
    print("\n" + "─"*80)
    print("1️⃣  KISA ÖZET")
    print("─"*80)
    try:
        summary = summarize_notes(
            sertan_content,
            summary_length="short",
            language="tr"
        )
        print(summary)
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("💡 API anahtarınızı kontrol edin!")
        return

    # 2. ANA NOKTALAR
    print("\n" + "─"*80)
    print("2️⃣  ANA NOKTALAR (8 Nokta)")
    print("─"*80)
    try:
        key_points = extract_key_points(
            sertan_content,
            max_points=8
        )
        if isinstance(key_points, list):
            for i, point in enumerate(key_points, 1):
                print(f"  {i}. {point}")
        else:
            print(key_points)
    except Exception as e:
        print(f"❌ Hata: {e}")

    # 3. SORU-CEVAP
    print("\n" + "─"*80)
    print("3️⃣  SORU-CEVAP SETİ (5 Soru)")
    print("─"*80)
    try:
        qa_set = generate_qa(
            sertan_content,
            question_count=5,
            difficulty="medium"
        )

        if isinstance(qa_set, list):
            for i, item in enumerate(qa_set, 1):
                print(f"\n  ❓ Soru {i}: {item.get('question', 'N/A')}")
                print(f"  ✅ Cevap: {item.get('answer', 'N/A')}")
        else:
            print(qa_set)
    except Exception as e:
        print(f"❌ Hata: {e}")

    # 4. ÇALIŞMA REHBERİ
    print("\n" + "─"*80)
    print("4️⃣  YAPILI ÇALIŞMA REHBERİ")
    print("─"*80)
    try:
        study_guide = create_study_guide(
            sertan_content,
            format="structured"
        )
        print(study_guide)
    except Exception as e:
        print(f"❌ Hata: {e}")

    # 5. ÖZETLERİ DOSYAYA KAY
    print("\n" + "─"*80)
    print("5️⃣  SONUÇLAR DOSYAYA KAYDEDILIYOR")
    print("─"*80)

    try:
        output = f"""# SERTAN - NotebookLM Entegrasyonu Sonuçları

## Tarih: {os.popen('date').read().strip()}

### 1. Kısa Özet
{summary}

### 2. Ana Noktalar
"""
        if isinstance(key_points, list):
            for i, point in enumerate(key_points, 1):
                output += f"{i}. {point}\n"

        output += "\n### 3. Soru-Cevap Seti\n"
        if isinstance(qa_set, list):
            for i, item in enumerate(qa_set, 1):
                output += f"\n**Soru {i}:** {item.get('question', 'N/A')}\n"
                output += f"**Cevap:** {item.get('answer', 'N/A')}\n"

        output += "\n### 4. Çalışma Rehberi\n"
        output += study_guide

        # Dosyaya kaydet
        with open("SERTAN_PROCESSED.md", "w", encoding="utf-8") as f:
            f.write(output)

        print("✅ SERTAN_PROCESSED.md dosyası oluşturuldu!")
        print("📁 Dosya yolu: ./SERTAN_PROCESSED.md")

    except Exception as e:
        print(f"❌ Dosya kaydetme hatası: {e}")

    print("\n" + "="*80)
    print("✨ İşlem Tamamlandı!")
    print("="*80)
    print("\n💡 İpuçları:")
    print("   - SERTAN_PROCESSED.md dosyasını görüntüle")
    print("   - Sonuçları NotebookLM'e kopyala")
    print("   - Sorularla kendinizi test et")
    print("   - Rehberi çalışma materyali olarak kullan")
    print()


if __name__ == "__main__":
    process_sertan()
