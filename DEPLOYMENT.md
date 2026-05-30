# AXTEA CNC HMI – Deployment Guide

## Web (Vercel)

### 1. Connect GitHub to Vercel
- Go to https://vercel.com/new
- Import this GitHub repo (`sertantoktas-ui/St`)
- Vercel auto-detects `vercel.json`
- Click **Deploy**

✅ **Live URL**: `https://<your-project>.vercel.app`

---

## Web (Netlify)

### 1. Connect GitHub to Netlify
- Go to https://app.netlify.com/sites
- Click **Add new site** → **Import an existing project**
- Select GitHub, find `sertantoktas-ui/St`
- **Deploy** (auto-detects build)

✅ **Live URL**: `https://<your-site>.netlify.app`

---

## Web (Railway) – Full Stack

### 1. Push to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

✅ **Live URL**: `https://your-project.up.railway.app`

---

## Local Web Server

### Python 3
```bash
cd St/
python -m http.server 8000
# → http://localhost:8000/hmi/index.html
```

### Node.js
```bash
cd St/hmi/
npx http-server -p 8000
# → http://localhost:8000
```

### Streamlit (interactive simulation)
```bash
streamlit run hmi_app.py --server.port=8501
# → http://localhost:8501
```

---

## Desktop App

### Windows 11
1. Download: `AXTEA-CNC-HMI-Setup-1.0.0.exe`
2. Run installer → Next → Install
3. Desktop shortcut created
4. Connect to OSAI (192.168.1.10:5050)

### macOS
1. Download: `AXTEA-CNC-HMI-1.0.0-mac.dmg`
2. Open `.dmg`
3. Drag **AXTEA CNC HMI** to **Applications**
4. Spotlight: type "AXTEA" → Open
5. (First launch: Right-click → Open)

---

## OSAI Connection

| Mode | IP | Port |
|---|---|---|
| Simulation | (any) | (any) |
| Real (C07/C11) | `192.168.1.10` | `5050` |
| Custom | (your unit IP) | (your unit port) |

Uncheck **Simulation** to connect to live OSAI unit.
