import streamlit as st
import os
from datetime import datetime
from full_featured_assistant import PersonalAssistant
from database import Database

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

            # Get AI response
            with st.spinner("🤔 Düşünüyor..."):
                response = st.session_state.assistant.chat(user_input)

            # Add assistant message to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })

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

    if st.button("❌ Çıkış", use_container_width=True):
        st.info("👋 Görüşmek üzere!")

st.markdown("---")
st.caption("🤖 Kişisel Asistan © 2026 | Powered by Claude AI")
