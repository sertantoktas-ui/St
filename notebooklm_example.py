#!/usr/bin/env python3
"""
NotebookLM + Claude API Entegrasyonu - Hızlı Örnek
"""

from notebooklm_integration import (
    summarize_notes,
    extract_key_points,
    generate_qa,
    create_study_guide,
    interactive_notebooklm_session
)

# Örnek: NotebookLM'den alınmış bir konu
SAMPLE_NOTEBOOKLM_CONTENT = """
Fotosintez: Bitkiler Güneş Enerjisini Nasıl Kullanır?

Fotosintez, bitkiler tarafından güneş ışığını kimyasal enerjiye dönüştürme işlemidir.
Bu, Dünya'daki hayatın en temel süreçlerinden biridir.

Fotosintez Formülü:
6CO₂ + 6H₂O + ışık → C₆H₁₂O₆ + 6O₂

İki Temel Aşama:

1. Işık Reaksiyonları (Açık Reaksiyonlar)
   - Yer: Kloroplastin tilakoid membranı
   - Girdi: Su ve ışık
   - Çıktı: ATP, NADPH ve O₂
   - Klorofil ve diğer pigmentler ışığı absorbe eder
   - Elektron zinciri enerji sağlar

2. Karanlık Reaksiyonları (Calvin Döngüsü)
   - Yer: Kloroplastin stroma
   - Girdi: CO₂, ATP, NADPH
   - Çıktı: Glikoz (şeker)
   - Karbonfiksasyon: CO₂ 3-fosfogliserat'a dönüşür
   - Gliseral-3-fosfat oluşur
   - Gliserat-1,3-bisfosfat glikoza dönüştürülür

Önemli Pigmentler:
- Klorofil a: Birincil ışık absorblayıcı
- Klorofil b: Yardımcı pigment
- Karotenoidler: Koruma ve emilim
- Ksantofil: Sarı pigment

Faktörler Fotosintez Hızını Etkiler:
1. Işık Şiddeti: Arttıkça fotosintez artar (belirli sınıra kadar)
2. CO₂ Konsantrasyonu: Arttıkça fotosintez artar
3. Sıcaklık: 25-35°C optimal aralık
4. Su Kullanılabilirliği: Su kuraklığında azalır

Bitkiler İçin Önem:
- Besince ürünleri (glikoz) sağlar
- Oksijen üretir (havadaki O₂'nin çoğu)
- Atmosferdeki CO₂ kontrol eder
- Enerji depolama

İnsan ve Dünya İçin:
- Gıda kaynağı (tüm bitkiler)
- Oksijen üretimi (yaşamsal)
- Fosil yakıtlar eski bitkilerin fotosintezinden
- İklim değişikliğinde rol oynar
"""


def demo_all_features():
    """Tüm özellikleri gösteren demo"""
    print("\n" + "="*70)
    print("NotebookLM + Claude API - Tüm Özellikleri Göster")
    print("="*70)

    print("\n📖 Örnek Konu: Fotosintez")
    print("-" * 70)

    # 1. ÖZET YAPMA
    print("\n1️⃣  KISA ÖZET:")
    print("-" * 70)
    short_summary = summarize_notes(
        SAMPLE_NOTEBOOKLM_CONTENT,
        summary_length="short",
        language="tr"
    )
    print(short_summary)

    # 2. ANA NOKTALAR
    print("\n2️⃣  ANA NOKTALAR (7 Nokta):")
    print("-" * 70)
    key_points = extract_key_points(
        SAMPLE_NOTEBOOKLM_CONTENT,
        max_points=7
    )
    for i, point in enumerate(key_points, 1):
        print(f"{i}. {point}")

    # 3. SORU-CEVAP
    print("\n3️⃣  SORU-CEVAP SETİ (Orta Zorluk):")
    print("-" * 70)
    qa_set = generate_qa(
        SAMPLE_NOTEBOOKLM_CONTENT,
        question_count=5,
        difficulty="medium"
    )
    for i, item in enumerate(qa_set, 1):
        print(f"\n❓ Soru {i}: {item['question']}")
        print(f"✅ Cevap: {item['answer']}")

    # 4. ÇALIŞMA REHBERİ
    print("\n4️⃣  YAPILI ÇALIŞMA REHBERİ:")
    print("-" * 70)
    study_guide = create_study_guide(
        SAMPLE_NOTEBOOKLM_CONTENT,
        format="structured"
    )
    print(study_guide)

    print("\n" + "="*70)
    print("✅ Demo Tamamlandı!")
    print("="*70)


def demo_quick_start():
    """Hızlı başlangıç demo"""
    print("\n" + "="*70)
    print("NotebookLM + Claude API - Hızlı Başlangıç")
    print("="*70)

    print("\n📚 Küçük Bir Konu ile Başlayalım...")

    small_topic = """
    Python Nedir?

    Python, başlangıçta "Monty Python" tarafından ilham alarak adlandırılan,
    1989 yılında Guido van Rossum tarafından oluşturulan açık kaynaklı bir programlama dilidir.

    Özellikleri:
    - Okunması kolay syntax
    - Dinamik tipe sahip
    - Geniş kütüphane
    - Veri bilimi için ideal
    """

    özet = summarize_notes(small_topic, summary_length="short")
    print(f"\n📝 Özet:\n{özet}")

    noktalar = extract_key_points(small_topic, max_points=3)
    print(f"\n🎯 Ana Noktalar:\n{noktalar}")


def demo_interactive():
    """İnteraktif demo"""
    print("\n" + "="*70)
    print("NotebookLM + Claude API - İnteraktif Mod")
    print("="*70)
    print("\nKendi notlarınızı yazın ve Claude'a soruşturabilirsiniz!")
    print("Örnek komutlar: /özetlet, /noktalar, /sorular, /rehber, /çıkış\n")

    interactive_notebooklm_session()


def main():
    """Ana menu"""
    print("\n" + "="*70)
    print("🚀 NotebookLM - Claude API Entegrasyonu")
    print("="*70)
    print("\nDemo Seçenekleri:")
    print("1. Tüm Özellikleri Göster (Fotosintez Örneği)")
    print("2. Hızlı Başlangıç (Python Örneği)")
    print("3. İnteraktif Mode Gir")
    print("4. Çıkış")
    print("-" * 70)

    choice = input("\nSeçim yapın (1-4): ").strip()

    if choice == "1":
        demo_all_features()
    elif choice == "2":
        demo_quick_start()
    elif choice == "3":
        demo_interactive()
    elif choice == "4":
        print("\nHoşça kalın! 👋")
        return
    else:
        print("\n❌ Geçersiz seçim!")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸  Program durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\n💡 API anahtarınızın doğru ayarlandığından emin olun!")
        print("   .env dosyasında ANTHROPIC_API_KEY tanımlı mı?")
