import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Dünya Saati",
    page_icon="🕐",
    layout="centered",
)

# Ülke -> Timezone eşlemeleri
ULKELER = {
    "Türkiye": "Europe/Istanbul",
    "Amerika Birleşik Devletleri (New York)": "America/New_York",
    "Amerika Birleşik Devletleri (Los Angeles)": "America/Los_Angeles",
    "Amerika Birleşik Devletleri (Chicago)": "America/Chicago",
    "İngiltere": "Europe/London",
    "Fransa": "Europe/Paris",
    "Almanya": "Europe/Berlin",
    "İtalya": "Europe/Rome",
    "İspanya": "Europe/Madrid",
    "Rusya (Moskova)": "Europe/Moscow",
    "Çin": "Asia/Shanghai",
    "Japonya": "Asia/Tokyo",
    "Hindistan": "Asia/Kolkata",
    "Avustralya (Sidney)": "Australia/Sydney",
    "Avustralya (Melbourne)": "Australia/Melbourne",
    "Brezilya (São Paulo)": "America/Sao_Paulo",
    "Kanada (Toronto)": "America/Toronto",
    "Meksika (Mexico City)": "America/Mexico_City",
    "Suudi Arabistan": "Asia/Riyadh",
    "Birleşik Arap Emirlikleri": "Asia/Dubai",
    "Güney Kore": "Asia/Seoul",
    "Singapur": "Asia/Singapore",
    "Hong Kong": "Asia/Hong_Kong",
    "İsviçre": "Europe/Zurich",
    "Hollanda": "Europe/Amsterdam",
    "Belçika": "Europe/Brussels",
    "İsveç": "Europe/Stockholm",
    "Norveç": "Europe/Oslo",
    "Danimarka": "Europe/Copenhagen",
    "Finlandiya": "Europe/Helsinki",
    "Polonya": "Europe/Warsaw",
    "Avusturya": "Europe/Vienna",
    "Portekiz": "Europe/Lisbon",
    "Yunanistan": "Europe/Athens",
    "Mısır": "Africa/Cairo",
    "Güney Afrika": "Africa/Johannesburg",
    "Nijerya": "Africa/Lagos",
    "Kenya": "Africa/Nairobi",
    "Pakistan": "Asia/Karachi",
    "Bangladeş": "Asia/Dhaka",
    "Endonezya (Cakarta)": "Asia/Jakarta",
    "Tayland": "Asia/Bangkok",
    "Vietnam": "Asia/Ho_Chi_Minh",
    "Filipinler": "Asia/Manila",
    "Yeni Zelanda": "Pacific/Auckland",
    "Arjantin": "America/Argentina/Buenos_Aires",
    "Şili": "America/Santiago",
    "Kolombiya": "America/Bogota",
    "Peru": "America/Lima",
}

st.title("🕐 Dünya Saati")
st.markdown("Ülke seçerek o ülkedeki güncel saati görün.")

col1, col2 = st.columns([2, 1])

with col1:
    secilen_ulke = st.selectbox(
        "Ülke Seçin",
        options=list(ULKELER.keys()),
        index=0,
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    yenile = st.button("Yenile", use_container_width=True)

timezone_str = ULKELER[secilen_ulke]
tz = ZoneInfo(timezone_str)
simdi = datetime.now(tz)

tarih_str = simdi.strftime("%d %B %Y")
saat_str = simdi.strftime("%H:%M:%S")
gun_str = simdi.strftime("%A")

GUN_TR = {
    "Monday": "Pazartesi",
    "Tuesday": "Salı",
    "Wednesday": "Çarşamba",
    "Thursday": "Perşembe",
    "Friday": "Cuma",
    "Saturday": "Cumartesi",
    "Sunday": "Pazar",
}

AY_TR = {
    "January": "Ocak", "February": "Şubat", "March": "Mart",
    "April": "Nisan", "May": "Mayıs", "June": "Haziran",
    "July": "Temmuz", "August": "Ağustos", "September": "Eylül",
    "October": "Ekim", "November": "Kasım", "December": "Aralık",
}

gun_tr = GUN_TR.get(gun_str, gun_str)
for en, tr in AY_TR.items():
    tarih_str = tarih_str.replace(en, tr)

utc_offset = simdi.strftime("%z")
utc_str = f"UTC{utc_offset[:3]}:{utc_offset[3:]}" if utc_offset else ""

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
">
    <div style="color: #a0a0c0; font-size: 1.1rem; margin-bottom: 8px;">
        📍 {secilen_ulke}
    </div>
    <div style="color: #e0e0ff; font-size: 1rem; margin-bottom: 16px; opacity: 0.7;">
        {timezone_str} &nbsp;|&nbsp; {utc_str}
    </div>
    <div style="color: #00d4ff; font-size: 4rem; font-weight: bold; letter-spacing: 4px; font-family: monospace;">
        {saat_str}
    </div>
    <div style="color: #c0c0e0; font-size: 1.2rem; margin-top: 12px;">
        {gun_tr}, {tarih_str}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("Birden Fazla Ülkeyi Karşılaştır")

karsilastir = st.multiselect(
    "Karşılaştırmak istediğiniz ülkeleri seçin",
    options=list(ULKELER.keys()),
    default=["Türkiye", "İngiltere", "Japonya"],
)

if karsilastir:
    cols = st.columns(len(karsilastir))
    for idx, ulke in enumerate(karsilastir):
        tz_k = ZoneInfo(ULKELER[ulke])
        simdi_k = datetime.now(tz_k)
        saat_k = simdi_k.strftime("%H:%M")
        tarih_k = simdi_k.strftime("%d/%m/%Y")
        gun_k = GUN_TR.get(simdi_k.strftime("%A"), simdi_k.strftime("%A"))
        with cols[idx]:
            st.markdown(f"""
<div style="
    background: #1e1e3a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid #3a3a6a;
">
    <div style="color: #a0a0c0; font-size: 0.85rem; margin-bottom: 6px;">📍 {ulke}</div>
    <div style="color: #00d4ff; font-size: 2rem; font-weight: bold; font-family: monospace;">{saat_k}</div>
    <div style="color: #8080b0; font-size: 0.8rem; margin-top: 4px;">{gun_k}</div>
    <div style="color: #8080b0; font-size: 0.8rem;">{tarih_k}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; color: #606080; font-size: 0.8rem; margin-top: 20px;">
    Saati güncellemek için sayfayı yenileyin veya Yenile butonuna basın.
</div>
""", unsafe_allow_html=True)
