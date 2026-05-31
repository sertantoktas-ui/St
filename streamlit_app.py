import streamlit as st
import os
import io
import zipfile
import tempfile
from datetime import datetime
from full_featured_assistant import PersonalAssistant
from database import Database

PROJE_DOSYALARI = [
    "personal_assistant.py", "advanced_assistant.py", "full_featured_assistant.py",
    "streamlit_app.py", "database.py", "email_service.py", "pdf_generator.py",
    "requirements.txt", "README.md", "SETUP.md", "DEPLOY.md", "STREAMLIT_KURULUM.md",
]


def _md_dosya(zip_buf: zipfile.ZipFile, yol: str, icerik: str):
    zip_buf.writestr(yol, icerik.encode("utf-8"))


def _obsidian_zip(db) -> bytes:
    """Tüm verileri tek zip dosyası olarak döner."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # Chat geçmişi
        oturumlar = db.get_chat_sessions()
        indeks = ["# Chat Geçmişi\n\n"]
        for o in oturumlar:
            sid = o["session_id"]
            mesajlar = db.get_chat_history(session_id=sid)
            satirlar = [f"# Sohbet — {o['started_at']}\n\n**Mesaj:** {len(mesajlar)}\n\n---\n"]
            for m in mesajlar:
                etiket = "**Kullanıcı**" if m["role"] == "user" else "**Asistan**"
                satirlar.append(f"\n{etiket} _{m['created_at']}_\n\n{m['content']}\n\n---\n")
            _md_dosya(zf, f"Chat Geçmişi/{sid}.md", "\n".join(satirlar))
            indeks.append(f"- [[{sid}|{o['started_at']}]] ({len(mesajlar)} mesaj)\n")
        _md_dosya(zf, "Chat Geçmişi/_Indeks.md", "".join(indeks))

        # Görevler
        bekleyen = db.get_tasks("pending")
        tamamlanan = db.get_tasks("completed")
        satirlar = ["# Görevler\n\n## Bekleyen\n\n"]
        for g in bekleyen:
            p = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(g["priority"], "⚪")
            satirlar.append(f"- [ ] {p} **{g['title']}** — {g['created_at']}\n")
        satirlar.append("\n## Tamamlanan\n\n")
        for g in tamamlanan:
            satirlar.append(f"- [x] **{g['title']}** — {g['created_at']}\n")
        _md_dosya(zf, "Gorevler.md", "".join(satirlar))

        # Emailler
        emailler = db.get_emails()
        indeks_e = ["# Emailler\n\n"]
        for e in emailler:
            durum = "✅ Gönderildi" if e["sent"] else "📤 Taslak"
            icerik = f"# {e['subject']}\n\n**Alıcı:** {e['recipient']}  \n**Tarih:** {e['created_at']}  \n**Durum:** {durum}\n\n---\n\n{e['body']}\n"
            _md_dosya(zf, f"Emailler/Email_{e['id']:04d}.md", icerik)
            indeks_e.append(f"- [[Email_{e['id']:04d}|{e['subject']}]] — {durum}\n")
        _md_dosya(zf, "Emailler/_Indeks.md", "".join(indeks_e))

        # Raporlar
        raporlar = db.get_reports()
        indeks_r = ["# Raporlar\n\n"]
        for r in raporlar:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM reports WHERE id = ?", (r["id"],))
            row = cursor.fetchone()
            conn.close()
            icerik = f"# {r['title']}\n\n**Tarih:** {r['created_at']}\n\n---\n\n{row[0] if row else ''}\n"
            _md_dosya(zf, f"Raporlar/Rapor_{r['id']:04d}.md", icerik)
            indeks_r.append(f"- [[Rapor_{r['id']:04d}|{r['title']}]]\n")
        _md_dosya(zf, "Raporlar/_Indeks.md", "".join(indeks_r))

        # Proje dosyaları
        repo = os.path.dirname(__file__)
        for dosya in PROJE_DOSYALARI:
            yol = os.path.join(repo, dosya)
            if not os.path.exists(yol):
                continue
            with open(yol, encoding="utf-8", errors="replace") as f:
                ham = f.read()
            uzanti = dosya.rsplit(".", 1)[-1]
            dil = {"py": "python", "toml": "toml", "txt": "text"}.get(uzanti, "")
            if dil:
                md = f"# {dosya}\n\n```{dil}\n{ham}\n```\n"
            else:
                md = f"# {dosya}\n\n{ham}\n"
            _md_dosya(zf, f"Proje Dosyaları/{dosya}.md", md)

        # Ana sayfa
        stats = db.get_statistics()
        ana = f"""# Kişisel Asistan — Obsidian Export

> Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}

