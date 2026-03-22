import streamlit as st
import os
from datetime import datetime
from full_featured_assistant import PersonalAssistant
from database import Database
from notebook_lm import NotebookLMService

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

if 'notebook_service' not in st.session_state:
    try:
        st.session_state.notebook_service = NotebookLMService()
    except Exception as e:
        st.session_state.notebook_service = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🤖 Kişisel Asistan")
    st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Sohbet",
    "📝 Notlar",
    "📧 Email",
    "📄 PDF",
    "📚 NotebookLM"
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

# ==================== NOTEBOOK LM TAB ====================
with tab5:
    st.header("📚 NotebookLM - Belge Tabanlı AI Asistan")
    st.markdown("Belgelerinizi yükleyin, sorular sorun ve AI'dan içgörüler elde edin.")

    nlm = st.session_state.get('notebook_service')
    if nlm is None:
        st.error("NotebookLM servisi başlatılamadı. API Key'i kontrol edin.")
    else:
        # Sidebar sol panel: Notebook yönetimi
        nlm_col1, nlm_col2 = st.columns([1, 2])

        with nlm_col1:
            st.subheader("📖 Notebooklar")

            # Yeni notebook oluştur
            with st.expander("➕ Yeni Notebook", expanded=False):
                nb_name = st.text_input("Notebook Adı:", placeholder="Örn: Proje Araştırması", key="nb_name_input")
                nb_desc = st.text_input("Açıklama (opsiyonel):", placeholder="Kısa açıklama...", key="nb_desc_input")
                if st.button("Oluştur", key="create_nb_btn", use_container_width=True):
                    if nb_name.strip():
                        nb_id = nlm.create_notebook(nb_name.strip(), nb_desc.strip())
                        st.success(f"Notebook oluşturuldu!")
                        st.rerun()
                    else:
                        st.warning("Notebook adı boş olamaz!")

            # Notebook listesi
            notebooks = nlm.list_notebooks()
            if not notebooks:
                st.info("Henüz notebook yok.")
            else:
                selected_nb_id = st.session_state.get('selected_notebook_id')
                for nb in notebooks:
                    is_selected = selected_nb_id == nb['id']
                    btn_label = f"{'✅ ' if is_selected else ''}{nb['name']} ({nb['source_count']} kaynak)"
                    if st.button(btn_label, key=f"nb_{nb['id']}", use_container_width=True):
                        st.session_state.selected_notebook_id = nb['id']
                        st.rerun()
                    if is_selected:
                        if st.button("🗑️ Sil", key=f"del_nb_{nb['id']}", use_container_width=True):
                            nlm.delete_notebook(nb['id'])
                            st.session_state.pop('selected_notebook_id', None)
                            st.success("Silindi!")
                            st.rerun()

        with nlm_col2:
            selected_nb_id = st.session_state.get('selected_notebook_id')

            if not selected_nb_id:
                st.info("Sol taraftan bir notebook seçin veya yeni oluşturun.")
            else:
                # Seçili notebook bilgisi
                notebooks = nlm.list_notebooks()
                selected_nb = next((nb for nb in notebooks if nb['id'] == selected_nb_id), None)
                if not selected_nb:
                    st.warning("Notebook bulunamadı.")
                else:
                    st.subheader(f"📖 {selected_nb['name']}")
                    if selected_nb['description']:
                        st.caption(selected_nb['description'])

                    nb_tab1, nb_tab2, nb_tab3 = st.tabs(["📄 Kaynaklar", "💬 Soru-Cevap", "🔍 Analiz"])

                    # --- KAYNAKLAR SEKMESİ ---
                    with nb_tab1:
                        st.markdown("**Belge Ekle**")
                        upload_type = st.radio("Kaynak Türü:", ["Metin Yaz", "Dosya Yükle"], horizontal=True, key="upload_type")

                        if upload_type == "Metin Yaz":
                            src_name = st.text_input("Kaynak Adı:", placeholder="Örn: Makale 1", key="src_name_text")
                            src_content = st.text_area("İçerik:", height=150, placeholder="Buraya metin yapıştırın...", key="src_content_text")
                            if st.button("Kaynak Ekle", key="add_src_text", use_container_width=True):
                                if src_name.strip() and src_content.strip():
                                    nlm.add_source(selected_nb_id, src_name.strip(), src_content.strip(), "text")
                                    st.success("Kaynak eklendi!")
                                    st.rerun()
                                else:
                                    st.warning("Ad ve içerik boş olamaz!")

                        else:
                            uploaded_file = st.file_uploader("Dosya yükle (TXT veya PDF):", type=["txt", "pdf"], key="file_uploader")
                            if uploaded_file:
                                if uploaded_file.type == "application/pdf":
                                    file_content = nlm.extract_text_from_pdf(uploaded_file.read())
                                else:
                                    file_content = uploaded_file.read().decode("utf-8", errors="replace")

                                st.text_area("Önizleme:", value=file_content[:500] + ("..." if len(file_content) > 500 else ""), height=100, disabled=True, key="file_preview")
                                if st.button("Dosyayı Ekle", key="add_src_file", use_container_width=True):
                                    nlm.add_source(selected_nb_id, uploaded_file.name, file_content, uploaded_file.type)
                                    st.success(f"'{uploaded_file.name}' eklendi!")
                                    st.rerun()

                        st.divider()
                        st.markdown("**Mevcut Kaynaklar**")
                        sources = nlm.get_sources(selected_nb_id)
                        if not sources:
                            st.info("Henüz kaynak yok. Yukarıdan ekleyin.")
                        else:
                            for src in sources:
                                with st.container(border=True):
                                    c1, c2 = st.columns([0.85, 0.15])
                                    with c1:
                                        st.markdown(f"**{src['name']}**")
                                        st.caption(f"{src['source_type']} | {src['created_at']} | {len(src['content'])} karakter")
                                        with st.expander("İçeriği Göster"):
                                            st.text(src['content'][:1000] + ("..." if len(src['content']) > 1000 else ""))
                                    with c2:
                                        if st.button("🗑️", key=f"del_src_{src['id']}"):
                                            nlm.delete_source(src['id'])
                                            st.success("Kaynak silindi!")
                                            st.rerun()

                    # --- SORU-CEVAP SEKMESİ ---
                    with nb_tab2:
                        st.markdown("Kaynaklar hakkında soru sorun, Claude size yanıt versin.")

                        if 'nb_chat_history' not in st.session_state:
                            st.session_state.nb_chat_history = {}

                        nb_history = st.session_state.nb_chat_history.get(selected_nb_id, [])

                        # Geçmiş mesajları göster
                        for msg in nb_history:
                            st.chat_message(msg['role']).write(msg['content'])

                        question = st.chat_input("Kaynaklar hakkında soru sorun...", key="nb_question")
                        if question:
                            nb_history.append({'role': 'user', 'content': question})
                            st.chat_message("user").write(question)

                            with st.spinner("Yanıt hazırlanıyor..."):
                                answer = nlm.ask_question(selected_nb_id, question)

                            nb_history.append({'role': 'assistant', 'content': answer})
                            st.chat_message("assistant").write(answer)
                            st.session_state.nb_chat_history[selected_nb_id] = nb_history

                        if nb_history and st.button("Sohbeti Temizle", key="clear_nb_chat"):
                            st.session_state.nb_chat_history[selected_nb_id] = []
                            st.rerun()

                    # --- ANALİZ SEKMESİ ---
                    with nb_tab3:
                        st.markdown("Kaynakları otomatik analiz edin.")

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("📝 Özet Oluştur", use_container_width=True, key="gen_summary"):
                                with st.spinner("Özet oluşturuluyor..."):
                                    summary = nlm.generate_summary(selected_nb_id)
                                st.session_state['nb_analysis_result'] = ('Özet', summary)
                                st.rerun()

                            if st.button("🔑 Anahtar Bilgiler", use_container_width=True, key="gen_insights"):
                                with st.spinner("Anahtar bilgiler çıkarılıyor..."):
                                    insights = nlm.get_key_insights(selected_nb_id)
                                st.session_state['nb_analysis_result'] = ('Anahtar Bilgiler', insights)
                                st.rerun()

                        with col_b:
                            if st.button("❓ FAQ Oluştur", use_container_width=True, key="gen_faq"):
                                with st.spinner("FAQ oluşturuluyor..."):
                                    faq = nlm.generate_faq(selected_nb_id)
                                st.session_state['nb_analysis_result'] = ('Sık Sorulan Sorular', faq)
                                st.rerun()

                        analysis_result = st.session_state.get('nb_analysis_result')
                        if analysis_result:
                            title, content = analysis_result
                            st.divider()
                            st.subheader(f"📊 {title}")
                            st.markdown(content)


st.markdown("---")
st.caption("🤖 Kişisel Asistan © 2026 | Powered by Claude AI")
