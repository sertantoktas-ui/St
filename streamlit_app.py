import streamlit as st
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from database import AssistantDatabase
import execution.task_operations as tasks
import execution.email_operations as emails
import execution.report_operations as reports
import execution.search_operations as notes_svc
from execution.tools_config import TOOLS
from execution.tool_executor import execute as execute_tool

load_dotenv()

st.set_page_config(
    page_title="🤖 Kişisel Asistan",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    </style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "anthropic_client" not in st.session_state:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    st.session_state.anthropic_client = Anthropic(api_key=api_key) if api_key else None

if "db" not in st.session_state:
    st.session_state.db = AssistantDatabase()

db: AssistantDatabase = st.session_state.db

# ── Orchestrator helper ────────────────────────────────────────────────────────
def get_directive(name: str) -> str:
    """DB'den direktif içeriğini çek — L1→L2 köprüsü."""
    d = db.get_directive(name)
    return d["content"] if d else ""

# ── Header ────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🤖 Kişisel Asistan")
    st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Sohbet",
    "📝 Notlar",
    "✅ Görevler",
    "📧 Email",
    "📄 PDF",
    "📋 Direktifler",
])

# ==================== SOHBET TAB ====================
with tab1:
    st.header("💬 Claude AI ile Sohbet")

    for message in st.session_state.chat_history:
        st.chat_message(message["role"]).write(message["content"])

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input("Sorunuz:", placeholder="Merhaba, nasılsın?", label_visibility="collapsed")
    with col2:
        send_btn = st.button("📤 Gönder", use_container_width=True)

    if send_btn and user_input:
        client = st.session_state.anthropic_client
        if not client:
            st.error("⚠️ ANTHROPIC_API_KEY bulunamadı. .env dosyasını kontrol edin.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("🤔 Düşünüyor..."):
                try:
                    messages = [m for m in st.session_state.chat_history]
                    while True:
                        response = client.messages.create(
                            model="claude-opus-4-6",
                            max_tokens=2048,
                            system="Sen yardımsever bir Türkçe kişisel asistansın. Görev, not, email ve rapor işlemleri için araçları kullan.",
                            tools=TOOLS,
                            messages=messages,
                        )

                        if response.stop_reason == "tool_use":
                            # Asistan yanıtını geçmişe ekle
                            messages.append({"role": "assistant", "content": response.content})
                            # Her tool_use bloğunu çalıştır
                            tool_results = []
                            for block in response.content:
                                if block.type == "tool_use":
                                    result_text = execute_tool(block.name, block.input)
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": result_text,
                                    })
                            messages.append({"role": "user", "content": tool_results})
                            # Sonuç için tekrar döngü
                        else:
                            reply = next((b.text for b in response.content if hasattr(b, "text")), "")
                            st.session_state.chat_history = messages
                            st.session_state.chat_history.append({"role": "assistant", "content": reply})
                            break

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata: {e}")

