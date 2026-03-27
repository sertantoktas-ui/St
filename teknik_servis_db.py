#!/usr/bin/env python3
"""
Teknik Servis Yönetim Sistemi - Veritabanı Katmanı
SQLite tabanlı: Müşteri, Cihaz, İş Emri, Parça, Fatura
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class TeknikServisDB:
    def __init__(self, db_path: str = "teknik_servis.db"):
        self.db_path = db_path
        self.init_database()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        conn = self._conn()
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                telefon TEXT,
                email TEXT,
                adres TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime'))
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS cihazlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER NOT NULL,
                marka TEXT NOT NULL,
                model TEXT NOT NULL,
                seri_no TEXT,
                tip TEXT,
                satin_alma_tarihi TEXT,
                notlar TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (musteri_id) REFERENCES musteriler(id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS is_emirleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cihaz_id INTEGER NOT NULL,
                musteri_id INTEGER NOT NULL,
                ariza_tanimi TEXT NOT NULL,
                durum TEXT DEFAULT 'Beklemede',
                teknisyen TEXT,
                oncelik TEXT DEFAULT 'Normal',
                tahmini_teslim TEXT,
                tamamlanma_tarihi TEXT,
                notlar TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (cihaz_id) REFERENCES cihazlar(id),
                FOREIGN KEY (musteri_id) REFERENCES musteriler(id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS parcalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_emri_id INTEGER NOT NULL,
                parca_adi TEXT NOT NULL,
                miktar REAL DEFAULT 1,
                birim_fiyat REAL DEFAULT 0,
                FOREIGN KEY (is_emri_id) REFERENCES is_emirleri(id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS faturalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_emri_id INTEGER NOT NULL UNIQUE,
                iscilik_ucreti REAL DEFAULT 0,
                parca_toplami REAL DEFAULT 0,
                toplam REAL DEFAULT 0,
                odeme_durumu TEXT DEFAULT 'Ödenmedi',
                odeme_tarihi TEXT,
                notlar TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (is_emri_id) REFERENCES is_emirleri(id)
            )
        """)

        conn.commit()
        conn.close()

    # ─── MÜŞTERİ ───────────────────────────────────────────────

    def musteri_ekle(self, ad, soyad, telefon="", email="", adres="") -> int:
        conn = self._conn()
        c = conn.cursor()
        c.execute(
            "INSERT INTO musteriler (ad, soyad, telefon, email, adres) VALUES (?,?,?,?,?)",
            (ad, soyad, telefon, email, adres)
        )
        conn.commit()
        mid = c.lastrowid
        conn.close()
        return mid

    def musteri_guncelle(self, mid, ad, soyad, telefon, email, adres):
        conn = self._conn()
        conn.execute(
            "UPDATE musteriler SET ad=?,soyad=?,telefon=?,email=?,adres=? WHERE id=?",
            (ad, soyad, telefon, email, adres, mid)
        )
        conn.commit()
        conn.close()

    def musteri_sil(self, mid):
        conn = self._conn()
        conn.execute("DELETE FROM musteriler WHERE id=?", (mid,))
        conn.commit()
        conn.close()

    def musterileri_listele(self, arama="") -> List[Dict]:
        conn = self._conn()
        if arama:
            rows = conn.execute(
                "SELECT * FROM musteriler WHERE ad||' '||soyad LIKE ? OR telefon LIKE ? ORDER BY ad",
                (f"%{arama}%", f"%{arama}%")
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM musteriler ORDER BY ad").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def musteri_getir(self, mid) -> Optional[Dict]:
        conn = self._conn()
        row = conn.execute("SELECT * FROM musteriler WHERE id=?", (mid,)).fetchone()
        conn.close()
        return dict(row) if row else None

    # ─── CİHAZ ─────────────────────────────────────────────────

    def cihaz_ekle(self, musteri_id, marka, model, seri_no="", tip="", satin_alma_tarihi="", notlar="") -> int:
        conn = self._conn()
        c = conn.cursor()
        c.execute(
            "INSERT INTO cihazlar (musteri_id, marka, model, seri_no, tip, satin_alma_tarihi, notlar) VALUES (?,?,?,?,?,?,?)",
            (musteri_id, marka, model, seri_no, tip, satin_alma_tarihi, notlar)
        )
        conn.commit()
        cid = c.lastrowid
        conn.close()
        return cid

    def cihaz_guncelle(self, cid, marka, model, seri_no, tip, satin_alma_tarihi, notlar):
        conn = self._conn()
        conn.execute(
            "UPDATE cihazlar SET marka=?,model=?,seri_no=?,tip=?,satin_alma_tarihi=?,notlar=? WHERE id=?",
            (marka, model, seri_no, tip, satin_alma_tarihi, notlar, cid)
        )
        conn.commit()
        conn.close()

    def cihaz_sil(self, cid):
        conn = self._conn()
        conn.execute("DELETE FROM cihazlar WHERE id=?", (cid,))
        conn.commit()
        conn.close()

    def cihazlari_listele(self, musteri_id=None, arama="") -> List[Dict]:
        conn = self._conn()
        if musteri_id:
            rows = conn.execute(
                """SELECT c.*, m.ad||' '||m.soyad AS musteri_adi
                   FROM cihazlar c JOIN musteriler m ON c.musteri_id=m.id
                   WHERE c.musteri_id=? ORDER BY c.marka""",
                (musteri_id,)
            ).fetchall()
        elif arama:
            rows = conn.execute(
                """SELECT c.*, m.ad||' '||m.soyad AS musteri_adi
                   FROM cihazlar c JOIN musteriler m ON c.musteri_id=m.id
                   WHERE c.marka||' '||c.model LIKE ? OR c.seri_no LIKE ?
                   ORDER BY c.marka""",
                (f"%{arama}%", f"%{arama}%")
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT c.*, m.ad||' '||m.soyad AS musteri_adi
                   FROM cihazlar c JOIN musteriler m ON c.musteri_id=m.id
                   ORDER BY c.marka"""
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── İŞ EMRİ ───────────────────────────────────────────────

    def is_emri_ekle(self, cihaz_id, musteri_id, ariza_tanimi, teknisyen="", oncelik="Normal", tahmini_teslim="", notlar="") -> int:
        conn = self._conn()
        c = conn.cursor()
        c.execute(
            """INSERT INTO is_emirleri
               (cihaz_id, musteri_id, ariza_tanimi, teknisyen, oncelik, tahmini_teslim, notlar)
               VALUES (?,?,?,?,?,?,?)""",
            (cihaz_id, musteri_id, ariza_tanimi, teknisyen, oncelik, tahmini_teslim, notlar)
        )
        conn.commit()
        iid = c.lastrowid
        conn.close()
        return iid

    def is_emri_guncelle(self, iid, ariza_tanimi, durum, teknisyen, oncelik, tahmini_teslim, notlar):
        conn = self._conn()
        tamamlanma = datetime.now().strftime("%Y-%m-%d %H:%M") if durum == "Tamamlandı" else None
        conn.execute(
            """UPDATE is_emirleri
               SET ariza_tanimi=?,durum=?,teknisyen=?,oncelik=?,tahmini_teslim=?,notlar=?,
                   tamamlanma_tarihi=COALESCE(tamamlanma_tarihi,?)
               WHERE id=?""",
            (ariza_tanimi, durum, teknisyen, oncelik, tahmini_teslim, notlar, tamamlanma, iid)
        )
        conn.commit()
        conn.close()

    def is_emirlerini_listele(self, durum=None, musteri_id=None, arama="", teknisyen=None) -> List[Dict]:
        conn = self._conn()
        base = """
            SELECT ie.*, m.ad||' '||m.soyad AS musteri_adi,
                   c.marka||' '||c.model AS cihaz_adi
            FROM is_emirleri ie
            JOIN musteriler m ON ie.musteri_id=m.id
            JOIN cihazlar c ON ie.cihaz_id=c.id
        """
        where, params = [], []
        if durum:
            where.append("ie.durum=?")
            params.append(durum)
        if musteri_id:
            where.append("ie.musteri_id=?")
            params.append(musteri_id)
        if arama:
            where.append("(ie.ariza_tanimi LIKE ? OR m.ad||' '||m.soyad LIKE ?)")
            params += [f"%{arama}%", f"%{arama}%"]
        if teknisyen == "Atanmamış":
            where.append("(ie.teknisyen IS NULL OR ie.teknisyen='')")
        elif teknisyen:
            where.append("ie.teknisyen=?")
            params.append(teknisyen)
        if where:
            base += " WHERE " + " AND ".join(where)
        base += " ORDER BY ie.created_at DESC"
        rows = conn.execute(base, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def teknisyenleri_listele(self) -> List[str]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT DISTINCT teknisyen FROM is_emirleri WHERE teknisyen IS NOT NULL AND teknisyen != '' ORDER BY teknisyen"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]

    def is_emri_getir(self, iid) -> Optional[Dict]:
        conn = self._conn()
        row = conn.execute(
            """SELECT ie.*, m.ad||' '||m.soyad AS musteri_adi,
                      c.marka||' '||c.model AS cihaz_adi
               FROM is_emirleri ie
               JOIN musteriler m ON ie.musteri_id=m.id
               JOIN cihazlar c ON ie.cihaz_id=c.id
               WHERE ie.id=?""",
            (iid,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    # ─── PARÇA ─────────────────────────────────────────────────

    def parca_ekle(self, is_emri_id, parca_adi, miktar, birim_fiyat) -> int:
        conn = self._conn()
        c = conn.cursor()
        c.execute(
            "INSERT INTO parcalar (is_emri_id, parca_adi, miktar, birim_fiyat) VALUES (?,?,?,?)",
            (is_emri_id, parca_adi, miktar, birim_fiyat)
        )
        conn.commit()
        pid = c.lastrowid
        conn.close()
        self._fatura_parca_guncelle(is_emri_id)
        return pid

    def parca_sil(self, pid, is_emri_id):
        conn = self._conn()
        conn.execute("DELETE FROM parcalar WHERE id=?", (pid,))
        conn.commit()
        conn.close()
        self._fatura_parca_guncelle(is_emri_id)

    def parcalari_listele(self, is_emri_id) -> List[Dict]:
        conn = self._conn()
        rows = conn.execute(
            "SELECT * FROM parcalar WHERE is_emri_id=?", (is_emri_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── FATURA ────────────────────────────────────────────────

    def _fatura_parca_guncelle(self, is_emri_id):
        """Parça toplamını faturaya yansıt"""
        conn = self._conn()
        row = conn.execute(
            "SELECT SUM(miktar*birim_fiyat) FROM parcalar WHERE is_emri_id=?",
            (is_emri_id,)
        ).fetchone()
        parca_top = row[0] or 0

        existing = conn.execute(
            "SELECT id, iscilik_ucreti FROM faturalar WHERE is_emri_id=?", (is_emri_id,)
        ).fetchone()
        if existing:
            iscilik = existing[1] or 0
            conn.execute(
                "UPDATE faturalar SET parca_toplami=?,toplam=? WHERE is_emri_id=?",
                (parca_top, iscilik + parca_top, is_emri_id)
            )
        else:
            conn.execute(
                "INSERT INTO faturalar (is_emri_id, parca_toplami, toplam) VALUES (?,?,?)",
                (is_emri_id, parca_top, parca_top)
            )
        conn.commit()
        conn.close()

    def fatura_guncelle(self, is_emri_id, iscilik_ucreti, odeme_durumu, notlar=""):
        conn = self._conn()
        existing = conn.execute(
            "SELECT id, parca_toplami FROM faturalar WHERE is_emri_id=?", (is_emri_id,)
        ).fetchone()
        parca_top = existing[1] if existing else 0
        toplam = iscilik_ucreti + parca_top
        odeme_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M") if odeme_durumu == "Ödendi" else None
        if existing:
            conn.execute(
                """UPDATE faturalar
                   SET iscilik_ucreti=?,toplam=?,odeme_durumu=?,
                       odeme_tarihi=COALESCE(odeme_tarihi,?),notlar=?
                   WHERE is_emri_id=?""",
                (iscilik_ucreti, toplam, odeme_durumu, odeme_tarihi, notlar, is_emri_id)
            )
        else:
            conn.execute(
                """INSERT INTO faturalar
                   (is_emri_id,iscilik_ucreti,parca_toplami,toplam,odeme_durumu,odeme_tarihi,notlar)
                   VALUES (?,?,?,?,?,?,?)""",
                (is_emri_id, iscilik_ucreti, 0, toplam, odeme_durumu, odeme_tarihi, notlar)
            )
        conn.commit()
        conn.close()

    def fatura_getir(self, is_emri_id) -> Optional[Dict]:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM faturalar WHERE is_emri_id=?", (is_emri_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def faturalari_listele(self, odeme_durumu=None) -> List[Dict]:
        conn = self._conn()
        base = """
            SELECT f.*, ie.ariza_tanimi, m.ad||' '||m.soyad AS musteri_adi
            FROM faturalar f
            JOIN is_emirleri ie ON f.is_emri_id=ie.id
            JOIN musteriler m ON ie.musteri_id=m.id
        """
        if odeme_durumu:
            rows = conn.execute(base + " WHERE f.odeme_durumu=? ORDER BY f.created_at DESC", (odeme_durumu,)).fetchall()
        else:
            rows = conn.execute(base + " ORDER BY f.created_at DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── İSTATİSTİK ────────────────────────────────────────────

    def istatistik(self) -> Dict:
        conn = self._conn()
        stats = {}
        stats["toplam_musteri"] = conn.execute("SELECT COUNT(*) FROM musteriler").fetchone()[0]
        stats["toplam_cihaz"] = conn.execute("SELECT COUNT(*) FROM cihazlar").fetchone()[0]
        stats["bekleyen"] = conn.execute("SELECT COUNT(*) FROM is_emirleri WHERE durum='Beklemede'").fetchone()[0]
        stats["devam_eden"] = conn.execute("SELECT COUNT(*) FROM is_emirleri WHERE durum='Devam Ediyor'").fetchone()[0]
        stats["tamamlanan"] = conn.execute("SELECT COUNT(*) FROM is_emirleri WHERE durum='Tamamlandı'").fetchone()[0]
        stats["teslim_edildi"] = conn.execute("SELECT COUNT(*) FROM is_emirleri WHERE durum='Teslim Edildi'").fetchone()[0]
        r = conn.execute("SELECT COALESCE(SUM(toplam),0) FROM faturalar").fetchone()[0]
        stats["toplam_ciro"] = r
        r2 = conn.execute("SELECT COALESCE(SUM(toplam),0) FROM faturalar WHERE odeme_durumu='Ödendi'").fetchone()[0]
        stats["tahsil_edilen"] = r2
        stats["bekleyen_odeme"] = stats["toplam_ciro"] - stats["tahsil_edilen"]
        # Son 30 gün aylık gelir
        rows = conn.execute(
            """SELECT strftime('%Y-%m',created_at) AS ay, COALESCE(SUM(toplam),0)
               FROM faturalar WHERE odeme_durumu='Ödendi'
               GROUP BY ay ORDER BY ay DESC LIMIT 12"""
        ).fetchall()
        stats["aylik_gelir"] = [(r[0], r[1]) for r in rows]
        conn.close()
        return stats
