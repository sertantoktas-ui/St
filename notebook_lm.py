#!/usr/bin/env python3
"""
NotebookLM Entegrasyonu - Claude API ile Belge Tabanlı AI Asistan
Google NotebookLM benzeri özellikler:
- Belge yükleme (TXT, PDF)
- Notebook oluşturma ve yönetme
- Kaynaklara dayalı soru-cevap
- Otomatik özet oluşturma
- Anahtar bilgiler çıkarma
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class NotebookLMService:
    """Claude API destekli NotebookLM servisi"""

    def __init__(self, db_path: str = "assistant.db"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.db_path = db_path
        self.model = "claude-opus-4-6"
        self._init_tables()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        """Notebook tablolarını oluştur"""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notebook_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notebook_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
            )
        """)

        conn.commit()
        conn.close()

    # ============ NOTEBOOK İŞLEMLERİ ============

    def create_notebook(self, name: str, description: str = "") -> int:
        """Yeni notebook oluştur"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notebooks (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        notebook_id = cursor.lastrowid
        conn.close()
        return notebook_id

    def list_notebooks(self) -> List[Dict]:
        """Tüm notebookları listele"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.id, n.name, n.description, n.created_at,
                   COUNT(s.id) as source_count
            FROM notebooks n
            LEFT JOIN notebook_sources s ON n.id = s.notebook_id
            GROUP BY n.id
            ORDER BY n.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "source_count": row[4]
            }
            for row in rows
        ]

    def delete_notebook(self, notebook_id: int) -> bool:
        """Notebook ve kaynaklarını sil"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notebook_sources WHERE notebook_id = ?", (notebook_id,))
        cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    # ============ KAYNAK İŞLEMLERİ ============

    def add_source(self, notebook_id: int, name: str, content: str, source_type: str = "text") -> int:
        """Notebooka belge/kaynak ekle"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notebook_sources (notebook_id, name, content, source_type)
            VALUES (?, ?, ?, ?)
        """, (notebook_id, name, content, source_type))
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        return source_id

    def get_sources(self, notebook_id: int) -> List[Dict]:
        """Notebookun kaynaklarını getir"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, content, source_type, created_at
            FROM notebook_sources
            WHERE notebook_id = ?
            ORDER BY created_at ASC
        """, (notebook_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "name": row[1],
                "content": row[2],
                "source_type": row[3],
                "created_at": row[4]
            }
            for row in rows
        ]

    def delete_source(self, source_id: int) -> bool:
        """Kaynak sil"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notebook_sources WHERE id = ?", (source_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def _build_context(self, notebook_id: int) -> str:
        """Notebook kaynaklarından bağlam metni oluştur"""
        sources = self.get_sources(notebook_id)
        if not sources:
            return ""

        context_parts = []
        for source in sources:
            context_parts.append(
                f"=== KAYNAK: {source['name']} ===\n{source['content']}\n"
            )
        return "\n".join(context_parts)

    # ============ AI İŞLEMLERİ ============

    def ask_question(self, notebook_id: int, question: str) -> str:
        """Kaynakları kullanarak soruyu yanıtla"""
        context = self._build_context(notebook_id)
        if not context:
            return "Bu notebookta henüz kaynak yok. Lütfen önce belge ekleyin."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system="""Sen bir belge analiz asistanısın. Kullanıcının sağladığı kaynak belgeler temel alınarak
soruları yanıtla. Yanıtlarında:
- Yalnızca kaynaklardaki bilgilere dayan
- Hangi kaynaktan bilgi aldığını belirt
- Kaynakta olmayan bilgi için "Bu bilgi kaynaklarda yer almıyor" de
- Türkçe yanıt ver""",
            messages=[
                {
                    "role": "user",
                    "content": f"KAYNAK BELGELER:\n\n{context}\n\nSORU: {question}"
                }
            ]
        )
        return response.content[0].text

    def generate_summary(self, notebook_id: int) -> str:
        """Tüm kaynakların özetini oluştur"""
        context = self._build_context(notebook_id)
        if not context:
            return "Özetlenecek kaynak bulunamadı."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system="""Sen bir içerik özetleme uzmanısın. Sağlanan belgeleri kapsamlı şekilde özetle.
Özet şunları içermeli:
- Ana konular ve temalar
- Önemli bilgiler ve bulgular
- Belgeler arası bağlantılar
Türkçe yaz, yapılandırılmış ve okunabilir bir format kullan.""",
            messages=[
                {
                    "role": "user",
                    "content": f"Aşağıdaki belgeleri özetle:\n\n{context}"
                }
            ]
        )
        return response.content[0].text

    def get_key_insights(self, notebook_id: int) -> str:
        """Kaynaklardan anahtar bilgiler çıkar"""
        context = self._build_context(notebook_id)
        if not context:
            return "Analiz edilecek kaynak bulunamadı."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system="""Sen bir analiz uzmanısın. Belgelerdeki en önemli bilgileri, kalıpları ve içgörüleri çıkar.
Çıktı formatı:
🔑 **Anahtar Bulgular**
- Madde madde en önemli noktalar

📊 **Önemli Veriler/İstatistikler** (varsa)
- Sayısal veriler ve istatistikler

💡 **Öneriler/Çıkarımlar**
- Belgelerden çıkarılabilecek sonuçlar

Türkçe yaz.""",
            messages=[
                {
                    "role": "user",
                    "content": f"Bu belgelerden anahtar bilgileri çıkar:\n\n{context}"
                }
            ]
        )
        return response.content[0].text

    def generate_faq(self, notebook_id: int) -> str:
        """Kaynaklardan sıkça sorulan sorular oluştur"""
        context = self._build_context(notebook_id)
        if not context:
            return "FAQ oluşturmak için kaynak bulunamadı."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system="""Belgeler hakkında 5-8 adet sıkça sorulan soru (FAQ) ve yanıtlarını oluştur.
Format:
**S: [Soru]**
C: [Yanıt]

Sorular belgeler hakkında en çok merak edilebilecek konuları kapsamalı.
Türkçe yaz.""",
            messages=[
                {
                    "role": "user",
                    "content": f"Bu belgeler için FAQ oluştur:\n\n{context}"
                }
            ]
        )
        return response.content[0].text

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """PDF'den metin çıkar"""
        try:
            import PyPDF2
            import io
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
        except ImportError:
            return "[PyPDF2 yüklü değil. pip install PyPDF2 çalıştırın]"
        except Exception as e:
            return f"[PDF okuma hatası: {str(e)}]"
