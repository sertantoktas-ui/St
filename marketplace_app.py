import streamlit as st
from datetime import date, timedelta
import marketplace_db as db

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaskMarket - Hizmet Pazarı",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* General */
    .main { padding-top: 1rem; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Cards */
    .task-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: box-shadow 0.2s;
    }
    .task-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

    .offer-card {
        background: #fff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    .review-card {
        background: #fffdf5;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .badge-open { color: #28a745; font-weight: 700; }
    .badge-assigned { color: #fd7e14; font-weight: 700; }
    .badge-completed { color: #6c757d; font-weight: 700; }
    .badge-cancelled { color: #dc3545; font-weight: 700; }

    /* Message bubble */
    .msg-me {
        background: #0084ff;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .msg-other {
        background: #e9ecef;
        color: #212529;
        border-radius: 18px 18px 18px 4px;
        padding: 0.5rem 1rem;
        margin: 0.2rem 0;
        max-width: 70%;
        float: left;
        clear: both;
    }
    .msg-wrap { overflow: hidden; margin-bottom: 0.4rem; }

    .stars { color: #ffc107; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)


# ── Session helpers ───────────────────────────────────────────────────────────
def is_logged_in():
    return "user" in st.session_state and st.session_state.user is not None


def current_user():
    return st.session_state.get("user")


def logout():
    st.session_state.user = None
    st.session_state.page = "home"
    st.rerun()


def go(page):
    st.session_state.page = page
    st.rerun()


def stars(rating, max_stars=5):
    full = int(rating)
    empty = max_stars - full
    return "★" * full + "☆" * empty


# ── Init session ─────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_task_id" not in st.session_state:
    st.session_state.selected_task_id = None
if "chat_with" not in st.session_state:
    st.session_state.chat_with = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛠️ TaskMarket")
    st.markdown("---")

    if is_logged_in():
        u = current_user()
        unread = db.get_unread_count(u["id"])
        st.markdown(f"**{u['avatar_emoji']} {u['name']}**")
        st.caption(f"{'Müşteri' if u['role'] == 'client' else 'Hizmet Veren'} · {u['location'] or 'Konum yok'}")
        if u["review_count"] > 0:
            st.markdown(f"<span class='stars'>{stars(u['rating'])}</span> ({u['review_count']} değerlendirme)", unsafe_allow_html=True)
        st.markdown("---")

        st.button("🏠 Ana Sayfa", on_click=go, args=("home",), use_container_width=True)
        st.button("🔍 Görevleri Keşfet", on_click=go, args=("browse",), use_container_width=True)

        if u["role"] == "client":
            st.button("➕ Görev Yayınla", on_click=go, args=("post_task",), use_container_width=True)
            st.button("📋 Görevlerim", on_click=go, args=("my_tasks",), use_container_width=True)
        else:
            st.button("📬 Tekliflerim", on_click=go, args=("my_offers",), use_container_width=True)

        msg_label = f"💬 Mesajlar" + (f" ({unread})" if unread > 0 else "")
        st.button(msg_label, on_click=go, args=("messages",), use_container_width=True)
        st.button("👤 Profilim", on_click=go, args=("profile",), use_container_width=True)
        st.markdown("---")
        st.button("🚪 Çıkış Yap", on_click=logout, use_container_width=True)
    else:
        st.button("🏠 Ana Sayfa", on_click=go, args=("home",), use_container_width=True)
        st.button("🔍 Görevleri Keşfet", on_click=go, args=("browse",), use_container_width=True)
        st.markdown("---")
        st.button("🔑 Giriş Yap", on_click=go, args=("login",), use_container_width=True)
        st.button("📝 Kayıt Ol", on_click=go, args=("register",), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

page = st.session_state.page

# ─── HOME ─────────────────────────────────────────────────────────────────────
if page == "home":
    st.markdown("""
    <div class='hero'>
        <h1>🛠️ TaskMarket</h1>
        <p style='font-size:1.2rem; margin:0.5rem 0 1rem'>
            Güvenilir hizmet uzmanlarını bul · Görev yayınla · Kazan
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    tasks_open = len(db.get_tasks("open"))
    taskers = db.get_top_taskers(100)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='stat-box'><h2>{tasks_open}</h2><p>Açık Görev</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-box'><h2>{len(taskers)}</h2><p>Aktif Uzman</p></div>", unsafe_allow_html=True)
    with col3:
        cats = db.get_categories()
        st.markdown(f"<div class='stat-box'><h2>{len(cats)}</h2><p>Kategori</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Categories
    st.subheader("Kategoriler")
    cats = db.get_categories()
    cols = st.columns(5)
    for i, cat in enumerate(cats):
        with cols[i % 5]:
            if st.button(f"{cat['icon']} {cat['name']}", key=f"cat_{cat['id']}", use_container_width=True):
                st.session_state.browse_category = cat["id"]
                go("browse")

    st.markdown("---")

    # Recent tasks
    st.subheader("Son Açık Görevler")
    recent = db.get_tasks("open")[:6]
    if not recent:
        st.info("Henüz açık görev yok. İlk görevi sen yayınla!")
    else:
        cols = st.columns(2)
        for i, task in enumerate(recent):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"""
                    <div class='task-card'>
                        <strong>{task['category_icon']} {task['title']}</strong><br>
                        <small>📍 {task['location']} &nbsp;|&nbsp; 📅 {task['scheduled_date']}</small><br>
                        <small>👤 {task['client_name']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.caption(f"Bütçe: **{task['budget']:.0f} ₺**")
                    with col_b:
                        if st.button("Detay", key=f"home_task_{task['id']}"):
                            st.session_state.selected_task_id = task["id"]
                            go("task_detail")

    st.markdown("---")

    # Top taskers
    st.subheader("En İyi Uzmanlar")
    top = db.get_top_taskers(6)
    if not top:
        st.info("Henüz uzman kaydı yok.")
    else:
        cols = st.columns(3)
        for i, t in enumerate(top):
            with cols[i % 3]:
                rating_str = f"<span class='stars'>{stars(t['rating'])}</span> {t['rating']:.1f}" if t["review_count"] > 0 else "Yeni"
                st.markdown(f"""
                <div class='task-card' style='text-align:center'>
                    <div style='font-size:2rem'>{t['avatar_emoji']}</div>
                    <strong>{t['name']}</strong><br>
                    <small>📍 {t['location'] or '-'}</small><br>
                    {rating_str}<br>
                    <small>{t['review_count']} değerlendirme</small>
                </div>
                """, unsafe_allow_html=True)


# ─── LOGIN ────────────────────────────────────────────────────────────────────
elif page == "login":
    st.title("🔑 Giriş Yap")
    col, _ = st.columns([1, 1])
    with col:
        with st.form("login_form"):
            email = st.text_input("E-posta")
            password = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True)
            if submitted:
                user = db.login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.success("Hoş geldiniz!")
                    go("home")
                else:
                    st.error("E-posta veya şifre hatalı.")
        st.button("Hesabın yok mu? Kayıt Ol", on_click=go, args=("register",))


# ─── REGISTER ─────────────────────────────────────────────────────────────────
elif page == "register":
    st.title("📝 Kayıt Ol")
    col, _ = st.columns([1, 1])
    with col:
        with st.form("register_form"):
            name = st.text_input("Ad Soyad")
            email = st.text_input("E-posta")
            password = st.text_input("Şifre", type="password")
            password2 = st.text_input("Şifre Tekrar", type="password")
            role = st.selectbox("Hesap Türü", ["client", "tasker"], format_func=lambda x: "Müşteri (Görev yayınlarım)" if x == "client" else "Uzman (Görev alırım)")
            location = st.text_input("Şehir / İlçe")
            bio = st.text_area("Hakkında (opsiyonel)", height=80)
            submitted = st.form_submit_button("Kayıt Ol", use_container_width=True)
            if submitted:
                if not name or not email or not password:
                    st.error("Ad, e-posta ve şifre zorunludur.")
                elif password != password2:
                    st.error("Şifreler eşleşmiyor.")
                else:
                    uid = db.create_user(name, email, password, role, location, bio)
                    if uid:
                        user = db.login_user(email, password)
                        st.session_state.user = user
                        st.success("Kayıt başarılı! Hoş geldiniz.")
                        go("home")
                    else:
                        st.error("Bu e-posta zaten kayıtlı.")
        st.button("Zaten hesabın var mı? Giriş Yap", on_click=go, args=("login",))


# ─── BROWSE TASKS ─────────────────────────────────────────────────────────────
elif page == "browse":
    st.title("🔍 Görevleri Keşfet")

    cats = db.get_categories()
    cat_options = {"Tümü": None} | {f"{c['icon']} {c['name']}": c["id"] for c in cats}

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("Ara...", placeholder="Görev başlığı veya açıklama")
    with col2:
        default_cat = st.session_state.get("browse_category")
        cat_labels = list(cat_options.keys())
        default_index = 0
        if default_cat:
            for i, (label, cid) in enumerate(cat_options.items()):
                if cid == default_cat:
                    default_index = i
                    break
            st.session_state.browse_category = None
        selected_cat_label = st.selectbox("Kategori", cat_labels, index=default_index)
        selected_cat_id = cat_options[selected_cat_label]
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_all = st.checkbox("Tamamlananlar dahil")

    status_filter = None if show_all else "open"
    tasks = db.get_tasks(status=status_filter or "open", category_id=selected_cat_id, search=search or None)

    if show_all:
        for s in ["assigned", "completed"]:
            tasks += db.get_tasks(status=s, category_id=selected_cat_id, search=search or None)

    st.caption(f"{len(tasks)} görev bulundu")

    if not tasks:
        st.info("Arama kriterlerinize uyan görev bulunamadı.")
    else:
        for task in tasks:
            badge_class = f"badge-{task['status']}"
            status_tr = {"open": "Açık", "assigned": "Atandı", "completed": "Tamamlandı", "cancelled": "İptal"}.get(task["status"], task["status"])
            with st.container():
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"""
                    <div class='task-card'>
                        <b>{task['category_icon']} {task['title']}</b>
                        &nbsp;<span class='{badge_class}'>● {status_tr}</span><br>
                        <small>{task['description'][:120]}{'...' if len(task['description']) > 120 else ''}</small><br>
                        <small>📍 {task['location']} &nbsp;|&nbsp; 📅 {task['scheduled_date']} &nbsp;|&nbsp; 👤 {task['client_name']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.metric("Bütçe", f"{task['budget']:.0f} ₺")
                    if st.button("Detay", key=f"browse_{task['id']}"):
                        st.session_state.selected_task_id = task["id"]
                        go("task_detail")


# ─── TASK DETAIL ──────────────────────────────────────────────────────────────
elif page == "task_detail":
    task_id = st.session_state.selected_task_id
    if not task_id:
        st.warning("Görev seçilmedi.")
        go("browse")
    else:
        task = db.get_task(task_id)
        if not task:
            st.error("Görev bulunamadı.")
        else:
            st.button("← Geri", on_click=go, args=("browse",))
            st.title(f"{task['category_icon']} {task['title']}")

            status_tr = {"open": "Açık", "assigned": "Atandı", "completed": "Tamamlandı", "cancelled": "İptal"}.get(task["status"], task["status"])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Bütçe", f"{task['budget']:.0f} ₺")
            col2.metric("Tarih", task["scheduled_date"])
            col3.metric("Konum", task["location"])
            col4.metric("Durum", status_tr)

            st.markdown("---")
            st.subheader("Görev Açıklaması")
            st.write(task["description"])
            st.caption(f"Yayınlayan: {task['client_avatar']} {task['client_name']} · {task['category_name']}")

            offers = db.get_task_offers(task_id)

            # ── Client actions ──
            if is_logged_in() and current_user()["id"] == task["client_id"]:
                st.markdown("---")
                st.subheader(f"Teklifler ({len(offers)})")
                if not offers:
                    st.info("Henüz teklif gelmedi.")
                else:
                    for offer in offers:
                        badge = {"pending": "⏳ Bekliyor", "accepted": "✅ Kabul Edildi", "rejected": "❌ Reddedildi"}.get(offer["status"], offer["status"])
                        st.markdown(f"""
                        <div class='offer-card'>
                            <b>{offer['tasker_avatar']} {offer['tasker_name']}</b> — <b>{offer['price']:.0f} ₺</b> &nbsp; {badge}<br>
                            <small>📍 {offer['tasker_location'] or '-'} &nbsp;|&nbsp; <span class='stars'>{stars(offer['tasker_rating'])}</span> ({offer['tasker_reviews']} değerlendirme)</small><br>
                            <em>"{offer['message']}"</em>
                        </div>
                        """, unsafe_allow_html=True)

                        if offer["status"] == "pending" and task["status"] == "open":
                            ca, cb, cc = st.columns([1, 1, 3])
                            with ca:
                                if st.button("Kabul Et", key=f"acc_{offer['id']}"):
                                    db.accept_offer(offer["id"], task_id, offer["tasker_id"])
                                    st.success("Teklif kabul edildi!")
                                    st.rerun()
                            with cb:
                                if st.button("Reddet", key=f"rej_{offer['id']}"):
                                    db.reject_offer(offer["id"])
                                    st.rerun()
                            with cc:
                                if st.button("Mesaj Gönder", key=f"msg_{offer['tasker_id']}"):
                                    st.session_state.chat_with = {"id": offer["tasker_id"], "name": offer["tasker_name"]}
                                    go("messages")

                if task["status"] == "assigned":
                    st.markdown("---")
                    if st.button("✅ Görevi Tamamlandı Olarak İşaretle", type="primary"):
                        db.complete_task(task_id)
                        st.success("Görev tamamlandı!")
                        st.rerun()

                if task["status"] == "open":
                    if st.button("🚫 Görevi İptal Et"):
                        db.cancel_task(task_id)
                        st.rerun()

                if task["status"] == "completed" and not db.has_reviewed(task_id, current_user()["id"]):
                    st.markdown("---")
                    st.subheader("Uzmanı Değerlendir")
                    with st.form("review_tasker"):
                        rating = st.slider("Puan", 1, 5, 5)
                        comment = st.text_area("Yorum")
                        if st.form_submit_button("Değerlendirme Gönder"):
                            db.create_review(task_id, current_user()["id"], task["tasker_id"], rating, comment)
                            st.success("Değerlendirmeniz kaydedildi!")
                            st.rerun()

            # ── Tasker: make offer ──
            elif is_logged_in() and current_user()["role"] == "tasker" and task["status"] == "open":
                st.markdown("---")
                already = any(o["tasker_id"] == current_user()["id"] for o in offers)
                if already:
                    st.info("Bu göreve zaten teklif verdiniz.")
                else:
                    st.subheader("Teklif Ver")
                    with st.form("make_offer"):
                        price = st.number_input("Teklif Fiyatı (₺)", min_value=1.0, value=float(task["budget"]), step=10.0)
                        message = st.text_area("Mesajınız", placeholder="Kendinizi tanıtın ve görevi nasıl yapacağınızı açıklayın...")
                        if st.form_submit_button("Teklif Gönder", type="primary"):
                            if not message.strip():
                                st.error("Lütfen bir mesaj yazın.")
                            else:
                                db.create_offer(task_id, current_user()["id"], price, message)
                                st.success("Teklifiniz gönderildi!")
                                st.rerun()

                st.markdown("---")
                st.subheader(f"Diğer Teklifler ({len(offers)})")
                for offer in offers:
                    st.markdown(f"- **{offer['tasker_name']}** — {offer['price']:.0f} ₺")

            elif not is_logged_in():
                st.markdown("---")
                st.info("Teklif vermek veya görev detaylarını görmek için giriş yapın.")
                st.button("Giriş Yap", on_click=go, args=("login",))


# ─── POST TASK ────────────────────────────────────────────────────────────────
elif page == "post_task":
    if not is_logged_in():
        st.warning("Görev yayınlamak için giriş yapmalısınız.")
        go("login")
    elif current_user()["role"] != "client":
        st.warning("Sadece müşteriler görev yayınlayabilir.")
    else:
        st.title("➕ Yeni Görev Yayınla")
        cats = db.get_categories()
        cat_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}

        with st.form("post_task_form"):
            title = st.text_input("Görev Başlığı", placeholder="Örn: Evimin 3 odasını temizlemesi lazım")
            description = st.text_area("Detaylı Açıklama", height=120, placeholder="Ne yapılmasını istiyorsunuz? Detayları belirtin...")
            col1, col2 = st.columns(2)
            with col1:
                cat_label = st.selectbox("Kategori", list(cat_map.keys()))
            with col2:
                budget = st.number_input("Bütçe (₺)", min_value=50.0, max_value=50000.0, value=500.0, step=50.0)
            col3, col4 = st.columns(2)
            with col3:
                location = st.text_input("Konum", value=current_user().get("location", ""), placeholder="İstanbul, Kadıköy")
            with col4:
                scheduled_date = st.date_input("Görev Tarihi", value=date.today() + timedelta(days=3), min_value=date.today())

            submitted = st.form_submit_button("Görevi Yayınla", type="primary", use_container_width=True)
            if submitted:
                if not title.strip() or not description.strip() or not location.strip():
                    st.error("Lütfen tüm alanları doldurun.")
                else:
                    tid = db.create_task(
                        current_user()["id"], title, description,
                        cat_map[cat_label], location, budget,
                        str(scheduled_date),
                    )
                    st.success(f"Görev yayınlandı! (#{tid})")
                    st.session_state.selected_task_id = tid
                    go("task_detail")


# ─── MY TASKS (client) ────────────────────────────────────────────────────────
elif page == "my_tasks":
    if not is_logged_in():
        go("login")
    else:
        st.title("📋 Görevlerim")
        tasks = db.get_client_tasks(current_user()["id"])
        if not tasks:
            st.info("Henüz görev yayınlamadınız.")
            st.button("İlk Görevi Yayınla", on_click=go, args=("post_task",))
        else:
            tab_open, tab_assigned, tab_done, tab_cancelled = st.tabs(["Açık", "Atandı", "Tamamlandı", "İptal"])

            def render_tasks(task_list):
                if not task_list:
                    st.info("Bu kategoride görev yok.")
                    return
                for task in task_list:
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        tasker_info = f" → {task['tasker_name']}" if task.get("tasker_name") else ""
                        st.markdown(f"""
                        <div class='task-card'>
                            <b>{task['category_icon']} {task['title']}</b>{tasker_info}<br>
                            <small>📍 {task['location']} &nbsp;|&nbsp; 📅 {task['scheduled_date']} &nbsp;|&nbsp; Bütçe: {task['budget']:.0f} ₺</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        if st.button("Detay", key=f"my_{task['id']}"):
                            st.session_state.selected_task_id = task["id"]
                            go("task_detail")

            with tab_open:
                render_tasks([t for t in tasks if t["status"] == "open"])
            with tab_assigned:
                render_tasks([t for t in tasks if t["status"] == "assigned"])
            with tab_done:
                render_tasks([t for t in tasks if t["status"] == "completed"])
            with tab_cancelled:
                render_tasks([t for t in tasks if t["status"] == "cancelled"])


# ─── MY OFFERS (tasker) ───────────────────────────────────────────────────────
elif page == "my_offers":
    if not is_logged_in():
        go("login")
    else:
        st.title("📬 Tekliflerim")
        offers = db.get_tasker_offers(current_user()["id"])
        if not offers:
            st.info("Henüz teklif vermediniz.")
            st.button("Görevlere Göz At", on_click=go, args=("browse",))
        else:
            for offer in offers:
                offer_status_tr = {"pending": "⏳ Bekliyor", "accepted": "✅ Kabul Edildi", "rejected": "❌ Reddedildi"}.get(offer["status"], offer["status"])
                task_status_tr = {"open": "Açık", "assigned": "Atandı", "completed": "Tamamlandı", "cancelled": "İptal"}.get(offer["task_status"], offer["task_status"])
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"""
                    <div class='offer-card'>
                        <b>{offer['task_title']}</b> — Görev: {task_status_tr} | Teklif: {offer_status_tr}<br>
                        <small>📍 {offer['task_location']} &nbsp;|&nbsp; 📅 {offer['scheduled_date']} &nbsp;|&nbsp; Müşteri: {offer['client_name']}</small><br>
                        <small>Teklifiniz: <b>{offer['price']:.0f} ₺</b></small>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("Detay", key=f"off_{offer['id']}"):
                        st.session_state.selected_task_id = offer["task_id"]
                        go("task_detail")

                if offer["status"] == "accepted" and offer["task_status"] == "completed":
                    if not db.has_reviewed(offer["task_id"], current_user()["id"]):
                        with st.expander("Müşteriyi Değerlendir"):
                            task = db.get_task(offer["task_id"])
                            with st.form(f"rev_{offer['id']}"):
                                rating = st.slider("Puan", 1, 5, 5, key=f"r_{offer['id']}")
                                comment = st.text_area("Yorum", key=f"c_{offer['id']}")
                                if st.form_submit_button("Gönder"):
                                    db.create_review(offer["task_id"], current_user()["id"], task["client_id"], rating, comment)
                                    st.success("Değerlendirmeniz kaydedildi!")
                                    st.rerun()


# ─── MESSAGES ─────────────────────────────────────────────────────────────────
elif page == "messages":
    if not is_logged_in():
        go("login")
    else:
        st.title("💬 Mesajlar")
        convs = db.get_conversations(current_user()["id"])

        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.subheader("Konuşmalar")
            if not convs:
                st.info("Henüz mesajınız yok.")
            for conv in convs:
                unread_badge = f" 🔴{conv['unread_count']}" if conv["unread_count"] > 0 else ""
                label = f"{conv['other_avatar']} {conv['other_name']}{unread_badge}"
                if st.button(label, key=f"conv_{conv['other_id']}", use_container_width=True):
                    st.session_state.chat_with = {"id": conv["other_id"], "name": conv["other_name"]}
                    st.rerun()

        with col_right:
            chat = st.session_state.chat_with
            if not chat:
                st.info("Sol taraftan bir konuşma seçin.")
            else:
                st.subheader(f"💬 {chat['name']}")
                msgs = db.get_conversation(current_user()["id"], chat["id"])

                chat_html = "<div style='height:400px; overflow-y:auto; padding:1rem; border:1px solid #dee2e6; border-radius:10px; margin-bottom:1rem;'>"
                for msg in msgs:
                    is_me = msg["sender_id"] == current_user()["id"]
                    css = "msg-me" if is_me else "msg-other"
                    chat_html += f"<div class='msg-wrap'><div class='{css}'>{msg['content']}<br><small style='opacity:0.7'>{msg['created_at'][:16]}</small></div></div>"
                chat_html += "</div>"
                st.markdown(chat_html, unsafe_allow_html=True)

                with st.form("send_msg", clear_on_submit=True):
                    msg_text = st.text_input("Mesaj yaz...", label_visibility="collapsed")
                    if st.form_submit_button("Gönder ➤"):
                        if msg_text.strip():
                            db.send_message(current_user()["id"], chat["id"], msg_text.strip())
                            st.rerun()


# ─── PROFILE ──────────────────────────────────────────────────────────────────
elif page == "profile":
    if not is_logged_in():
        go("login")
    else:
        u = current_user()
        st.title(f"{u['avatar_emoji']} Profilim")

        tab_info, tab_reviews = st.tabs(["Bilgiler", "Değerlendirmeler"])

        with tab_info:
            with st.form("profile_form"):
                name = st.text_input("Ad Soyad", value=u["name"])
                bio = st.text_area("Hakkında", value=u.get("bio", ""), height=100)
                location = st.text_input("Konum", value=u.get("location", ""))
                if st.form_submit_button("Kaydet", type="primary"):
                    db.update_user_profile(u["id"], name, bio, location)
                    updated = db.get_user(u["id"])
                    st.session_state.user = updated
                    st.success("Profil güncellendi!")
                    st.rerun()

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Rol", "Müşteri" if u["role"] == "client" else "Uzman")
            col2.metric("Puan", f"{u['rating']:.1f} / 5.0" if u["review_count"] > 0 else "—")
            col3.metric("Değerlendirme", u["review_count"])

        with tab_reviews:
            reviews = db.get_user_reviews(u["id"])
            if not reviews:
                st.info("Henüz değerlendirme almadınız.")
            else:
                for rev in reviews:
                    st.markdown(f"""
                    <div class='review-card'>
                        <span class='stars'>{stars(rev['rating'])}</span> <b>{rev['rating']}/5</b>
                        — <em>{rev['task_title']}</em><br>
                        <small>{rev['reviewer_avatar']} {rev['reviewer_name']} · {rev['created_at'][:10]}</small><br>
                        "{rev['comment']}"
                    </div>
                    """, unsafe_allow_html=True)

else:
    go("home")
