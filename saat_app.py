import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Dünya Saati",
    page_icon="🕐",
    layout="centered",
)

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

secilen_ulke = st.selectbox(
    "Ülke Seçin",
    options=list(ULKELER.keys()),
    index=0,
)

timezone_str = ULKELER[secilen_ulke]

# Canlı saat — JavaScript ile her saniye güncellenir
saat_html = f"""
<div style="
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    font-family: sans-serif;
">
    <div style="color: #a0a0c0; font-size: 1.1rem; margin-bottom: 6px;">
        📍 {secilen_ulke}
    </div>
    <div id="utc-label" style="color: #e0e0ff; font-size: 0.9rem; margin-bottom: 16px; opacity: 0.6;"></div>
    <div id="saat" style="color: #00d4ff; font-size: 4rem; font-weight: bold; letter-spacing: 6px; font-family: monospace;">
        --:--:--
    </div>
    <div id="tarih" style="color: #c0c0e0; font-size: 1.1rem; margin-top: 14px;">
        &nbsp;
    </div>
</div>

<script>
const tz = "{timezone_str}";

const GUNLER = ["Pazar","Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi"];
const AYLAR = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran",
               "Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"];

function guncelle() {{
    const simdi = new Date();

    const saatFmt = new Intl.DateTimeFormat("tr-TR", {{
        timeZone: tz,
        hour: "2-digit", minute: "2-digit", second: "2-digit",
        hour12: false
    }});
    const tarihFmt = new Intl.DateTimeFormat("tr-TR", {{
        timeZone: tz,
        weekday: "long", day: "numeric", month: "long", year: "numeric"
    }});
    const offsetFmt = new Intl.DateTimeFormat("en", {{
        timeZone: tz,
        timeZoneName: "shortOffset"
    }});

    document.getElementById("saat").textContent = saatFmt.format(simdi);
    document.getElementById("tarih").textContent = tarihFmt.format(simdi);

    // UTC offset
    const parts = offsetFmt.formatToParts(simdi);
    const tzName = parts.find(p => p.type === "timeZoneName");
    document.getElementById("utc-label").textContent = tz + (tzName ? "  |  " + tzName.value : "");
}}

guncelle();
setInterval(guncelle, 1000);
</script>
"""

components.html(saat_html, height=240)

# Karşılaştırma bölümü
st.markdown("---")
st.subheader("Birden Fazla Ülkeyi Karşılaştır")

karsilastir = st.multiselect(
    "Ülke seçin",
    options=list(ULKELER.keys()),
    default=["Türkiye", "İngiltere", "Japonya"],
)

if karsilastir:
    kart_js = ""
    for ulke in karsilastir:
        tz_k = ULKELER[ulke]
        kart_js += f"""
        {{
            label: "{ulke}",
            tz: "{tz_k}"
        }},"""

    karsilastir_html = f"""
<style>
  .kart-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
  }}
  .kart {{
    background: #1e1e3a;
    border: 1px solid #3a3a6a;
    border-radius: 12px;
    padding: 18px 24px;
    text-align: center;
    min-width: 130px;
    font-family: sans-serif;
  }}
  .kart-ulke {{ color: #a0a0c0; font-size: 0.82rem; margin-bottom: 8px; }}
  .kart-saat {{ color: #00d4ff; font-size: 1.8rem; font-weight: bold; font-family: monospace; }}
  .kart-tarih {{ color: #8080b0; font-size: 0.75rem; margin-top: 6px; }}
</style>

<div class="kart-grid" id="kart-grid"></div>

<script>
const ulkeler = [{kart_js}];

const GUNLER_TR = ["Paz","Pzt","Sal","Çar","Per","Cum","Cmt"];

function kartlariGuncelle() {{
    const grid = document.getElementById("kart-grid");
    if (!grid) return;

    ulkeler.forEach((u, i) => {{
        const simdi = new Date();
        const saatFmt = new Intl.DateTimeFormat("tr-TR", {{
            timeZone: u.tz, hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false
        }});
        const tarihFmt = new Intl.DateTimeFormat("tr-TR", {{
            timeZone: u.tz, day: "2-digit", month: "2-digit", year: "numeric"
        }});
        const gunFmt = new Intl.DateTimeFormat("tr-TR", {{
            timeZone: u.tz, weekday: "short"
        }});

        let kart = document.getElementById("kart-" + i);
        if (!kart) {{
            kart = document.createElement("div");
            kart.className = "kart";
            kart.id = "kart-" + i;
            kart.innerHTML = `
                <div class="kart-ulke">📍 ${{u.label}}</div>
                <div class="kart-saat" id="ks-${{i}}">--:--</div>
                <div class="kart-tarih" id="kt-${{i}}">&nbsp;</div>
            `;
            grid.appendChild(kart);
        }}
        document.getElementById("ks-" + i).textContent = saatFmt.format(simdi);
        document.getElementById("kt-" + i).textContent =
            gunFmt.format(simdi) + "  " + tarihFmt.format(simdi);
    }});
}}

kartlariGuncelle();
setInterval(kartlariGuncelle, 1000);
</script>
"""
    components.html(karsilastir_html, height=max(160, 80 + (len(karsilastir) // 4 + 1) * 140))
