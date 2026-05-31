#!/usr/bin/env python3
"""
Obsidian Export - Tüm verileri Obsidian vault'una markdown olarak aktarır.
Kullanım: python export_to_obsidian.py --vault /path/to/vault
          python export_to_obsidian.py  (varsayılan: ./obsidian_export/)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from database import AssistantDatabase

PROJE_DOSYALARI = [
    "personal_assistant.py",
    "advanced_assistant.py",
    "full_featured_assistant.py",
    "streamlit_app.py",
    "database.py",
    "email_service.py",
    "pdf_generator.py",
    "requirements.txt",
    "README.md",
    "SETUP.md",
    "DEPLOY.md",
    "STREAMLIT_KURULUM.md",
]

def yaz(path: Path, icerik: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(icerik, encoding="utf-8")
    print(f"  ✅ {path}")


def export_chat_gecmisi(db: AssistantDatabase, vault: Path):
    klasor = vault / "Chat Geçmişi"
    oturumlar = db.get_chat_sessions()

    if not oturumlar:
        print("  ℹ️  Kayıtlı chat geçmişi bulunamadı.")
        return

    # Ana dizin notu
    indeks_satirlar = [
        "# Chat Geçmişi\n",
        f"> Dışa aktarma tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        f"\nToplam **{len(oturumlar)}** oturum.\n",
    ]

    for oturum in oturumlar:
        sid = oturum["session_id"]
        baslangic = oturum["started_at"]
        mesajlar = db.get_chat_history(session_id=sid)

        satirlar = [
            f"# Sohbet — {baslangic}\n",
            f"**Oturum ID:** `{sid}`  \n",
            f"**Mesaj sayısı:** {len(mesajlar)}\n\n---\n",
        ]

        for m in mesajlar:
            zaman = m["created_at"]
            if m["role"] == "user":
                satirlar.append(f"\n**Kullanıcı** _{zaman}_\n\n{m['content']}\n")
            else:
                satirlar.append(f"\n**Asistan** _{zaman}_\n\n{m['content']}\n")
            satirlar.append("\n---\n")

        dosya_adi = f"{sid}.md"
        yaz(klasor / dosya_adi, "\n".join(satirlar))
        indeks_satirlar.append(f"- [[Chat Geçmişi/{sid}|{baslangic}]] ({len(mesajlar)} mesaj)\n")

    yaz(klasor / "_Indeks.md", "".join(indeks_satirlar))


def export_notlar(db: AssistantDatabase, vault: Path):
    klasor = vault / "Notlar"
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY created_at DESC")
        notlar = cursor.fetchall()
        conn.close()
    except Exception:
        print("  ℹ️  'notes' tablosu bulunamadı, atlanıyor.")
        return

    if not notlar:
        print("  ℹ️  Kayıtlı not bulunamadı.")
        return

    indeks = ["# Notlar\n\n"]
    for n in notlar:
        nid, icerik, tarih = n
        baslik = icerik[:60].replace("\n", " ").strip()
        dosya_adi = f"Not_{nid:04d}.md"
        yaz(klasor / dosya_adi, f"# Not #{nid}\n\n**Tarih:** {tarih}\n\n---\n\n{icerik}\n")
        indeks.append(f"- [[Notlar/{dosya_adi.replace('.md','')}|{baslik}...]]\n")

    yaz(klasor / "_Indeks.md", "".join(indeks))


def export_gorevler(db: AssistantDatabase, vault: Path):
    bekleyen = db.get_tasks("pending")
    tamamlanan = db.get_tasks("completed")
    tum = bekleyen + tamamlanan

    if not tum:
        print("  ℹ️  Kayıtlı görev bulunamadı.")
        return

    satirlar = [
        "# Görevler\n\n",
        f"> Dışa aktarma: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n",
        "## Bekleyen\n\n",
    ]
    for g in bekleyen:
        oncelik = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(g["priority"], "⚪")
        satirlar.append(f"- [ ] {oncelik} **{g['title']}** — {g['created_at']}\n")
        if g["description"]:
            satirlar.append(f"  > {g['description']}\n")

    satirlar.append("\n## Tamamlanan\n\n")
    for g in tamamlanan:
        satirlar.append(f"- [x] **{g['title']}** — {g['created_at']}\n")

    yaz(vault / "Gorevler.md", "".join(satirlar))


def export_emailler(db: AssistantDatabase, vault: Path):
    klasor = vault / "Emailler"
    emailler = db.get_emails()

    if not emailler:
        print("  ℹ️  Kayıtlı email bulunamadı.")
        return

    indeks = ["# Emailler\n\n"]
    for e in emailler:
        durum = "✅ Gönderildi" if e["sent"] else "📤 Taslak"
        dosya_adi = f"Email_{e['id']:04d}.md"
        icerik = (
            f"# {e['subject']}\n\n"
            f"**Alıcı:** {e['recipient']}  \n"
            f"**Tarih:** {e['created_at']}  \n"
            f"**Durum:** {durum}  \n"
            f"**Ton:** {e['tone']}\n\n---\n\n{e['body']}\n"
        )
        yaz(klasor / dosya_adi, icerik)
        indeks.append(f"- [[Emailler/{dosya_adi.replace('.md','')}|{e['subject']}]] — {durum}\n")

    yaz(klasor / "_Indeks.md", "".join(indeks))


def export_raporlar(db: AssistantDatabase, vault: Path):
    klasor = vault / "Raporlar"
    raporlar = db.get_reports()

    if not raporlar:
        print("  ℹ️  Kayıtlı rapor bulunamadı.")
        return

    indeks = ["# Raporlar\n\n"]
    for r in raporlar:
        # Tam içeriği al
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM reports WHERE id = ?", (r["id"],))
        row = cursor.fetchone()
        conn.close()
        icerik_metni = row[0] if row else ""

        dosya_adi = f"Rapor_{r['id']:04d}.md"
        icerik = (
            f"# {r['title']}\n\n"
            f"**Tarih:** {r['created_at']}  \n"
            f"**Format:** {r['format']}\n\n---\n\n{icerik_metni}\n"
        )
        yaz(klasor / dosya_adi, icerik)
        indeks.append(f"- [[Raporlar/{dosya_adi.replace('.md','')}|{r['title']}]]\n")

    yaz(klasor / "_Indeks.md", "".join(indeks))


def export_proje_dosyalari(repo_koku: Path, vault: Path):
    klasor = vault / "Proje Dosyaları"
    for dosya_adi in PROJE_DOSYALARI:
        kaynak = repo_koku / dosya_adi
        if not kaynak.exists():
            continue
        ham = kaynak.read_text(encoding="utf-8", errors="replace")
        uzanti = kaynak.suffix.lstrip(".")
        dil = {"py": "python", "md": "", "txt": "text", "toml": "toml"}.get(uzanti, uzanti)
        if dil:
            md_icerik = f"# {dosya_adi}\n\n```{dil}\n{ham}\n```\n"
        else:
            md_icerik = f"# {dosya_adi}\n\n{ham}\n"
        hedef = klasor / (dosya_adi.replace("/", "_") + ".md")
        yaz(hedef, md_icerik)


def ana_sayfa(vault: Path, db: AssistantDatabase):
    stats = db.get_statistics()
    oturumlar = db.get_chat_sessions()
    icerik = f"""# Kişisel Asistan — Obsidian Vault

