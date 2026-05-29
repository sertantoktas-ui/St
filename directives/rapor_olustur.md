# Rapor Oluşturma — SOP

## Amaç
Kullanıcının verdiği başlık ve içerikten PDF raporu oluşturmak, veritabanına kaydetmek ve indirilebilir hale getirmek.

## Girdiler
- `title`: Rapor başlığı
- `content`: Rapor metni (düz metin veya Markdown)
- `report_type`: `Özet` | `Detaylı` | `Analiz`
- `export_pdf`: `true` | `false` (varsayılan: true)

## Kullanılacak Script
`execution/report_operations.py`

## Akış
1. `report_operations.save_report()` ile içeriği veritabanına kaydet.
2. `export_pdf=True` ise `report_operations.generate_pdf()` çağır.
3. PDF dosya yolunu DB kaydına ekle.
4. Streamlit'te indirme butonu sun.

## Çıktılar
- Report ID (DB kaydı)
- PDF dosya yolu (örn. `reports/report_20260101_120000.pdf`)

## Edge Cases
- ReportLab yoksa pip install reportlab ile yükle.
- İçerik çok uzunsa truncate etme, tüm sayfaları oluştur.
- Türkçe karakter sorunları için Helvetica yerine DejaVu font kullanmayı dene.

## Öğrenilen Kısıtlar
- `reports/` dizini otomatik oluşturulur.
- PDF oluşturma yaklaşık 1-3 saniye sürer.
