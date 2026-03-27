# 🚀 Railway'e Dağıtım Rehberi / Railway Deployment Guide

## Dünya Saatleri (World Clock) + Servis Yönetimi Sistemi

Railway: Modern, hızlı, ve Heroku'dan daha ucuz bir alternatif.

---

## ⚡ Railway Neden Seçmelisiniz?

| Özellik | Railway | Heroku |
|---------|---------|--------|
| **Başlangıç Maliyeti** | $5/ay | $5/ay |
| **Deploy Hızı** | 30 saniye | 2-3 dakika |
| **GitHub Integration** | ✅ Native | ✅ Native |
| **Docker Support** | ✅ Full | ✅ Limited |
| **Veritabanı Ekleme** | 1 tıkla | İnsan müdahalesi |
| **Kullanıcı Arayüzü** | Modern | Eski |

---

## 📋 Ön Gereksinimler / Prerequisites

1. **Railway Hesabı** - https://railway.app (GitHub ile kaydolun)
2. **GitHub Deposu** - Bu kod
3. **Git** - Komut satırında kullanım
4. **Railway CLI** (opsiyonel)

---

## 🔧 Kurulum / Setup

### 1. GitHub'a Push Et / Push to GitHub

```bash
# Repository oluştur (https://github.com/new)
git remote add origin https://github.com/your-username/St.git
git branch -M main
git push -u origin main
```

### 2. Railway'e Giriş Yap / Login to Railway

1. https://railway.app'e git
2. "Create New Project" tıkla
3. "Deploy from GitHub" seç
4. GitHub repo'nunu seç (St)
5. "Deploy Now" tıkla

**VEYA CLI ile / Or with CLI:**

```bash
# Railway CLI'ı kur / Install CLI
npm install -g @railway/cli

# Giriş yap / Login
railway login

# Project oluştur / Create project
railway init
```

---

## 📦 Otomatik Kurulum / Automatic Setup

### 3. Veritabanı Ekleme / Add Database

Railway Dashboard'da:

1. **"+ New"** tıkla
2. **"Database"** seç
3. **"PostgreSQL"** seç
4. **"Create"** tıkla

Railway otomatik olarak `DATABASE_URL` ortam değişkenini ayarlar!

### 4. Redis Ekleme / Add Redis

1. **"+ New"** tıkla
2. **"Database"** seç
3. **"Redis"** seç
4. **"Create"** tıkla

Railway otomatik olarak `REDIS_URL` ortam değişkenini ayarlar!

---

## ⚙️ Environment Variables / Ortam Değişkenleri

### 5. Değişkenleri Ayarla / Set Variables

Railway Dashboard'da, **Variables** sekmesine git:

```bash
# JWT Secret (güvenli string)
JWT_SECRET_KEY=your-super-secure-random-string

# Flask
FLASK_ENV=production
DEBUG=False

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourapp.com

# World Clock
REPORTS_TIMEZONE=Europe/Istanbul
REPORT_EMAIL_HOUR=09
REPORT_EMAIL_MINUTE=00
```

---

## 🚀 Deploy Başlat / Start Deployment

### 6. Docker ile Deploy / Deploy with Docker

Railway Docker'ı otomatik olarak algılar!

**Procfile (açılı opsiyonel) / Procfile (optional):**
```bash
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 60 'app:create_app()'
worker: celery -A celery_app worker --loglevel=info
beat: celery -A celery_app beat --loglevel=info
```

### 7. GitHub Actions ile Otomatik Deploy / Auto Deploy with GitHub

1. GitHub repo'nda **Actions** tıkla
2. Railway integration otomatik çalışır
3. Her `git push`'da otomatik deploy!

### 8. Port Yapılandırması / Port Configuration

Railway otomatik olarak $PORT environment variable'ını ayarlar.

Bizim Dockerfile zaten bunu kullanıyor:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", ...]
```

**Eğer 5000 port kullanmak istemezsen / If you want custom port:**
```bash
# Railway'de PORT variable'ını ayarla
PORT=3000
```

---

## ✅ Doğrulama / Verification

### 9. Deploy Durumunu Kontrol Et / Check Deployment Status

```bash
# Railway CLI ile / Using Railway CLI
railway logs

# Veya / Or web dashboard'dan
Deployments > Latest > Logs
```

### 10. Health Check / Sistem Kontrolü

```bash
# Uygulamayı test et
curl https://your-railway-app.up.railway.app/health

# World Clock'u aç
# https://your-railway-app.up.railway.app/api/clock
```

---

## 🛠️ Gelişmiş Konfigürasyon / Advanced Configuration

### Veritabanı Migrate Etme / Migrate Database

```bash
# Railway CLI ile / Using Railway CLI
railway run flask db upgrade