> Dışa aktarma tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Özet

| Alan | Sayı |
|------|------|
| Chat Oturumları | {len(oturumlar)} |
| Bekleyen Görevler | {stats['pending_tasks']} |
| Tamamlanan Görevler | {stats['completed_tasks']} |
| Emailler (taslak) | {stats['unsent_emails']} |
| Emailler (gönderildi) | {stats['sent_emails']} |
| Raporlar | {stats['total_reports']} |

## Bölümler

- [[Chat Geçmişi/_Indeks|Chat Geçmişi]]
- [[Notlar/_Indeks|Notlar]]
- [[Gorevler|Görevler]]
- [[Emailler/_Indeks|Emailler]]
- [[Raporlar/_Indeks|Raporlar]]
- [[Proje Dosyaları|Proje Dosyaları]]
"""
    yaz(vault / "Ana Sayfa.md", icerik)


def main():
    parser = argparse.ArgumentParser(description="Obsidian Export")
    parser.add_argument("--vault", default="./obsidian_export", help="Vault klasörü")
    parser.add_argument("--db", default="assistant.db", help="Veritabanı dosyası")
    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    repo_koku = Path(__file__).parent

    print(f"\n📚 Obsidian Export Başlıyor...")
    print(f"   Vault: {vault}\n")

    db = AssistantDatabase(args.db)

    print("💬 Chat geçmişi dışa aktarılıyor...")
    export_chat_gecmisi(db, vault)

    print("📝 Notlar dışa aktarılıyor...")
    export_notlar(db, vault)

    print("✅ Görevler dışa aktarılıyor...")
    export_gorevler(db, vault)

    print("📧 Emailler dışa aktarılıyor...")
    export_emailler(db, vault)

    print("📄 Raporlar dışa aktarılıyor...")
    export_raporlar(db, vault)

    print("🗂️  Proje dosyaları dışa aktarılıyor...")
    export_proje_dosyalari(repo_koku, vault)

    print("🏠 Ana sayfa oluşturuluyor...")
    ana_sayfa(vault, db)

    print(f"\n✨ Tamamlandı! Vault klasörü: {vault}")
    print("   Obsidian'da 'Open folder as vault' ile bu klasörü açın.\n")


if __name__ == "__main__":
    main()
