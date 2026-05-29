# Deploy to Vercel in 2 Minutes

## Step 1: Go to Vercel
👉 **https://vercel.com/new**

## Step 2: Import from GitHub
1. Click **"Continue with GitHub"** (if not logged in, create free account first)
2. Search for your repo: **`sertantoktas-ui/St`**
3. Click **Import**

## Step 3: Configure Project
- **Project Name**: `axtea-cnc-hmi` (or any name)
- **Framework**: Select **"Other"** (it's static HTML/JS)
- **Root Directory**: Leave blank (default)
- Leave all other settings as default

## Step 4: Deploy
Click **"Deploy"** button → Wait 30 seconds

---

## ✅ Done!

You'll get a live URL like:
```
https://axtea-cnc-hmi.vercel.app
```

(or your custom domain)

---

## Access Your HMI

Open in browser:
```
https://axtea-cnc-hmi.vercel.app/hmi/
```

---

## OSAI Connection in Web

1. Click **⟳ Connect** button (top right)
2. Enter OSAI IP: `192.168.1.10` (or your machine IP)
3. Port: `5050` (default)
4. Check/uncheck **Simulation** mode
5. Click **Connect**

---

## Auto-Updates

Every time you push to GitHub:
```bash
git push origin claude/nifty-ride-Qmdgb
```

Vercel **automatically rebuilds & redeploys** within 30 seconds.

No manual steps needed after initial setup! 🚀

---

## Need Custom Domain?

Vercel Settings → **Domains** → Add your own domain (free for `.vercel.app`)

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Page blank | Clear browser cache (Ctrl+Shift+Del) |
| OSAI not connecting | Check IP/port, firewall allows outbound 5050 |
| Simulation stuck | Open DevTools (F12) → Console → check errors |

---

Questions? Check `/DEPLOYMENT.md` for all deploy options.
