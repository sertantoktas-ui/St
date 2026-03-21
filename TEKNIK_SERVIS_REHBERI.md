# Teknik Servis Takip ve Planlama Programı

Bir masaüstü uygulaması olarak geliştirilmiş, teknik servis hizmeti sağlayıcıları için kapsamlı takip ve planlama sistemi.

## 🎯 Özellikler

- **Müşteri Yönetimi**: Müşteri bilgilerini kaydedin ve yönetin
- **Teknisyen Yönetimi**: Teknisyenleri ve uzmanlık alanlarını kaydedin
- **Servis Talebi Takibi**: Müşteri taleplerini oluşturun, atayın ve izleyin
- **Zaman Planlama**: Servis randevularını planlayın ve takip edin
- **İstatistikler ve Raporlar**: Gerçek zamanlı iş istatistikleri ve tamamlanma oranları
- **Veritabanı**: Tüm veriler güvenli SQLite veritabanında saklanır

## 📋 Sistem Gereksinimleri

- **Python 3.7+**
- **Windows, macOS veya Linux**

## 💾 Kurulum

### 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

PyQt5 kurulursa, uygulama çalıştırmaya hazır olacaksınız.

### 2. Programı Çalıştırın

```bash
python technical_service_app.py
```

## 📖 Kullanım Kılavuzu

### Ana Sekmeler

#### 1️⃣ **Servis Talepleri Sekmesi**

Tüm servis taleplerini yönetmeniz için merkezi yer.

**Yeni Servis Talebi Ekleme:**
1. "Yeni Servis Talebi" düğmesine tıklayın
2. Müşteri seçin
3. Sorunun açıklamasını yazın
4. Öncelik seviyesini seçin (Düşük/Orta/Yüksek/Acil)
5. Durumu ayarlayın (Açık/Atandı/İnceleme Altında/Tamamlandı)
6. Planlanan tarihi ve saati seçin
7. Teknisyen atayın (opsiyonel)
8. Notlar ekleyin
9. "Kaydet" düğmesini tıklayın

**Servis Talebini Tamamlama:**
1. Tablodan talebini seçin
2. "Tamamla" düğmesini tıklayın
3. Otomatik olarak "Tamamlandı" durumuna geçer ve tamamlanma tarihi kaydedilir

**Tablo Sütunları:**
- **ID**: Servis talebinin benzersiz numarası
- **Müşteri**: Talep sahibinin adı
- **Açıklama**: Sorun açıklaması
- **Öncelik**: Aciliyeti (Düşük/Orta/Yüksek/Acil)
- **Durum**: Mevcut durumu
- **Planlanan Tarih**: Servis yapılacak tarih ve saat
- **Teknisyen**: Atanan teknisyenin adı
- **Notlar**: Ek bilgiler

---

#### 2️⃣ **Müşteriler Sekmesi**

Tüm müşterilerin bilgilerini yönetin.

**Yeni Müşteri Ekleme:**
1. "Yeni Müşteri" düğmesini tıklayın
2. Müşterinin adını yazın
3. Telefon numarasını girin
4. Email adresini girin
5. İçinde adres girin
6. "Kaydet" düğmesini tıklayın

**Tablo Sütunları:**
- **ID**: Müşterinin benzersiz numarası
- **Ad Soyad**: Müşterinin tam adı
- **Telefon**: İletişim telefon numarası
- **Email**: E-posta adresi
- **Adres**: Fiziksel adres

---

#### 3️⃣ **Teknisyenler Sekmesi**

Teknisyenleri ve uzmanlık alanlarını yönetin.

**Yeni Teknisyen Ekleme:**
1. "Yeni Teknisyen" düğmesini tıklayın
2. Teknisyenin adını yazın
3. Telefon numarasını girin
4. Uzmanlık alanını yazın (örn: "Bilgisayar Tamiri", "Yazıcı Bakımı")
5. "Kaydet" düğmesini tıklayın

**Tablo Sütunları:**
- **ID**: Teknisyenin benzersiz numarası
- **Ad Soyad**: Teknisyenin tam adı
- **Telefon**: İletişim telefon numarası
- **Uzmanlık**: Uzman olduğu alan(lar)

