#!/usr/bin/env python3
"""
Claude.ai → Obsidian tam entegrasyon.

İki mod:
  1. JSON parse  : claude_to_obsidian.py --json conversations.json --out ./vault
  2. Obsidian API: claude_to_obsidian.py --json conversations.json --obsidian http://localhost:27123 --token <token>
  3. Drive'a yükle: claude_to_obsidian.py --json conversations.json --drive

Adımlar (Claude.ai export):
  Claude.ai → Ayarlar → Privacy → Export Data → ZIP indir → conversations.json'ı çıkar
"""

import argparse
import json
import io
import zipfile
import os
import sys
import re
from pathlib import Path
from datetime import datetime


# ─── YARDIMCI ───────────────────────────────────────────────────────────────

def temizle_baslik(metin: str, maks: int = 60) -> str:
    metin = metin.strip() or "Isimsiz Sohbet"
    metin = re.sub(r'[\\/*?:"<>|]', "", metin)
    return metin[:maks]


def tarih_formatla(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso


# ─── MARKDOWN OLUŞTURUCU ─────────────────────────────────────────────────────

def sohbet_markdown(sohbet: dict) -> str:
    baslik = temizle_baslik(sohbet.get("name") or "Isimsiz Sohbet")
    olusturma = tarih_formatla(sohbet.get("created_at", ""))
    guncelleme = tarih_formatla(sohbet.get("updated_at", ""))
    model = sohbet.get("model", "")
    mesajlar = sohbet.get("chat_messages", [])

    satirlar = [
        f"# {baslik}\n",
        f"**Tarih:** {olusturma}  ",
        f"**Son güncelleme:** {guncelleme}  ",
        f"**Model:** {model}  ",
        f"**Mesaj sayısı:** {len(mesajlar)}",
        "\n---\n",
    ]

    for m in mesajlar:
        sender = m.get("sender", "")
        icerik = m.get("text") or ""
        zaman = tarih_formatla(m.get("created_at", ""))

        if sender == "human":
            satirlar.append(f"\n> **Kullanıcı** — _{zaman}_\n")
            satirlar.append(f">\n> {icerik.replace(chr(10), chr(10) + '> ')}\n")
        else:
            satirlar.append(f"\n**Claude** — _{zaman}_\n\n{icerik}\n")

        satirlar.append("\n---\n")

    return "\n".join(satirlar)


def ana_sayfa_markdown(sohbetler: list) -> str:
    satirlar = [
        "# Claude Sohbetleri — Obsidian\n",
        f"> Aktarım tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"Toplam **{len(sohbetler)}** sohbet.\n\n",
        "| Tarih | Başlık | Mesaj |\n",
        "|-------|--------|-------|\n",
    ]
    for s in sorted(sohbetler, key=lambda x: x.get("created_at", ""), reverse=True):
        baslik = temizle_baslik(s.get("name") or "Isimsiz Sohbet")
        tarih = tarih_formatla(s.get("created_at", ""))
        mesaj_sayisi = len(s.get("chat_messages", []))
        dosya = temizle_baslik(s.get("name") or s.get("uuid", "sohbet"))
        satirlar.append(f"| {tarih} | [[Claude Sohbetleri/{dosya}\\|{baslik}]] | {mesaj_sayisi} |\n")
    return "".join(satirlar)


# ─── YEREL KLASÖRE YAZ ───────────────────────────────────────────────────────

def yerel_yaz(sohbetler: list, cikti_klas: Path):
    klasor = cikti_klas / "Claude Sohbetleri"
    klasor.mkdir(parents=True, exist_ok=True)

    for s in sohbetler:
        baslik = temizle_baslik(s.get("name") or s.get("uuid", "sohbet"))
        icerik = sohbet_markdown(s)
        (klasor / f"{baslik}.md").write_text(icerik, encoding="utf-8")
        print(f"  ✅ {baslik}.md")

    (cikti_klas / "Claude Sohbetleri" / "_Indeks.md").write_text(
        ana_sayfa_markdown(sohbetler), encoding="utf-8"
    )
    print(f"\n📚 {len(sohbetler)} sohbet → {klasor}")


# ─── ZIP OLARAK PAKETLE ──────────────────────────────────────────────────────

def zip_paketle(sohbetler: list) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for s in sohbetler:
            baslik = temizle_baslik(s.get("name") or s.get("uuid", "sohbet"))
            zf.writestr(
                f"Claude Sohbetleri/{baslik}.md",
                sohbet_markdown(s).encode("utf-8"),
            )
        zf.writestr(
            "Claude Sohbetleri/_Indeks.md",
            ana_sayfa_markdown(sohbetler).encode("utf-8"),
        )
    buf.seek(0)
    return buf.read()


# ─── OBSİDİAN LOCAL REST API ─────────────────────────────────────────────────

def obsidian_api_gonder(sohbetler: list, base_url: str, token: str):
    """
    Obsidian Local REST API eklentisi gereklidir.
    Eklenti: https://github.com/coddingtonbear/obsidian-local-rest-api
    """
    import urllib.request
    import urllib.error

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/markdown",
    }

    basarili = 0
    hatali = 0

    for s in sohbetler:
        baslik = temizle_baslik(s.get("name") or s.get("uuid", "sohbet"))
        dosya_yolu = f"Claude Sohbetleri/{baslik}.md"
        icerik = sohbet_markdown(s).encode("utf-8")
        url = f"{base_url.rstrip('/')}/vault/{urllib.request.quote(dosya_yolu)}"

        req = urllib.request.Request(url, data=icerik, headers=headers, method="PUT")
        try:
            urllib.request.urlopen(req, timeout=10)
            basarili += 1
            print(f"  ✅ {baslik}")
        except urllib.error.HTTPError as e:
            hatali += 1
            print(f"  ❌ {baslik}: HTTP {e.code}")
        except Exception as e:
            hatali += 1
            print(f"  ❌ {baslik}: {e}")

    # İndeks sayfası
    indeks_url = f"{base_url.rstrip('/')}/vault/Claude%20Sohbetleri/_Indeks.md"
    req = urllib.request.Request(
        indeks_url,
        data=ana_sayfa_markdown(sohbetler).encode("utf-8"),
        headers=headers,
        method="PUT",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"  ✅ _Indeks.md")
    except Exception as e:
        print(f"  ❌ _Indeks: {e}")

    print(f"\n✨ {basarili} başarılı, {hatali} hatalı")


