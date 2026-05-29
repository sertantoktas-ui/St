# AXTEA CNC HMI

3 eksen CNC makinesi için Windows 11 uyumlu HMI uygulaması.  
OSAI C07/C11 kontrol ünitesiyle TCP/IP üzerinden haberleşir.

## Kurulum

```bash
pip install PyQt5 PyQtChart
```

## Çalıştırma

```bash
cd hmi
python main.py
```
veya `run.bat` dosyasına çift tıklayın.

## OSAI Bağlantısı

1. Sağ üstteki **Connect** butonuna tıklayın
2. OSAI ünitesinin IP adresini ve port numarasını girin (varsayılan: `192.168.1.10:5050`)
3. Gerçek makineye bağlanmak için **Simulation** kutusunu kaldırın

Simülasyon modunda tüm eksenler, hız ve yük değerleri otomatik üretilir.

## Özellikler

| Özellik | Açıklama |
|---|---|
| 3 eksen görüntü | X/Y/Z makine + iş koordinatları |
| Override | İlerleme ve mil hızı %0–200 arasında ayarlanabilir |
| Program kontrolü | Başlat / Durdur / Beklet / Sıfırla / Referans Al |
| Yük göstergesi | X/Y/Z ekseni + mil motor yükleri |
| Hız göstergesi | Dairesel gösterge (feed + spindle) |
| Enerji grafiği | Gerçek zamanlı sparkline |
| Notlar | Operatör notu ekle/sil |
| Alarm listesi | Aktif alarm listesi (Inspect ekranı) |
| Analiz | Haftalık üretim grafiği |
| 7 dil | TR, EN, DE, FR, IT, ES, ZH |

## Kurumsal Renkler

- Ana Mavi: `#535DDC`
- Lacivert: `#141E23`
- Açık Mavi: `#E3E6FF`
- Yeşil Aksan: `#00B581`
- Amber Uyarı: `#F5A623`