# ==================== NOTLAR TAB ====================
with tab2:
    st.header("📝 Notlarınız")

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.subheader("✏️ Yeni Not Ekle")
        note_text = st.text_area(
            "Not yazın:", height=120,
            placeholder="Örnek: Pazartesi 3'te toplantı...",
            label_visibility="collapsed"
        )
        if st.button("💾 Kaydet", use_container_width=True):
            if note_text.strip():
                result = notes_svc.add_note(note_text)
                if result["success"]:
                    st.success("✅ Not kaydedildi!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.warning("⚠️ Not boş olamaz!")

    with col2:
        st.subheader("🔍 Filtre")
        search_term = st.text_input("Not ara:", placeholder="Anahtar kelime...")

    st.subheader("📚 Kayıtlı Notlar")
    note_list = notes_svc.search_notes(search_term) if search_term else notes_svc.list_notes()
    if note_list:
        for note in note_list:
            with st.container(border=True):
                c1, c2 = st.columns([0.9, 0.1])
                with c1:
                    preview = note["content"][:100] + ("..." if len(note["content"]) > 100 else "")
                    st.write(f"**{preview}**")
                    st.caption(f"📅 {note['created_at']}")
                with c2:
                    if st.button("🗑️", key=f"del_note_{note['id']}"):
                        notes_svc.delete_note(note["id"])
                        st.rerun()
    else:
        st.info("📭 Henüz not yok.")

# ==================== GÖREVLER TAB ====================
with tab3:
    st.header("✅ Görev Yönetimi")

    # Orchestrator: direktifi yükle (L1→L2)
    get_directive("directives/gorev_yonet.md")

    col1, col2, col3_w = st.columns(3)
    with col1:
        task_title = st.text_input("Görev başlığı:", placeholder="Sunum hazırla")
    with col2:
        task_desc = st.text_input("Açıklama (opsiyonel):")
    with col3_w:
        task_priority = st.selectbox("Öncelik:", ["medium", "low", "high"])

    if st.button("➕ Görev Ekle", use_container_width=True, type="primary"):
        if task_title.strip():
            result = tasks.add_task(task_title, task_desc, task_priority)
            st.success(f"✅ Görev eklendi (ID: {result['task_id']})")
            st.rerun()
        else:
            st.warning("⚠️ Görev başlığı boş olamaz!")

    st.subheader("📋 Bekleyen Görevler")
    pending = tasks.get_tasks("pending")
    if pending:
        for task in pending:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task["priority"], "⚪")
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
                with c1:
                    st.write(f"{priority_emoji} **{task['title']}**")
                    if task["description"]:
                        st.caption(task["description"])
                    st.caption(f"📅 {task['created_at']}")
                with c2:
                    if st.button("✅", key=f"done_{task['id']}", help="Tamamla"):
                        tasks.complete_task(task["id"])
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_task_{task['id']}", help="Sil"):
                        tasks.delete_task(task["id"])
                        st.rerun()
    else:
        st.info("🎉 Bekleyen görev yok!")

    with st.expander("✅ Tamamlanan Görevler"):
        done = tasks.get_tasks("completed")
        for task in done:
            st.write(f"✅ ~~{task['title']}~~")
        if not done:
            st.info("Henüz tamamlanan görev yok.")

# ==================== EMAIL TAB ====================
with tab4:
    st.header("📧 Email")

    get_directive("directives/email_yaz.md")

    col1, col2 = st.columns(2)
    with col1:
        recipient = st.text_input("Alıcı Email:", placeholder="ornek@gmail.com")
        tone = st.selectbox("Ton:", ["formal", "casual", "friendly"])
    with col2:
        subject = st.text_input("Konu:", placeholder="Email konusu...")
        send_now = st.checkbox("Şimdi gönder (SMTP gerekli)", value=False)

    body = st.text_area("İçerik:", height=150, placeholder="Email metni...", label_visibility="collapsed")

    if not emails.smtp_available():
        st.info("💡 SMTP yapılandırılmamış — email taslak olarak kaydedilecek.")

    if st.button("📤 Gönder / Kaydet", use_container_width=True, type="primary"):
        if recipient and subject and body:
            with st.spinner("İşleniyor..."):
                if send_now:
                    result = emails.save_and_send(recipient, subject, body, tone)
                    if result["sent"]:
                        st.success("✅ Email gönderildi!")
                    else:
                        st.warning(f"💾 Email kaydedildi, gönderilemedi: {result.get('send_error', '')}")
                else:
                    result = emails.save_email(recipient, subject, body, tone)
                    st.success(f"💾 Email taslak olarak kaydedildi (ID: {result['email_id']})")
        else:
            st.warning("⚠️ Tüm alanları doldurunuz!")

    with st.expander("📬 Kayıtlı Emailler"):
        saved_emails = emails.get_emails()
        for em in saved_emails:
            status = "✅ Gönderildi" if em["sent"] else "📬 Taslak"
            st.write(f"{status} — **{em['subject']}** → {em['recipient']} ({em['created_at'][:16]})")
        if not saved_emails:
            st.info("Kayıtlı email yok.")