# ─── GOOGLE DRIVE ────────────────────────────────────────────────────────────

def drive_yukle(sohbetler: list):
    try:
        import google_drive as gd
    except ImportError:
        print("❌ google_drive.py bulunamadı.")
        sys.exit(1)

    zip_data = zip_paketle(sohbetler)
    dosya_adi = f"claude_sohbetler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    print("⬆️  Drive'a yükleniyor...")
    link = gd.upload_zip(zip_data, filename=dosya_adi)
    print(f"✅ Yüklendi: {link}")


# ─── ANA ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Claude.ai → Obsidian")
    parser.add_argument("--json", required=True, help="conversations.json dosyası")
    parser.add_argument("--out", default="./obsidian_claude", help="Çıktı klasörü (yerel mod)")
    parser.add_argument("--obsidian", help="Obsidian Local REST API URL (örn: http://localhost:27123)")
    parser.add_argument("--token", help="Obsidian API token")
    parser.add_argument("--drive", action="store_true", help="Google Drive'a yükle")
    args = parser.parse_args()

    json_yolu = Path(args.json)
    if not json_yolu.exists():
        print(f"❌ Dosya bulunamadı: {json_yolu}")
        sys.exit(1)

    print(f"\n📖 Okunuyor: {json_yolu}")
    with open(json_yolu, encoding="utf-8") as f:
        veri = json.load(f)

    # Hem liste hem tekil sohbet destekle
    if isinstance(veri, list):
        sohbetler = veri
    elif isinstance(veri, dict) and "conversations" in veri:
        sohbetler = veri["conversations"]
    else:
        sohbetler = [veri]

    print(f"💬 {len(sohbetler)} sohbet bulundu.\n")

    if args.obsidian:
        if not args.token:
            print("❌ Obsidian API için --token gerekli.")
            sys.exit(1)
        print("🔷 Obsidian Local REST API'ye gönderiliyor...")
        obsidian_api_gonder(sohbetler, args.obsidian, args.token)

    if args.drive:
        drive_yukle(sohbetler)

    if not args.obsidian and not args.drive:
        print(f"📁 Yerel klasöre yazılıyor: {args.out}")
        yerel_yaz(sohbetler, Path(args.out))


if __name__ == "__main__":
    main()
