# Sorun Giderme

## ❌ "Sayfa boş / yüklenmedi"

```bash
# 1. Cache temizle
# Chrome/Edge: Ctrl+Shift+Del → "All time" → Clear
# Firefox: Ctrl+Shift+Del → seç → Clear

# 2. Hard refresh
Ctrl+Shift+R  (Linux/Windows)
Cmd+Shift+R   (macOS)

# 3. Developer Tools'u aç
F12 → Console tab → hata oku
```

---

## ❌ "OSAI connection failed"

**Simulate mode'da test et:**
1. Connect button → ⟳
2. **Simulation** kutusunu CHECK et
3. Connect

Eğer simulation çalışsa → problem OSAI TCP değil

**Gerçek OSAI için:**
- IP doğru mu? (`192.168.1.10`)
- Port doğru mu? (`5050`)
- Network kablo/WiFi bağlı mı?
- Firewall izin veriyor mu?

```bash
# Network test
ping 192.168.1.10
telnet 192.168.1.10 5050  # telnet varsa
nc -zv 192.168.1.10 5050  # netcat varsa
```

---

## ❌ "Streamlit iframe boş/kaymış"

**Ctrl+F5** (hard refresh) yapın

Eğer hala sorunlu:
```bash
# Streamlit'i kapat
pkill -f streamlit

# Yeniden başlat
streamlit run /home/user/St/hmi_app.py --server.port=8501
```

---

## ❌ "Hiç açılmıyor"

```bash
# Port kullanımdaki mi?
lsof -i :8080
lsof -i :8501

# Eğer başka process varsa
pkill -f "http.server"
pkill -f "streamlit"

# Yeniden başlat
python3 -m http.server 8080 &
streamlit run /home/user/St/hmi_app.py --server.port=8501 &
```

---

## ❌ "Vercel/GitHub Pages açılmıyor"

**GitHub Pages:**
1. Repo Settings → Pages
2. Source → "GitHub Actions" seç
3. Workflow runs'a git → düğmeye tıkla
4. 1-2 dakika sonra: `https://sertantoktas-ui.github.io/St/hmi/`

**Vercel:**
1. https://vercel.com/new
2. GitHub'dan import
3. Deploy tıkla
4. 30 saniye bekle
5. URL'yi kopyala

---

## ✅ "Tüm portlar açık ama hiçbir şey çalışmıyor"

```bash
# Logs kontrol et
tail -20 /tmp/st.log    # Streamlit
tail -20 /tmp/http.log  # HTTP server

# Ports kontrol
netstat -tlnp | grep 8080
netstat -tlnp | grep 8501

# Firewall kontrol
sudo ufw status
# Eğer active ise ports'u allow et
sudo ufw allow 8080
sudo ufw allow 8501
```

---

## 📞 Hala çalışmıyor?

1. **Browser Console (F12)** → hangi hata?
2. **Network tab** → requests successful mi?
3. **Python logs** → `tail /tmp/st.log` ne diyor?

Bana hata mesajını kopyala-yapıştır!
