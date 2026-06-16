#!/usr/bin/env python3
"""
Teknik Servis Yönetim Sistemi
Streamlit tabanlı masaüstü/web uygulaması
"""

import streamlit as st
from teknik_servis_db import TeknikServisDB

# ─── SAYFA YAPISI ───────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Teknik Servis Yönetim Sistemi",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── STIL ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 10px;
        padding: 16px 20px;
        color: white;
        margin-bottom: 8px;
    }
    .metric-card .label { font-size: 13px; opacity: 0.85; }
    .metric-card .value { font-size: 28px; font-weight: bold; }
    .status-beklemede  { color: #f59e0b; font-weight: 600; }
    .status-devam      { color: #3b82f6; font-weight: 600; }
    .status-tamamlandi { color: #10b981; font-weight: 600; }
    .status-teslim     { color: #6366f1; font-weight: 600; }
    .status-odenmedi   { color: #ef4444; font-weight: 600; }
    .status-odendi     { color: #10b981; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─── VERİTABANI ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_db():
    return TeknikServisDB()

db = get_db()

# ─── YARDIMCİ ───────────────────────────────────────────────────────────────

DURUM_RENK = {
    "Beklemede": "status-beklemede",
    "Devam Ediyor": "status-devam",
    "Tamamlandı": "status-tamamlandi",
    "Teslim Edildi": "status-teslim",
}

def durum_badge(durum):
    cls = DURUM_RENK.get(durum, "")
    return f'<span class="{cls}">{durum}</span>'

def para_fmt(val):
    return f"₺{val:,.2f}"

# ─── SAYFALAR ───────────────────────────────────────────────────────────────

def sayfa_dashboard():
    st.header("Dashboard")
    s = db.istatistik()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Toplam Müşteri", s["toplam_musteri"])
        st.metric("Toplam Cihaz", s["toplam_cihaz"])
    with col2:
        st.metric("Beklemede", s["bekleyen"])
        st.metric("Devam Ediyor", s["devam_eden"])
    with col3:
        st.metric("Tamamlandı", s["tamamlanan"])
        st.metric("Teslim Edildi", s["teslim_edildi"])
    with col4:
        st.metric("Toplam Ciro", para_fmt(s["toplam_ciro"]))
        st.metric("Bekleyen Ödeme", para_fmt(s["bekleyen_odeme"]))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Son İş Emirleri")
        emirler = db.is_emirlerini_listele()[:8]
        if emirler:
            for ie in emirler:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    c1.write(f"**#{ie['id']}** {ie['musteri_adi']}")
                    c1.caption(ie['cihaz_adi'])
                    c2.markdown(durum_badge(ie['durum']), unsafe_allow_html=True)
                    c2.caption(ie.get('teknisyen') or "—")
                    c3.caption(ie['created_at'][:10])
        else:
            st.info("Henüz iş emri yok.")

    with col_b:
        st.subheader("Aylık Gelir")
        aylik = s["aylik_gelir"]
        if aylik:
            import pandas as pd
            df = pd.DataFrame(aylik, columns=["Ay", "Gelir (₺)"])
            df = df.sort_values("Ay")
            st.bar_chart(df.set_index("Ay"))
        else:
            st.info("Henüz ödeme kaydı yok.")


def sayfa_musteriler():
    st.header("Müşteri Yönetimi")
    tab1, tab2 = st.tabs(["Müşteri Listesi", "Yeni Müşteri"])

    with tab1:
        arama = st.text_input("Arama (ad, soyad, telefon)", placeholder="Arama yapın...")
        musteriler = db.musterileri_listele(arama)

        if musteriler:
            for m in musteriler:
                with st.expander(f"#{m['id']} — {m['ad']} {m['soyad']}  |  {m.get('telefon','')}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        a, s_v, t, e = st.columns(4)
                        with a:
                            yeni_ad = st.text_input("Ad", m['ad'], key=f"mad_{m['id']}")
                            yeni_soyad = st.text_input("Soyad", m['soyad'], key=f"msd_{m['id']}")
                        with s_v:
                            yeni_tel = st.text_input("Telefon", m.get('telefon',''), key=f"mtel_{m['id']}")
                            yeni_email = st.text_input("E-posta", m.get('email',''), key=f"meml_{m['id']}")
                        with t:
                            yeni_adres = st.text_area("Adres", m.get('adres',''), key=f"madr_{m['id']}", height=80)
                        with e:
                            st.write("")
                            st.write("")
                            if st.button("Kaydet", key=f"msave_{m['id']}"):
                                db.musteri_guncelle(m['id'], yeni_ad, yeni_soyad, yeni_tel, yeni_email, yeni_adres)
                                st.success("Güncellendi!")
                                st.rerun()
                    with col2:
                        st.write("")
                        cihazlar = db.cihazlari_listele(musteri_id=m['id'])
                        st.metric("Cihaz Sayısı", len(cihazlar))
                        emirler = db.is_emirlerini_listele(musteri_id=m['id'])
                        st.metric("İş Emri Sayısı", len(emirler))
                        if st.button("Müşteriyi Sil", key=f"mdel_{m['id']}", type="secondary"):
                            db.musteri_sil(m['id'])
                            st.warning("Müşteri silindi.")
                            st.rerun()
        else:
            st.info("Müşteri bulunamadı.")

    with tab2:
        with st.form("yeni_musteri_form"):
            col1, col2 = st.columns(2)
            ad = col1.text_input("Ad *")
            soyad = col2.text_input("Soyad *")
            tel = col1.text_input("Telefon")
            email = col2.text_input("E-posta")
            adres = st.text_area("Adres")
            if st.form_submit_button("Müşteri Ekle", type="primary"):
                if ad and soyad:
                    mid = db.musteri_ekle(ad, soyad, tel, email, adres)
                    st.success(f"Müşteri eklendi. (ID: {mid})")
                else:
                    st.error("Ad ve soyad zorunludur.")


def sayfa_cihazlar():
    st.header("Cihaz Yönetimi")
    tab1, tab2 = st.tabs(["Cihaz Listesi", "Yeni Cihaz"])

    with tab1:
        arama = st.text_input("Arama (marka, model, seri no)")
        cihazlar = db.cihazlari_listele(arama=arama)

        if cihazlar:
            for c in cihazlar:
                with st.expander(f"#{c['id']} — {c['marka']} {c['model']} | Müşteri: {c['musteri_adi']}", expanded=False):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        ca, cb, cc, cd = st.columns(4)
                        marka = ca.text_input("Marka", c['marka'], key=f"cmarka_{c['id']}")
                        model = cb.text_input("Model", c['model'], key=f"cmodel_{c['id']}")
                        seri = cc.text_input("Seri No", c.get('seri_no',''), key=f"cseri_{c['id']}")
                        tip = cd.text_input("Tip", c.get('tip',''), key=f"ctip_{c['id']}")
                        notlar = st.text_area("Notlar", c.get('notlar',''), key=f"cnot_{c['id']}", height=60)
                        if st.button("Kaydet", key=f"csave_{c['id']}"):
                            db.cihaz_guncelle(c['id'], marka, model, seri, tip, c.get('satin_alma_tarihi',''), notlar)
                            st.success("Güncellendi!")
                            st.rerun()
                    with col2:
                        st.caption(f"Eklenme: {c['created_at'][:10]}")
                        if st.button("Cihazı Sil", key=f"cdel_{c['id']}", type="secondary"):
                            db.cihaz_sil(c['id'])
                            st.warning("Cihaz silindi.")
                            st.rerun()
        else:
            st.info("Cihaz bulunamadı.")

    with tab2:
        musteriler = db.musterileri_listele()
        if not musteriler:
            st.warning("Önce bir müşteri ekleyin.")
            return
        with st.form("yeni_cihaz_form"):
            musteri_secim = st.selectbox(
                "Müşteri *",
                options=[(m['id'], f"{m['ad']} {m['soyad']}") for m in musteriler],
                format_func=lambda x: x[1]
            )
            col1, col2 = st.columns(2)
            marka = col1.text_input("Marka *")
            model = col2.text_input("Model *")
            seri = col1.text_input("Seri No")
            tip = col2.text_input("Tip (Laptop, Telefon, Tablet...)")
            satin = st.date_input("Satın Alma Tarihi", value=None)
            notlar = st.text_area("Notlar")
            if st.form_submit_button("Cihaz Ekle", type="primary"):
                if marka and model:
                    cid = db.cihaz_ekle(
                        musteri_secim[0], marka, model, seri, tip,
                        str(satin) if satin else "", notlar
                    )
                    st.success(f"Cihaz eklendi. (ID: {cid})")
                else:
                    st.error("Marka ve model zorunludur.")


def sayfa_is_emirleri():
    st.header("İş Emri Yönetimi")
    tab1, tab2 = st.tabs(["İş Emirleri", "Yeni İş Emri"])

    with tab1:
        col1, col2, col3 = st.columns([2, 2, 3])
        durum_filtre = col1.selectbox("Durum Filtresi", ["Tümü", "Beklemede", "Devam Ediyor", "Tamamlandı", "Teslim Edildi"])
        arama = col3.text_input("Arama (arıza, müşteri)")
        durum_param = None if durum_filtre == "Tümü" else durum_filtre

        emirler = db.is_emirlerini_listele(durum=durum_param, arama=arama)

        if emirler:
            for ie in emirler:
                renkli = durum_badge(ie['durum'])
                with st.expander(
                    f"#{ie['id']} — {ie['musteri_adi']} | {ie['cihaz_adi']} | {ie['durum']}",
                    expanded=False
                ):
                    c1, c2 = st.columns([4, 2])
                    with c1:
                        ariza = st.text_area("Arıza Tanımı", ie['ariza_tanimi'], key=f"iariza_{ie['id']}", height=80)
                        ia, ib = st.columns(2)
                        durum = ia.selectbox(
                            "Durum", ["Beklemede", "Devam Ediyor", "Tamamlandı", "Teslim Edildi"],
                            index=["Beklemede", "Devam Ediyor", "Tamamlandı", "Teslim Edildi"].index(ie['durum']),
                            key=f"idurum_{ie['id']}"
                        )
                        oncelik = ib.selectbox(
                            "Öncelik", ["Düşük", "Normal", "Yüksek", "Acil"],
                            index=["Düşük", "Normal", "Yüksek", "Acil"].index(ie.get('oncelik','Normal')),
                            key=f"ioncelik_{ie['id']}"
                        )
                        teknisyen = ia.text_input("Teknisyen", ie.get('teknisyen',''), key=f"itek_{ie['id']}")
                        tahmini = ib.text_input("Tahmini Teslim", ie.get('tahmini_teslim',''), key=f"itah_{ie['id']}")
                        notlar = st.text_area("Notlar", ie.get('notlar',''), key=f"inot_{ie['id']}", height=60)
                        if st.button("İş Emrini Kaydet", key=f"isave_{ie['id']}", type="primary"):
                            db.is_emri_guncelle(ie['id'], ariza, durum, teknisyen, oncelik, tahmini, notlar)
                            st.success("Güncellendi!")
                            st.rerun()

                    with c2:
                        st.markdown(f"**Durum:** {renkli}", unsafe_allow_html=True)
                        st.caption(f"Oluşturma: {ie['created_at'][:10]}")
                        if ie.get('tamamlanma_tarihi'):
                            st.caption(f"Tamamlanma: {ie['tamamlanma_tarihi'][:10]}")

                        st.divider()
                        st.write("**Kullanılan Parçalar**")
                        parcalar = db.parcalari_listele(ie['id'])
                        for p in parcalar:
                            pc1, pc2 = st.columns([3, 1])
                            pc1.caption(f"{p['parca_adi']} x{p['miktar']} = {para_fmt(p['miktar']*p['birim_fiyat'])}")
                            if pc2.button("X", key=f"pdel_{p['id']}"):
                                db.parca_sil(p['id'], ie['id'])
                                st.rerun()

                        with st.form(f"parca_form_{ie['id']}"):
                            pa, pb, pc = st.columns(3)
                            padi = pa.text_input("Parça Adı", key=f"padi_{ie['id']}")
                            pmik = pb.number_input("Miktar", 1.0, key=f"pmik_{ie['id']}", step=1.0)
                            pfiy = pc.number_input("Birim Fiyat (₺)", 0.0, key=f"pfiy_{ie['id']}", step=10.0)
                            if st.form_submit_button("Parça Ekle"):
                                if padi:
                                    db.parca_ekle(ie['id'], padi, pmik, pfiy)
                                    st.rerun()

                        st.divider()
                        fatura = db.fatura_getir(ie['id'])
                        if fatura:
                            st.caption(f"İşcilik: {para_fmt(fatura['iscilik_ucreti'])}")
                            st.caption(f"Parça: {para_fmt(fatura['parca_toplami'])}")
                            st.write(f"**Toplam: {para_fmt(fatura['toplam'])}**")
        else:
            st.info("İş emri bulunamadı.")

    with tab2:
        musteriler = db.musterileri_listele()
        if not musteriler:
            st.warning("Önce bir müşteri ekleyin.")
            return

        with st.form("yeni_is_emri_form"):
            musteri_secim = st.selectbox(
                "Müşteri *",
                options=[(m['id'], f"{m['ad']} {m['soyad']}") for m in musteriler],
                format_func=lambda x: x[1],
                key="ie_musteri"
            )

            # Müşteriye ait cihazları göster
            cihazlar_musteri = db.cihazlari_listele(musteri_id=musteri_secim[0]) if musteri_secim else []
            if not cihazlar_musteri:
                st.warning("Bu müşterinin cihazı yok. Önce cihaz ekleyin.")
                st.form_submit_button("İş Emri Oluştur", disabled=True)
                return

            cihaz_secim = st.selectbox(
                "Cihaz *",
                options=[(c['id'], f"{c['marka']} {c['model']} ({c.get('seri_no','')})") for c in cihazlar_musteri],
                format_func=lambda x: x[1]
            )
            ariza = st.text_area("Arıza Tanımı *", height=100)
            col1, col2 = st.columns(2)
            teknisyen = col1.text_input("Teknisyen")
            oncelik = col2.selectbox("Öncelik", ["Düşük", "Normal", "Yüksek", "Acil"], index=1)
            tahmini = col1.text_input("Tahmini Teslim Tarihi (gg.aa.yyyy)")
            notlar = st.text_area("Notlar", height=60)

            if st.form_submit_button("İş Emri Oluştur", type="primary"):
                if ariza:
                    iid = db.is_emri_ekle(
                        cihaz_secim[0], musteri_secim[0], ariza, teknisyen, oncelik, tahmini, notlar
                    )
                    st.success(f"İş emri oluşturuldu. (ID: {iid})")
                else:
                    st.error("Arıza tanımı zorunludur.")


def sayfa_faturalar():
    st.header("Fatura & Ödeme Yönetimi")
    tab1, tab2 = st.tabs(["Tüm Faturalar", "Fatura Düzenle"])

    with tab1:
        filtre = st.selectbox("Ödeme Durumu", ["Tümü", "Ödenmedi", "Kısmi Ödendi", "Ödendi"])
        filtre_param = None if filtre == "Tümü" else filtre
        faturalar = db.faturalari_listele(odeme_durumu=filtre_param)

        if faturalar:
            toplam_tutar = sum(f['toplam'] for f in faturalar)
            tahsil = sum(f['toplam'] for f in faturalar if f['odeme_durumu'] == 'Ödendi')
            col1, col2, col3 = st.columns(3)
            col1.metric("Fatura Sayısı", len(faturalar))
            col2.metric("Toplam Tutar", para_fmt(toplam_tutar))
            col3.metric("Tahsil Edilen", para_fmt(tahsil))

            st.divider()
            for f in faturalar:
                odeme_cls = "status-odendi" if f['odeme_durumu'] == "Ödendi" else "status-odenmedi"
                with st.expander(
                    f"Fatura #{f['id']} | İş Emri #{f['is_emri_id']} | {f['musteri_adi']} | {para_fmt(f['toplam'])}",
                    expanded=False
                ):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("İşçilik", para_fmt(f['iscilik_ucreti']))
                    c2.metric("Parça", para_fmt(f['parca_toplami']))
                    c3.metric("Toplam", para_fmt(f['toplam']))
                    st.markdown(f"**Ödeme Durumu:** <span class='{odeme_cls}'>{f['odeme_durumu']}</span>", unsafe_allow_html=True)
                    if f.get('odeme_tarihi'):
                        st.caption(f"Ödeme Tarihi: {f['odeme_tarihi'][:10]}")
                    if f.get('notlar'):
                        st.caption(f"Not: {f['notlar']}")
        else:
            st.info("Fatura bulunamadı.")

    with tab2:
        emirler = db.is_emirlerini_listele()
        if not emirler:
            st.info("İş emri yok.")
            return

        secim = st.selectbox(
            "İş Emri Seç",
            options=[(ie['id'], f"#{ie['id']} — {ie['musteri_adi']} | {ie['cihaz_adi']}") for ie in emirler],
            format_func=lambda x: x[1]
        )

        if secim:
            iid = secim[0]
            fatura = db.fatura_getir(iid)
            parcalar = db.parcalari_listele(iid)
            parca_top = sum(p['miktar'] * p['birim_fiyat'] for p in parcalar)

            with st.form("fatura_form"):
                iscilik = st.number_input(
                    "İşçilik Ücreti (₺)",
                    min_value=0.0,
                    value=float(fatura['iscilik_ucreti']) if fatura else 0.0,
                    step=50.0
                )
                st.info(f"Parça Toplamı: {para_fmt(parca_top)} | Genel Toplam: {para_fmt(iscilik + parca_top)}")
                odeme = st.selectbox(
                    "Ödeme Durumu",
                    ["Ödenmedi", "Kısmi Ödendi", "Ödendi"],
                    index=["Ödenmedi", "Kısmi Ödendi", "Ödendi"].index(fatura['odeme_durumu']) if fatura else 0
                )
                notlar = st.text_area("Notlar", fatura.get('notlar','') if fatura else "")
                if st.form_submit_button("Faturayı Kaydet", type="primary"):
                    db.fatura_guncelle(iid, iscilik, odeme, notlar)
                    st.success("Fatura güncellendi!")
                    st.rerun()


def sayfa_raporlar():
    st.header("Raporlar & İstatistikler")
    s = db.istatistik()

    # Özet
    st.subheader("Genel Özet")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Müşteri", s["toplam_musteri"])
        st.metric("Toplam Cihaz", s["toplam_cihaz"])
    with col2:
        toplam_is = s["bekleyen"] + s["devam_eden"] + s["tamamlanan"] + s["teslim_edildi"]
        st.metric("Toplam İş Emri", toplam_is)
        st.metric("Tamamlanan", s["tamamlanan"] + s["teslim_edildi"])
    with col3:
        st.metric("Toplam Ciro", para_fmt(s["toplam_ciro"]))
        st.metric("Tahsil Edilen", para_fmt(s["tahsil_edilen"]))
        st.metric("Bekleyen Ödeme", para_fmt(s["bekleyen_odeme"]))

    st.divider()

    # İş emri durum dağılımı
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("İş Emri Durum Dağılımı")
        import pandas as pd
        durum_data = {
            "Beklemede": s["bekleyen"],
            "Devam Ediyor": s["devam_eden"],
            "Tamamlandı": s["tamamlanan"],
            "Teslim Edildi": s["teslim_edildi"],
        }
        df_durum = pd.DataFrame(list(durum_data.items()), columns=["Durum", "Adet"])
        st.bar_chart(df_durum.set_index("Durum"))

    with col_b:
        st.subheader("Aylık Tahsil Edilen Gelir")
        aylik = s["aylik_gelir"]
        if aylik:
            df_gelir = pd.DataFrame(aylik, columns=["Ay", "Gelir (₺)"])
            df_gelir = df_gelir.sort_values("Ay")
            st.line_chart(df_gelir.set_index("Ay"))
        else:
            st.info("Henüz ödeme kaydı yok.")

    st.divider()

    # Teknisyen istatistikleri
    st.subheader("Teknisyen Bazlı İş Emri Sayısı")
    emirler = db.is_emirlerini_listele()
    if emirler:
        import pandas as pd
        from collections import Counter
        teknisyenler = [ie.get('teknisyen') or "Atanmamış" for ie in emirler]
        tek_sayac = Counter(teknisyenler)
        df_tek = pd.DataFrame(list(tek_sayac.items()), columns=["Teknisyen", "İş Emri"])
        df_tek = df_tek.sort_values("İş Emri", ascending=False)
        st.bar_chart(df_tek.set_index("Teknisyen"))
    else:
        st.info("İş emri bulunamadı.")


# ─── NAVİGASYON ─────────────────────────────────────────────────────────────

def main():
    with st.sidebar:
        st.title("🔧 Teknik Servis")
        st.divider()
        sayfa = st.radio(
            "Menü",
            ["Dashboard", "Müşteriler", "Cihazlar", "İş Emirleri", "Faturalar", "Raporlar"],
            label_visibility="collapsed"
        )
        st.divider()
        s = db.istatistik()
        st.caption(f"Bekleyen: **{s['bekleyen']}** iş emri")
        st.caption(f"Ödenmedi: **{para_fmt(s['bekleyen_odeme'])}**")

    if sayfa == "Dashboard":
        sayfa_dashboard()
    elif sayfa == "Müşteriler":
        sayfa_musteriler()
    elif sayfa == "Cihazlar":
        sayfa_cihazlar()
    elif sayfa == "İş Emirleri":
        sayfa_is_emirleri()
    elif sayfa == "Faturalar":
        sayfa_faturalar()
    elif sayfa == "Raporlar":
        sayfa_raporlar()


if __name__ == "__main__":
    main()
