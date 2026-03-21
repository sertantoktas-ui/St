# 🌐 Streamlit Web Uygulaması

## 🚀 Başlatma

### Yöntem 1: Direkt Çalıştır
```bash
pip install streamlit
streamlit run streamlit_app.py
```

Tarayıcı otomatik açılır: `http://localhost:8501`

### Yöntem 2: Python Komutu İle
```bash
python -m streamlit run streamlit_app.py
```

---

## 📱 Özellikler

### 💬 Sohbet Sekmesi
- Claude AI ile gerçek zamanlı sohbet
- Sohbet geçmişi otomatik kaydedilir
- Doğal dil konuşması

### 📝 Notlar Sekmesi
- Not ekle, gör, ara
- Tarih ve saat otomatik kaydedilir
- Not silme özelliği
- Veritabanında kalıcı depolama

### 📧 Email Sekmesi
- Direkt email gönderme
- Alıcı, konu, içerik seçenekleri
- Gmail/Outlook desteği

### 📄 PDF Sekmesi
- Rapor oluşturma
- Başlık özelleştirmesi
- Rapor türü seçimi (Özet, Detaylı, Analiz)
- PDF indir

---

## ⚙️ Ayarlar

### .env Dosyası Gerekli:
```
ANTHROPIC_API_KEY=your_key_here
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
```

### Chrome'da Çalıştır:
```bash
streamlit run streamlit_app.py --client.toolbarPosition=bottom
```

### Dark Mode:
```bash
streamlit run streamlit_app.py --theme.base="dark"
```

---

## 🌐 Buluta Deploy

### Streamlit Cloud (Ücretsiz)

1. GitHub'a Push Et
```bash
git push origin main
```

2. https://share.streamlit.io/ Git
3. "New App" → GitHub Repo Seç
4. Main file: `streamlit_app.py`

### Heroku'ya Deploy
```bash
pip install gunicorn
heroku create your-app-name
git push heroku main
```

### Railway.app'a Deploy (En Kolay)
1. https://railway.app Git
2. "New Project" → GitHub Connect
3. Otomatik detekt eder

---

## 📊 Performans İpuçları

- Ağır işlemler için `@st.cache_data` kullan
- `st.spinner()` ile yükleme göster
- Session state'i kullan veri için

---

## 🔒 Güvenlik

✅ API Key .env'de (exposed değil)
✅ Veritabanı SQLite (güvenli)
✅ Email şifresi .env'de

---

## 📚 Kaynaklar

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Cloud](https://share.streamlit.io)

---

**Enjoy! 🎉**