# ==================== PDF TAB ====================
with tab5:
    st.header("📄 PDF Rapor Oluştur")

    get_directive("directives/rapor_olustur.md")

    col1, col2 = st.columns(2)
    with col1:
        report_title = st.text_input("Rapor Başlığı:", value="Aylık Rapor")
    with col2:
        report_type = st.selectbox("Rapor Türü:", ["Özet", "Detaylı", "Analiz"])

    report_content = st.text_area("Rapor İçeriği:", height=150, placeholder="Rapor metni...")

    if st.button("📥 PDF Oluştur", use_container_width=True, type="primary"):
        if report_content.strip():
            with st.spinner("PDF oluşturuluyor..."):
                result = reports.save_and_generate(report_title, report_content, report_type)
            if result["pdf_path"]:
                st.success(f"✅ PDF oluşturuldu! (Rapor ID: {result['report_id']})")
                with open(result["pdf_path"], "rb") as f:
                    st.download_button(
                        label="💾 İndir",
                        data=f.read(),
                        file_name=os.path.basename(result["pdf_path"]),
                        mime="application/pdf",
                    )
            else:
                st.warning(f"💾 Rapor DB'ye kaydedildi, PDF oluşturulamadı: {result.get('pdf_error', '')}")
        else:
            st.warning("⚠️ Rapor içeriği boş olamaz!")

    with st.expander("📋 Oluşturulan Raporlar"):
        rpt_list = reports.get_reports()
        for rpt in rpt_list:
            st.write(f"📄 **{rpt['title']}** — {rpt['created_at'][:16]}")
        if not rpt_list:
            st.info("Henüz rapor yok.")

# ==================== DİREKTİFLER TAB ====================
with tab6:
    st.header("📋 Direktifler")
    st.caption("Sistemin SOP'ları — veritabanında saklanır, buradan görüntülenip düzenlenebilir.")

    all_directives = db.get_all_directives()

    if not all_directives:
        st.info("Veritabanında direktif bulunamadı.")
    else:
        selected = st.selectbox("Direktif seç:", options=[d["name"] for d in all_directives])
        if selected:
            d = db.get_directive(selected)
            if d:
                c1, c2 = st.columns([0.7, 0.3])
                with c1:
                    st.subheader(d["name"])
                with c2:
                    st.caption(f"Son güncelleme: {d['updated_at'][:16]}")
                st.markdown(d["content"])

                with st.expander("✏️ Direktifi Güncelle"):
                    new_content = st.text_area("İçerik:", value=d["content"], height=300, key=f"edit_{selected}")
                    if st.button("💾 Kaydet", key=f"save_{selected}"):
                        db.save_directive(selected, new_content)
                        st.success("✅ Direktif güncellendi!")
                        st.rerun()

    st.divider()
    st.subheader("➕ Yeni Direktif Ekle")
    new_name = st.text_input("Direktif adı:", placeholder="directives/yeni_ozellik.md")
    new_dir_content = st.text_area("İçerik:", height=200, placeholder="## Amaç\n...")
    if st.button("💾 Direktif Ekle"):
        if new_name.strip() and new_dir_content.strip():
            db.save_directive(new_name, new_dir_content)
            st.success(f"✅ '{new_name}' direktifi eklendi!")
            st.rerun()
        else:
            st.warning("⚠️ Ad ve içerik boş olamaz.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Ayarlar")
    st.subheader("📊 İstatistikler")
    try:
        stats = tasks.get_statistics()
        st.metric("Bekleyen Görev", stats["pending_tasks"])
        st.metric("Tamamlanan Görev", stats["completed_tasks"])
        st.metric("Toplam Rapor", stats["total_reports"])
        st.metric("Toplam Not", len(notes_svc.list_notes()))
        st.metric("Sohbet", len(st.session_state.chat_history) // 2)
    except Exception:
        pass

    st.divider()
    st.subheader("ℹ️ Mimari")
    st.info("""
**3-Katmanlı Mimari**

📋 **L1 — Direktifler**
`directives/` → SOP'lar (DB'de)

⚙️ **L2 — Orkestrasyon**
`streamlit_app.py`

🔧 **L3 — Execution**
`execution/` → Deterministik
    """)

    st.divider()
    if st.button("🔄 Sohbeti Temizle", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.caption("🤖 Kişisel Asistan © 2026 | Powered by Claude AI | 3-Katmanlı Mimari")