# Veya / Or web dashboard'da
Services > API > Shell
$ flask db upgrade
```

### Worker ve Beat Servisi Ekleme / Add Worker & Beat Services

**railway.json oluştur / Create railway.json:**
```json
{
  "services": [
    {
      "name": "api",
      "source": ".",
      "cmd": "gunicorn --bind 0.0.0.0:$PORT --workers 4 'app:create_app()'"
    },
    {
      "name": "worker",
      "source": ".",
      "cmd": "celery -A celery_app worker --loglevel=info",
      "deploy": false
    },
    {
      "name": "beat",
      "source": ".",
      "cmd": "celery -A celery_app beat --loglevel=info",
      "deploy": false
    }
  ]
}
```

### Custom Domain Ekle / Add Custom Domain

1. Railway Dashboard > Settings
2. **"Custom Domain"** seç
3. Domain'i gir: `your-domain.com`
4. DNS kayıtlarını güncelle

---

## 📊 Monitoring / İzleme

### Logs'ları İzle / Monitor Logs

```bash
# Railway CLI
railway logs --tail

# Gerçek zamanlı
railway logs -f
```

### Metrics Görüntüle / View Metrics

Railway Dashboard:
1. Services > API
2. **"Metrics"** sekmesi
3. CPU, Memory, Network kullanımı

### Sürekli Build & Deploy / Auto Build & Deploy

Railway otomatik olarak:
1. GitHub'dan yeni push'u algılar
2. Build eder (2-3 dakika)
3. Deploy eder (otomatik zero-downtime)

---

## 💰 Maliyet / Pricing

Railway **"Pay as you go" sistem** kullanır (Heroku'dan daha ucuz!).

| Hizmet | Süre | Aylık Maliyet |
|--------|------|--------------|
| Dyno (Web) | 100 saat | $5 |
| PostgreSQL | 100 GB | $20 |
| Redis | 1 GB | $1 |
| **Toplam** | | **$26/ay** |

**1000 ücretsiz dyno saati vardır!**

---

## 🔐 Güvenlik / Security

### HTTPS / SSL

✅ Otomatik olarak etkin (Let's Encrypt)

### Secrets Management / Gizli Yönetimi

```bash
# Environment variables secure olarak saklanır
railway config set JWT_SECRET_KEY "your-key"

# Encrypt edilir
railway config get JWT_SECRET_KEY
# *** (masked)
```

---

## 🐛 Sorun Giderme / Troubleshooting

### Problem: Build başarısız

```bash
# Logs'ı kontrol et
railway logs

# Dockerfile syntax hatası?
docker build .

# requirements.txt eksik?
cat backend_requirements.txt
```

### Problem: Uygulama 503 hatası veriyor

```bash
# Veritabanı migrate edildi mi?
railway run flask db upgrade

# Env variables ayarlı mı?
railway config list

# Logs'ları kontrol et
railway logs -d api
```

### Problem: Worker çalışmıyor

```bash
# Redis bağlı mı?
railway config get REDIS_URL

# Celery ayarı kontrol et
railway logs -d worker
```

### Problem: Email gönderme başarısız

```bash
# MAIL_ variables'ları kontrol et
railway config list | grep MAIL

# Gmail app password kullandın mı?
# (normal şifre değil, app-specific password)
```

---

## 🎯 Production Checklist

- [ ] JWT_SECRET_KEY güvenli ve unique mi?
- [ ] MAIL_PASSWORD doğru mu?
- [ ] DEBUG=False ayarlandı mı?
- [ ] FLASK_ENV=production mi?
- [ ] PostgreSQL backup ayarlandı mı?
- [ ] Custom domain ayarlandı mı?
- [ ] SSL sertifikası otomatik mi?
- [ ] Monitoring ayarlandı mı?

---

## 📚 Kaynaklar / Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway CLI Commands](https://docs.railway.app/reference/cli-api)
- [Deployment Guides](https://docs.railway.app/guides)
- [Pricing](https://railway.app/pricing)

---

## 🎉 Başarı!

Uygulamanız Railway'de yayında:

```
🌐 Web: https://your-railway-app.up.railway.app
🕐 Clock: https://your-railway-app.up.railway.app/api/clock
💚 Health: https://your-railway-app.up.railway.app/health
📊 Dashboard: https://railway.app > your-project
```

---

**Last Updated:** March 2026
**Version:** 1.0.0
**Recommendation:** Railway for modern, fast deployment! ⚡