---

#### 4️⃣ **İstatistikler Sekmesi**

Işletmenizin genel performans göstergelerini görüntüleyin.

**Gösterilen Bilgiler:**
- **Toplam Servis Talepleri**: Sisteme kaydedilen tüm taleplerin sayısı
  - Tamamlanan: Tamamlanan taleplerin sayısı
  - Açık: Henüz çözülmemiş taleplerin sayısı
  - Acil: Acil öncelikli taleplerin sayısı
- **Sistem Bilgileri**:
  - Toplam Müşteri: Sisteme kayıtlı müşteri sayısı
  - Toplam Teknisyen: Sisteme kayıtlı teknisyen sayısı
- **Tamamlanma Oranı**: Yüzde cinsinden tamamlanan taleplerin oranı

---

## 🗄️ Veritabanı Yapısı

Program otomatik olarak `service_tracking.db` adında bir SQLite veritabanı oluşturur.

**Tablolar:**
- **customers**: Müşteri bilgileri
- **technicians**: Teknisyen bilgileri
- **service_requests**: Servis taleplerinin detayları
- **service_log**: Tamamlanan işlerin günlüğü

Veritabanı dosyası programla aynı dizinde saklanır.

## 🎨 Arayüz Özellikleri

- **Türkçe Arayüz**: Tamamen Türkçe menüler ve açıklamalar
- **Sekme Sistemi**: Dört ana sekmeyle organize edilmiş yapı
- **Tablo Görüntüleme**: Verileri hızlı ve kolay şekilde inceleyin
- **Dialog Pencereler**: Temiz ve basit veri giriş formları
- **Uyarı Mesajları**: Önemli işlemlerde onay ve feedback

## ⚡ Klavye Kısayolları

- **Yeni Öğe Ekleme**: Düğmeyi tıklayın veya ilgili sekmede çalışın
- **Verileri Yenileme**: "Yenile" düğmesini tıklayın
- **Tablo Seçimi**: Satırı tıklayarak seçin

## 🔒 Veri Güvenliği

- Tüm veriler yerel SQLite veritabanında saklanır
- Veri tabanı dosyası (`service_tracking.db`) hassas bilgiler içerir
- **Yedekleme önerisi**: Düzenli olarak veritabanı dosyasını yedekleyin

## 🐛 Sorun Giderme

### Uygulama başlamıyor
- Python 3.7+ yüklü olduğundan emin olun
- PyQt5 yüklü olduğundan emin olun: `pip install PyQt5`

### Veritabanı hatası
- `service_tracking.db` dosyasını silin (yeni veritabanı oluşturulacak)
- Veya dosyanın yazılabilir bir konumda olduğundan emin olun

### Türkçe karakterler gösterilmiyor
- Dosyanın UTF-8 ile kodlandığından emin olun
- Ortam değişkenlerini kontrol edin: `export LANG=tr_TR.UTF-8`

## 📝 Örnek İş Akışı

1. **Başlangıç**: Müşteri ve teknisyen bilgilerini ekleyin
2. **Talep Alma**: Müşteri telefon araması yapınca "Yeni Servis Talebi" ekleyin
3. **Atama**: Uygun teknisyeni seçin
4. **İzleme**: "Servis Talepleri" sekmesinden ilerlemesini izleyin
5. **Tamamlama**: İş bittiğinde "Tamamla" düğmesini tıklayın
6. **Raporlama**: İstatistikler sekmesinden başarı oranını görüntüleyin

## 🚀 İleri Özellikler (Gelecek Sürümler)

- Servis notları ve fotoğraf yükleme
- SMS/Email bildirimleri
- Gümrük ve para birimi desteği
- Teknisyen performans raporları
- Müşteri memnuniyet anketleri
- Yedekleme ve dışa aktarma özellikleri

## 📞 Destek

Sorularınız veya hata raporları için lütfen proje yöneticisine başvurun.

## 📄 Lisans

Bu program açık kaynak kodlu olup, özgürce kullanılabilir ve değiştirilebilir.

---

**Sürüm**: 1.0
**Son Güncelleme**: Mart 2026
**Geliştirici**: Claude AI
