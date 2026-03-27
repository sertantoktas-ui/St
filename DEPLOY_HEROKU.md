# 🚀 Heroku'ya Dağıtım Rehberi / Heroku Deployment Guide

## Dünya Saatleri (World Clock) + Servis Yönetimi Sistemi

Adım adım Heroku'ya dağıtım rehberi.

---

## 📋 Ön Gereksinimler / Prerequisites

1. **Heroku Hesabı** - https://www.heroku.com
2. **Heroku CLI** - https://devcenter.heroku.com/articles/heroku-cli
3. **Git** - Kurulu olmalı
4. **GitHub** - Kod deposu (opsiyonel ama önerilen)

---

## 🔧 Kurulum Adımları / Installation Steps

### 1. Heroku CLI'ı Kur / Install Heroku CLI

**macOS:**
```bash
brew tap heroku/brew && brew install heroku
```

**Windows:**
```bash
# Download from https://cli-assets.heroku.com/heroku-x64.exe
# Veya chocolatey ile / Or with chocolatey:
choco install heroku-cli
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Heroku'ya Giriş Yap / Login to Heroku

```bash
heroku login
```

İnternet tarayıcınızda açılacak. E-postanız ve şifrenizi girin.

---

## 📦 Hazırlık / Preparation

### 3. Procfile Oluştur / Create Procfile

```bash
cat > Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 60 'app:create_app()'
worker: celery -A celery_app worker --loglevel=info
beat: celery -A celery_app beat --loglevel=info
EOF
```

### 4. runtime.txt Oluştur / Create runtime.txt

```bash
echo "python-3.11.7" > runtime.txt
```

### 5. .gitignore Kontrol Et / Check .gitignore

```bash
cat > .gitignore << 'EOF'
*.pyc
__pycache__/
.env
.venv/
venv/
*.egg-info/
dist/
build/
.DS_Store
.vscode/
.idea/
*.log
EOF
```

---

## 🚀 Heroku App Oluştur / Create Heroku App

### 6. Yeni App Oluştur / Create New App

```bash
# App adı örneği: my-service-app-123
heroku create my-service-app-unique-name
```

**Not:** App adı benzersiz olmalı ve sadece küçük harf + sayı + tire içermeli.

Eğer adı değiştirmek istersen:
```bash
heroku apps:rename new-name
```

### 7. Git Remote Kontrol Et / Verify Git Remote

```bash
git remote -v
```

`heroku` remote'unun listelendiğini kontrol et.

---

## 🗄️ Veritabanı Yapılandırması / Database Configuration

### 8. PostgreSQL Ekle / Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

**Not:** `hobby-dev` ücretsizdir (sınırlamalar var). Üretim için `standard` veya üstünü kullan.

Veritabanı URL'i otomatik olarak `DATABASE_URL` environment variable'ına atanır.

### 9. Redis Ekle / Add Redis

```bash
heroku addons:create heroku-redis:premium-0
```

**Not:** Ücretlidir. Alternatif olarak Redis Cloud'u kullan:
```bash
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-redis.git
```

---

## ⚙️ Environment Variables Ayarla / Configure Environment Variables

### 10. Kritik Değişkenleri Ayarla / Set Critical Variables

```bash
# JWT Secret Key (güvenli bir string üret / generate secure string)
heroku config:set JWT_SECRET_KEY="your-super-secure-random-string-here"

# Email Configuration
heroku config:set MAIL_SERVER="smtp.gmail.com"
heroku config:set MAIL_PORT="587"
heroku config:set MAIL_USERNAME="your-email@gmail.com"
heroku config:set MAIL_PASSWORD="your-app-password"
heroku config:set MAIL_DEFAULT_SENDER="noreply@yourapp.com"

# Flask Environment
heroku config:set FLASK_ENV="production"
heroku config:set DEBUG="False"

# World Clock Settings
heroku config:set REPORTS_TIMEZONE="Europe/Istanbul"
heroku config:set REPORT_EMAIL_HOUR="09"
heroku config:set REPORT_EMAIL_MINUTE="00"
```

### 11. Tüm Variables'ı Kontrol Et / Check All Variables

```bash
heroku config
```

---

## 📝 Buildpack'ler / Buildpacks

### 12. Python Buildpack Ekle / Add Python Buildpack

```bash
heroku buildpacks:add heroku/python
```

---

## 📤 Dağıt / Deploy

### 13. Git'e Commit Et / Commit to Git

```bash
git add .
git commit -m "feat: Prepare for Heroku deployment with Docker and World Clock"
```

### 14. Heroku'ya Push Et / Push to Heroku

```bash
git push heroku main
```

**Veya farklı branch kullanıyorsan / If using different branch:**
```bash
git push heroku your-branch:main
```

**Veya GitHub ile / If using GitHub:**
1. GitHub'a push et / Push to GitHub
2. Heroku Dashboard > Deploy > GitHub
3. Connect to GitHub ve otomatik deploy'ı aktif et

### 15. Veritabanını Migrate Et / Migrate Database

```bash
heroku run flask db upgrade
```

### 16. Uygulamayı Kontrol Et / Check Application

```bash
# Logs'ı izle / Watch logs
heroku logs --tail

