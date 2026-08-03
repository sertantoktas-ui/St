#!/usr/bin/env python3
"""
NotebookLM Entegrasyonu Örnek Kullanımı
Claude Code ortamında belge analizi yapmanın farklı yolları
"""

import os
from dotenv import load_dotenv
from notebooklm_integration import NotebookLMIntegration

load_dotenv()

def example_1_basic_analysis():
    """Örnek 1: Temel belge analizi"""
    print("\n" + "=" * 60)
    print("ÖRNEK 1: Temel Belge Analizi")
    print("=" * 60)

    nl = NotebookLMIntegration()

    # Örnek belge
    document_content = """
    Python Programlama Dili

    Python, 1989 yılında Guido van Rossum tarafından oluşturulan
    yüksek düzey, yorumlanan bir programlama dilidir.

    Özellikleri:
    - Dinamik yazma sistemi
    - Okunabilir söz dizimi
    - Geniş standart kütüphane
    - Cross-platform desteği

    Uygulamalar:
    1. Web geliştirme (Django, Flask)
    2. Veri analizi (Pandas, NumPy)
    3. Makine öğrenmesi (TensorFlow, PyTorch)
    4. Bilimsel hesaplamalar
    5. Otomasyon

    Topluluk desteği çok güçlüdür ve hızla büyümektedir.
    """

    # Belge ekle
    print("\n📝 Belge ekleniyor...")
    nl.add_document("python_doc", document_content, "Python Rehberi")

    # Özet oluştur
    print("\n📋 Özet oluşturuluyor...")
    summary = nl.generate_summary("python_doc")
    print(f"\n{summary}")

    # Anahat oluştur
    print("\n📍 Anahat oluşturuluyor...")
    outline = nl.generate_outline("python_doc")
    print(f"\n{outline}")


def example_2_question_answering():
    """Örnek 2: Belge hakkında sorular sorma"""
    print("\n" + "=" * 60)
    print("ÖRNEK 2: Belge Hakkında Sorular Sorma")
    print("=" * 60)

    nl = NotebookLMIntegration()

    document_content = """
    İklim Değişikliği: Sebepler ve Etkiler

    İklim değişikliği, insan faaliyetlerinin neden olduğu
    atmosferik değişikliklerin sonucudur.

    Temel Sebepler:
    1. Fosil yakıtların yakılması (kömür, petrol, doğal gaz)
    2. Ormansızlaştırma
    3. Endüstriyel faaliyetler
    4. Tarım ve hayvancılık

    Başlıca Etkiler:
    - Artan ortalama sıcaklıklar
    - Deniz seviyesinin yükselmesi
    - Ekstrem hava olayları
    - Ekosistem bozulması
    - Tarım verimliliğinin azalması

    Çözüm Yolları:
    - Yenilenebilir enerji kullanımı
    - Ormanlara yatırım
    - Uluslararası işbirliği
    - Teknolojik inovasyonlar
    """

    # Belge ekle
    nl.add_document("climate_doc", document_content, "İklim Değişikliği")

    # Sorular sor
    questions = [
        "İklim değişikliğinin başlıca sebeплeri nelerdir?",
        "Deniz seviyesi neden yükselişe geçmiştir?",
        "Hangi çözüm yolları önerilmektedir?"
    ]

    print("\n💬 Sorular soruluyor:\n")
    for question in questions:
        print(f"\n❓ Soru: {question}")
        answer = nl.ask_document("climate_doc", question)
        print(f"✅ Cevap: {answer[:500]}...")


def example_3_document_comparison():
    """Örnek 3: Çoklu belge karşılaştırması"""
    print("\n" + "=" * 60)
    print("ÖRNEK 3: Çoklu Belge Karşılaştırması")
    print("=" * 60)

    nl = NotebookLMIntegration()

    # İlk belge - Web Geliştirme
    doc1 = """
    Web Geliştirme Ön Uç

    HTML, CSS ve JavaScript kullanarak kullanıcı arabirimleri oluşturulur.

    Teknolojiler:
    - HTML5: Yapı ve anlam
    - CSS3: Stil ve düzen
    - JavaScript: Etkileşim

    Çerçeveler:
    - React: Meta tarafından
    - Vue: İnsan merkezi
    - Angular: Kapsamlı çözüm
    """

    # İkinci belge - Web Geliştirme Arka Uç
    doc2 = """
    Web Geliştirme Arka Uç

    Sunucu tarafında veri işleme ve depolama yapılır.

    Teknolojiler:
    - Python: Basit ve güçlü
    - Node.js: JavaScript sunucuda
    - Java: Kurumsal çözümler

    Veritabanları:
    - PostgreSQL: İlişkisel
    - MongoDB: Belge tabanlı
    - Redis: Hızlı bellek depolama
    """

    nl.add_document("frontend", doc1, "Ön Uç Geliştirme")
    nl.add_document("backend", doc2, "Arka Uç Geliştirme")

    # Farklılıkları bul
    print("\n🔄 Ön uç ve arka uç geliştirme arasındaki farklar:")
    comparison = nl.compare_documents(
        ["frontend", "backend"],
        analysis_type="differences"
    )
    print(f"\n{comparison}")


