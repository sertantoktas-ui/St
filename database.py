#!/usr/bin/env python3
"""
SQLite Database Management für Kişisel Asistan
Veritabanı işlemleri: Görevler, Emailler, Raporlar
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class AssistantDatabase:
    """Asistan için veritabanı yönetimi"""

    def __init__(self, db_path: str = "assistant.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Veritabanı bağlantısı al"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Veritabanını başlat ve tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Görevler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                priority TEXT DEFAULT 'medium'
            )
        """)

        # Emailler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                tone TEXT DEFAULT 'formal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent INTEGER DEFAULT 0,
                sent_at TIMESTAMP
            )
        """)

        # Raporlar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                format TEXT DEFAULT 'markdown',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT
            )
        """)

        # Arama geçmişi tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # ============ GÖREV İŞLEMLERİ ============

    def add_task(self, title: str, description: str = "", priority: str = "medium") -> int:
        """Yeni görev ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, priority)
            VALUES (?, ?, ?)
        """, (title, description, priority))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id

    def get_tasks(self, status: str = "pending") -> List[Dict]:
        """Görevleri listele"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, status, priority, created_at
            FROM tasks
            WHERE status = ?
            ORDER BY created_at DESC
        """, (status,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

    def complete_task(self, task_id: int) -> bool:
        """Görev tamamla"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_task(self, task_id: int) -> bool:
        """Görev sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    # ============ EMAIL İŞLEMLERİ ============

    def save_email(self, recipient: str, subject: str, body: str, tone: str = "formal") -> int:
        """Email kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emails (recipient, subject, body, tone)
            VALUES (?, ?, ?, ?)
        """, (recipient, subject, body, tone))
        conn.commit()
        email_id = cursor.lastrowid
        conn.close()
        return email_id

    def get_emails(self, sent_only: bool = False) -> List[Dict]:
        """Emailleri listele"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT id, recipient, subject, body, tone, created_at, sent FROM emails"
        if sent_only:
            query += " WHERE sent = 1"
        query += " ORDER BY created_at DESC"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "recipient": row[1],
                "subject": row[2],
                "body": row[3],
                "tone": row[4],
                "created_at": row[5],
                "sent": bool(row[6])
            }
            for row in rows
        ]

    def mark_email_sent(self, email_id: int) -> bool:
        """Emaili gönderildi olarak işaretle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emails
            SET sent = 1, sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (email_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    # ============ RAPOR İŞLEMLERİ ============

    def save_report(self, title: str, content: str, format_type: str = "markdown", file_path: str = None) -> int:
        """Rapor kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (title, content, format, file_path)
            VALUES (?, ?, ?, ?)
        """, (title, content, format_type, file_path))
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    def get_reports(self) -> List[Dict]:
        """Raporları listele"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, format, created_at, file_path
            FROM reports
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "title": row[1],
                "format": row[2],
                "created_at": row[3],
                "file_path": row[4]
            }
            for row in rows
        ]

    # ============ ARAMA GEÇMİŞİ ============

    def save_search(self, query: str, results: str) -> int:
        """Arama geçmişini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO search_history (query, results)
            VALUES (?, ?)
        """, (query, results))
        conn.commit()
        search_id = cursor.lastrowid
        conn.close()
        return search_id

    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """Arama geçmişini al"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, query, created_at
            FROM search_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "query": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

    # ============ İSTATİSTİKLER ============

    def get_statistics(self) -> Dict:
        """İstatistikleri al"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Görev istatistikleri
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending_tasks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()[0]

        # Email istatistikleri
        cursor.execute("SELECT COUNT(*) FROM emails WHERE sent = 0")
        unsent_emails = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emails WHERE sent = 1")
        sent_emails = cursor.fetchone()[0]

        # Rapor sayısı
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]

        conn.close()

        return {
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "unsent_emails": unsent_emails,
            "sent_emails": sent_emails,
            "total_reports": total_reports
        }

if __name__ == "__main__":
    # Test
    db = AssistantDatabase()
    print("✅ Veritabanı başarıyla başlatıldı!")

    # Test: Görev ekle
    task_id = db.add_task("Test görevi", "Bu bir test görevidir", "high")
    print(f"✅ Görev eklendi: ID={task_id}")

    # Test: Görevleri listele
    tasks = db.get_tasks()
    print(f"📋 Görevler: {len(tasks)} adet")

    # İstatistikler
    stats = db.get_statistics()
    print(f"📊 İstatistikler: {stats}")