# Health check
curl https://your-app-name.herokuapp.com/health

# World Clock'u aç / Open World Clock
# https://your-app-name.herokuapp.com/api/clock
```

---

## 🎯 İlk Kullanım / First Use

### 17. Dyno Türlerini Ayarla / Configure Dyno Types

```bash
# Web dyno (free tier)
heroku ps:scale web=1

# Worker dyno (optional, ücretli)
heroku ps:scale worker=1

# Beat scheduler (optional, ücretli)
heroku ps:scale beat=1
```

**Not:** Free tier sadece 550 saatlik dyno süresi sağlar. Üretim için upgraded tier kullan.

---

## 🔍 Sorun Giderme / Troubleshooting

### Problem: "slug too large" hatası

```bash
# Gereksiz dosyaları .slugignore'a ekle
echo "node_modules/" >> .slugignore
echo ".git/" >> .slugignore
git push heroku main
```

### Problem: Veritabanı bağlantısı başarısız

```bash
# DATABASE_URL'yi kontrol et
heroku config | grep DATABASE_URL

# Veritabanı reset et
heroku pg:reset DATABASE
heroku run flask db upgrade
```

### Problem: Worker/Beat başlamıyor

```bash
# Ücretli dyno olduğundan emin ol
heroku ps

# Yeniden başlat
heroku restart
```

### Problem: Email gönderme başarısız

```bash
# MAIL_ variables'ları kontrol et
heroku config | grep MAIL

# Log'ları kontrol et
heroku logs --tail | grep "mail\|email"
```

### Problem: Saat dilimi hataları

```bash
# REPORTS_TIMEZONE'yi kontrol et
heroku config | grep TIMEZONE

# Ayarla
heroku config:set REPORTS_TIMEZONE="Europe/Istanbul"
```

---

## 📊 Monitoring & Maintenance

### Logs'ları İzle / Monitor Logs

```bash
# Son 100 satır
heroku logs -n 100

# Gerçek zamanlı logs
heroku logs --tail

# Sadece API logs
heroku logs --tail -d api

# Sadece Worker logs
heroku logs --tail -d worker
```

### Metrics Görüntüle / View Metrics

```bash
# Dyno kullanımı
heroku ps

# CPU/Memory kullanımı
heroku metrics
```

### Yedek Oluştur / Create Backups

```bash
# Otomatik yedekleme (paid plans)
heroku pg:backups:schedule DATABASE_URL --at '02:00 UTC'

# Manuel yedek
heroku pg:backups:capture
```

---

## 🔐 Güvenlik Kontrol Listesi / Security Checklist

- [ ] JWT_SECRET_KEY güvenli mi?
- [ ] MAIL_PASSWORD doğru mu?
- [ ] DEBUG mode kapalı mı?
- [ ] HTTPS kullanılıyor mu?
- [ ] Database credentials güvenli mi?
- [ ] Redis şifre ayarlandı mı?
- [ ] CORS ayarları doğru mu?

---

## 💰 Maliyet Tahmini / Cost Estimation

| Hizmet | Tier | Aylık Maliyet |
|--------|------|--------------|
| Dyno (Web) | Eco | $5 |
| PostgreSQL | Mini | $9 |
| Redis | Mini | $15 |
| **Toplam** | | **$29/ay** |

---

## 🎉 Başarı!

Uygulamanız şu adreste yayında:
```
https://your-app-name.herokuapp.com
World Clock: https://your-app-name.herokuapp.com/api/clock
Health: https://your-app-name.herokuapp.com/health
```

---

## 📚 Kaynaklar / Resources

- [Heroku Devcenter](https://devcenter.heroku.com)
- [Heroku CLI Commands](https://devcenter.heroku.com/articles/heroku-cli-commands)
- [Flask on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python)
- [PostgreSQL on Heroku](https://devcenter.heroku.com/articles/heroku-postgresql)

---

**Last Updated:** March 2026
**Version:** 1.0.0