def example_4_export():
    """Örnek 4: Analiz sonuçlarını dışa aktarma"""
    print("\n" + "=" * 60)
    print("ÖRNEK 4: Analiz Sonuçlarını Dışa Aktarma")
    print("=" * 60)

    nl = NotebookLMIntegration()

    document_content = """
    Yapay Zeka ve Makine Öğrenmesi

    Yapay zeka, bilgisayarların insan benzeri zeka göstermesini sağlar.

    Türleri:
    1. Dar AI: Spesifik görevler için
    2. Genel AI: İnsan seviyesi zeka

    Makine Öğrenmesi Algoritmaları:
    - Denetimli Öğrenme: Etiketli veriler
    - Denetimsiz Öğrenme: Etiketli olmayan veriler
    - Takviyeli Öğrenme: Ödüller tabanlı

    Uygulamalar:
    - Doğal dil işleme
    - Bilgisayar görüşü
    - Tavsiye sistemleri
    - Anomali tespiti
    """

    nl.add_document("ai_doc", document_content, "AI ve ML Rehberi")

    # Markdown olarak dışa aktar
    print("\n📄 Markdown formatında dışa aktarılıyor...")
    markdown_export = nl.export_analysis("ai_doc", format_type="markdown")

    # Dosyaya kaydet
    with open("ai_analysis.md", "w", encoding="utf-8") as f:
        f.write(markdown_export)

    print("✅ ai_analysis.md dosyasına kaydedildi")


def example_5_interactive():
    """Örnek 5: Etkileşimli mod"""
    print("\n" + "=" * 60)
    print("ÖRNEK 5: Etkileşimli Belge Analizi")
    print("=" * 60)

    nl = NotebookLMIntegration()

    print("\n📚 Belge Analiz Sistemi")
    print("-" * 40)

    # Belge gir
    print("\nBelge başlığını girin:")
    title = input(">>> ").strip()

    print("\nBelge içeriğini girin (sonlandırmak için 'END' yazın):")
    content = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        content.append(line)

    doc_id = title.replace(" ", "_").lower()
    nl.add_document(doc_id, "\n".join(content), title)
    print(f"\n✅ Belge '{title}' eklendi")

    # Analiz menüsü
    while True:
        print("\n📋 Analiz Menüsü:")
        print("1. Özet göster")
        print("2. Anahat göster")
        print("3. Soru sor")
        print("4. Çıkış")

        choice = input("\nSeçim (1-4): ").strip()

        if choice == "1":
            summary = nl.generate_summary(doc_id)
            print(f"\n{summary}")

        elif choice == "2":
            outline = nl.generate_outline(doc_id)
            print(f"\n{outline}")

        elif choice == "3":
            question = input("\nSorunuz: ").strip()
            if question:
                answer = nl.ask_document(doc_id, question)
                print(f"\n{answer}")

        elif choice == "4":
            print("\n👋 Çıkılıyor...")
            break


if __name__ == "__main__":
    print("🎯 NotebookLM Entegrasyonu Örnekleri")

    # Örneği seç
    print("\nLütfen bir örnek seçin:")
    print("1. Temel Belge Analizi")
    print("2. Belge Hakkında Sorular Sorma")
    print("3. Çoklu Belge Karşılaştırması")
    print("4. Analiz Sonuçlarını Dışa Aktarma")
    print("5. Etkileşimli Mod")
    print("6. Tüm Örnekleri Çalıştır")

    choice = input("\nSeçim (1-6): ").strip()

    try:
        if choice == "1":
            example_1_basic_analysis()
        elif choice == "2":
            example_2_question_answering()
        elif choice == "3":
            example_3_document_comparison()
        elif choice == "4":
            example_4_export()
        elif choice == "5":
            example_5_interactive()
        elif choice == "6":
            example_1_basic_analysis()
            example_2_question_answering()
            example_3_document_comparison()
            example_4_export()
        else:
            print("❌ Geçersiz seçim")

    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        print("💡 Lütfen .env dosyasında ANTHROPIC_API_KEY'nin ayarlandığından emin olun")