| Alan | Sayı |
|------|------|
| Chat Oturumları | {len(oturumlar)} |
| Bekleyen Görevler | {stats['pending_tasks']} |
| Tamamlanan Görevler | {stats['completed_tasks']} |
| Emailler | {stats['sent_emails'] + stats['unsent_emails']} |
| Raporlar | {stats['total_reports']} |

## Bölümler
- [[Chat Geçmişi/_Indeks|Chat Geçmişi]]
- [[Gorevler|Görevler]]
- [[Emailler/_Indeks|Emailler]]
- [[Raporlar/_Indeks|Raporlar]]
- [[Proje Dosyaları|Proje Dosyaları]]
"""
        _md_dosya(zf, "Ana Sayfa.md", ana)

    buf.seek(0)
    return buf.read()


# Sayfa ayarları
st.set_page_config(
    page_title="🤖 Kişisel Asistan",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'assistant' not in st.session_state:
    try:
        st.session_state.assistant = PersonalAssistant()
        st.session_state.db = Database()
    except Exception as e:
        st.error(f"⚠️ API Key hatası: {str(e)}")
        st.info("Lütfen .env dosyanızda ANTHROPIC_API_KEY'inizi ayarlayın")
        st.stop()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🤖 Kişisel Asistan")
    st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Sohbet",
    "📝 Notlar",
    "📧 Email",
    "📄 PDF"
])

# ==================== SOHBET TAB ====================
with tab1:
    st.header("💬 Claude AI ile Sohbet")

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])

    # Input
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input(
            "Sorunuz:",
            placeholder="Merhaba, nasılsın?",
            label_visibility="collapsed"
        )
    with col2:
        send_btn = st.button("📤 Gönder", use_container_width=True)

    # Process message
    if send_btn and user_input:
        try:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            st.session_state.db.save_chat_message(
                st.session_state.chat_session_id, 'user', user_input
            )

            # Get AI response
            with st.spinner("🤔 Düşünüyor..."):
                response = st.session_state.assistant.chat(user_input)

            # Add assistant message to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            st.session_state.db.save_chat_message(
                st.session_state.chat_session_id, 'assistant', response
            )

            # Otomatik Drive yükleme
            if st.session_state.get("auto_drive_upload", False):
                try:
                    import google_drive as gd
                    if gd.is_authenticated():
                        zip_data = _obsidian_zip(st.session_state.db)
                        gd.upload_zip(zip_data)
                except Exception:
                    pass

            st.rerun()
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")

# ==================== NOTLAR TAB ====================
with tab2:
    st.header("📝 Notlarınız")

    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        st.subheader("✏️ Yeni Not Ekle")
        note_text = st.text_area(
            "Not yazın:",
            height=120,
            placeholder="Örnek: Pazartesi 3'te toplantı...",
            label_visibility="collapsed"
        )

        if st.button("💾 Kaydet", use_container_width=True):
            if note_text.strip():
                try:
                    st.session_state.assistant.add_note(note_text)
                    st.success("✅ Not kaydedildi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
            else:
                st.warning("⚠️ Not boş olamaz!")

    with col2:
        st.subheader("🔍 Filtre")
        search_term = st.text_input("Not ara:", placeholder="Anahtar kelime...")

    # Display notes
    st.subheader("📚 Kayıtlı Notlar")
    try:
        notes = st.session_state.assistant.list_notes()

        if notes:
            for i, note in enumerate(notes, 1):
                # Check if search matches
                if search_term and search_term.lower() not in note['content'].lower():
                    continue

                with st.container(border=True):
                    col1, col2 = st.columns([0.9, 0.1])

                    with col1:
                        st.write(f"**{i}. {note['content'][:100]}...**" if len(note['content']) > 100 else f"**{i}. {note['content']}**")
                        st.caption(f"📅 {note['created_at']}")

                    with col2:
                        if st.button("🗑️", key=f"delete_{i}"):
                            st.session_state.assistant.delete_note(note['id'])
                            st.success("Silindi!")
                            st.rerun()
        else:
            st.info("📭 Henüz not yok. Eklemek için yukarıya yazın!")

    except Exception as e:
        st.error(f"❌ Notlar yüklenemiyor: {str(e)}")

# ==================== EMAIL TAB ====================
with tab3:
    st.header("📧 Email Gönder")

    col1, col2 = st.columns(2)

    with col1:
        recipient = st.text_input(
            "Alıcı Email:",
            placeholder="ornek@gmail.com"
        )

    with col2:
        subject = st.text_input(
            "Konu:",
            placeholder="Email konusu..."
        )

    body = st.text_area(
        "İçerik:",
        height=150,
        placeholder="Email metni...",
        label_visibility="collapsed"
    )

    if st.button("📤 Gönder", use_container_width=True, type="primary"):
        if recipient and subject and body:
            try:
                with st.spinner("Gönderiliyor..."):
                    st.session_state.assistant.send_email(recipient, subject, body)
                st.success("✅ Email başarıyla gönderildi!")
            except Exception as e:
                st.error(f"❌ Email gönderilemedi: {str(e)}")
                st.info("💡 Lütfen .env dosyasındaki email ayarlarını kontrol edin")
        else:
            st.warning("⚠️ Tüm alanları doldurunuz!")

# ==================== PDF TAB ====================
with tab4:
    st.header("📄 PDF Rapor Oluştur")

    col1, col2 = st.columns(2)

    with col1:
        report_title = st.text_input(
            "Rapor Başlığı:",
            value="Aylık Rapor"
        )

    with col2:
        report_type = st.selectbox(
            "Rapor Türü:",
            ["Özet", "Detaylı", "Analiz"]
        )

    report_content = st.text_area(
        "Rapor İçeriği:",
        height=150,
        placeholder="Rapor metni..."
    )

    if st.button("📥 PDF Oluştur", use_container_width=True, type="primary"):
        if report_content.strip():
            try:
                with st.spinner("PDF oluşturuluyor..."):
                    filename = st.session_state.assistant.generate_pdf(
                        title=report_title,
                        content=report_content,
                        report_type=report_type
                    )
                st.success("✅ PDF başarıyla oluşturuldu!")

                # Download button
                with open(filename, "rb") as f:
                    st.download_button(
                        label="💾 İndir",
                        data=f.read(),
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ PDF oluşturulamadı: {str(e)}")
        else:
            st.warning("⚠️ Rapor içeriği boş olamaz!")

# Sidebar
with st.sidebar:
    st.title("⚙️ Ayarlar")

    st.subheader("📊 İstatistikler")
    try:
        notes_count = len(st.session_state.assistant.list_notes())
        st.metric("Toplam Notlar", notes_count)
        st.metric("Sohbet Sayısı", len(st.session_state.chat_history) // 2)
    except:
        pass

    st.divider()

    st.subheader("ℹ️ Bilgi")
    st.info("""
    **Kişisel Asistan v1.0**

    ✨ Özellikler:
    - 💬 AI Sohbet
    - 📝 Not Yönetimi
    - 📧 Email Gönderme
    - 📄 PDF Oluşturma

    📚 Teknoloji:
    - Claude API
    - Streamlit
    - SQLite
    """)

    st.divider()

    if st.button("🔄 Sohbeti Temizle", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    st.subheader("📥 Obsidian Export")

    # ZIP indirme butonu
    if st.button("📦 ZIP Hazırla", use_container_width=True):
        try:
            with st.spinner("Export hazırlanıyor..."):
                zip_data = _obsidian_zip(st.session_state.db)
            st.download_button(
                label="⬇️ İndir",
                data=zip_data,
                file_name=f"obsidian_export_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                mime="application/zip",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ Export hatası: {str(e)}")

    st.divider()

    # Google Drive otomatik yükleme
    st.subheader("☁️ Google Drive")

    try:
        import google_drive as gd
        drive_ok = gd.is_authenticated()
    except ImportError:
        drive_ok = False
        gd = None

    if gd is None:
        st.warning("google_drive.py bulunamadı.")
    elif not drive_ok:
        st.info("Google Drive'a bağlanmak için `credentials.json` dosyanızı uygulama klasörüne koyun, sonra bağlan butonuna tıklayın.")
        if st.button("🔗 Google Drive'a Bağlan", use_container_width=True):
            try:
                with st.spinner("Tarayıcıda oturum açılıyor..."):
                    gd._get_service()
                st.success("✅ Bağlantı kuruldu!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {str(e)}")
    else:
        st.success("✅ Google Drive bağlı")

        # Otomatik yükleme ayarı
        auto_upload = st.toggle(
            "Her sohbet sonunda otomatik yükle",
            value=st.session_state.get("auto_drive_upload", False),
            key="auto_drive_upload",
        )

        if st.button("⬆️ Şimdi Drive'a Yükle", use_container_width=True):
            try:
                with st.spinner("Drive'a yükleniyor..."):
                    zip_data = _obsidian_zip(st.session_state.db)
                    link = gd.upload_zip(zip_data)
                st.success("✅ Yüklendi!")
                st.markdown(f"[Drive'da aç]({link})")
            except Exception as e:
                st.error(f"❌ {str(e)}")

        if st.button("🔓 Drive Bağlantısını Kes", use_container_width=True):
            gd.revoke_auth()
            st.rerun()

    if st.button("❌ Çıkış", use_container_width=True):
        st.info("👋 Görüşmek üzere!")

st.markdown("---")
st.caption("🤖 Kişisel Asistan © 2026 | Powered by Claude AI")
