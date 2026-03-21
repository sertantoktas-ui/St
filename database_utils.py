#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for database operations
Veritabanı işlemleri için yardımcı fonksiyonlar
"""

import sqlite3
import csv
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "service_tracking.db"


class ServiceDatabase:
    """Database management utility class"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def backup_database(self):
        """Create a backup of the database"""
        backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            print(f"✓ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return None

    def export_service_requests_to_csv(self, output_file="service_requests.csv"):
        """Export service requests to CSV file"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''SELECT sr.id, c.name, sr.description, sr.priority, sr.status,
                                sr.created_date, sr.scheduled_date, sr.completed_date,
                                t.name, sr.notes
                         FROM service_requests sr
                         LEFT JOIN customers c ON sr.customer_id = c.id
                         LEFT JOIN technicians t ON sr.technician_id = t.id
                         ORDER BY sr.id DESC''')

            rows = c.fetchall()
            conn.close()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Müşteri', 'Açıklama', 'Öncelik', 'Durum',
                               'Oluşturulma Tarihi', 'Planlanan Tarih', 'Tamamlanma Tarihi',
                               'Teknisyen', 'Notlar'])
                writer.writerows(rows)

            print(f"✓ Exported to: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False

    def export_customers_to_csv(self, output_file="customers.csv"):
        """Export customers to CSV file"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('SELECT id, name, phone, email, address FROM customers ORDER BY id')
            rows = c.fetchall()
            conn.close()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ad Soyad', 'Telefon', 'Email', 'Adres'])
                writer.writerows(rows)

            print(f"✓ Exported to: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False

    def export_technicians_to_csv(self, output_file="technicians.csv"):
        """Export technicians to CSV file"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('SELECT id, name, phone, specialty, status FROM technicians ORDER BY id')
            rows = c.fetchall()
            conn.close()

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ad Soyad', 'Telefon', 'Uzmanlık', 'Durum'])
                writer.writerows(rows)

            print(f"✓ Exported to: {output_file}")
            return True
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False

    def get_statistics(self):
        """Get comprehensive statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Service request statistics
            c.execute('SELECT COUNT(*) FROM service_requests')
            total_requests = c.fetchone()[0]

            c.execute('SELECT COUNT(*) FROM service_requests WHERE status = ?', ("Tamamlandı",))
            completed = c.fetchone()[0]

            c.execute('SELECT COUNT(*) FROM service_requests WHERE status = ?', ("Açık",))
            open_requests = c.fetchone()[0]

            c.execute('SELECT COUNT(*) FROM service_requests WHERE priority = ?', ("Acil",))
            urgent = c.fetchone()[0]

            # Customer statistics
            c.execute('SELECT COUNT(*) FROM customers')
            customers_count = c.fetchone()[0]

            # Technician statistics
            c.execute('SELECT COUNT(*) FROM technicians')
            technicians_count = c.fetchone()[0]

            c.execute('SELECT COUNT(*) FROM technicians WHERE status = ?', ("Aktif",))
            active_technicians = c.fetchone()[0]

            conn.close()

            completion_rate = (completed / total_requests * 100) if total_requests > 0 else 0

            stats = {
                'total_requests': total_requests,
                'completed_requests': completed,
                'open_requests': open_requests,
                'urgent_requests': urgent,
                'completion_rate': round(completion_rate, 2),
                'total_customers': customers_count,
                'total_technicians': technicians_count,
                'active_technicians': active_technicians
            }

            return stats
        except Exception as e:
            print(f"✗ Statistics retrieval failed: {e}")
            return None

    def print_statistics(self):
        """Print statistics in a formatted way"""
        stats = self.get_statistics()
        if stats:
            print("\n" + "="*50)
            print("           İSTATİSTİKLER")
            print("="*50)
            print(f"Toplam Servis Talepleri: {stats['total_requests']}")
            print(f"  ├─ Tamamlanan: {stats['completed_requests']}")
            print(f"  ├─ Açık: {stats['open_requests']}")
            print(f"  └─ Acil: {stats['urgent_requests']}")
            print(f"\nTamamlanma Oranı: {stats['completion_rate']}%")
            print(f"\nMüşteri Sayısı: {stats['total_customers']}")
            print(f"Teknisyen Sayısı: {stats['total_technicians']}")
            print(f"Aktif Teknisyen: {stats['active_technicians']}")
            print("="*50 + "\n")

    def get_service_request_by_id(self, request_id):
        """Get detailed information about a service request"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''SELECT sr.id, c.name, c.phone, sr.description, sr.priority,
                                sr.status, sr.created_date, sr.scheduled_date,
                                sr.completed_date, t.name, sr.notes
                         FROM service_requests sr
                         LEFT JOIN customers c ON sr.customer_id = c.id
                         LEFT JOIN technicians t ON sr.technician_id = t.id
                         WHERE sr.id = ?''', (request_id,))

            result = c.fetchone()
            conn.close()

            if result:
                return {
                    'id': result[0],
                    'customer_name': result[1],
                    'customer_phone': result[2],
                    'description': result[3],
                    'priority': result[4],
                    'status': result[5],
                    'created_date': result[6],
                    'scheduled_date': result[7],
                    'completed_date': result[8],
                    'technician_name': result[9],
                    'notes': result[10]
                }
            return None
        except Exception as e:
            print(f"✗ Failed to retrieve request: {e}")
            return None

    def get_technician_workload(self):
        """Get workload statistics for each technician"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''SELECT t.id, t.name, COUNT(sr.id) as assigned_requests,
                                SUM(CASE WHEN sr.status = 'Tamamlandı' THEN 1 ELSE 0 END) as completed
                         FROM technicians t
                         LEFT JOIN service_requests sr ON sr.technician_id = t.id
                         GROUP BY t.id, t.name
                         ORDER BY assigned_requests DESC''')

            results = c.fetchall()
            conn.close()

            print("\n" + "="*60)
            print("           TEKNİSYEN İŞ YÜKÜNDEMİ")
            print("="*60)
            print(f"{'Ad':<20} {'Atanan':<15} {'Tamamlanan':<15}")
            print("-"*60)

            for row in results:
                name = row[1] or "Atanmamış"
                assigned = row[2] or 0
                completed = row[3] or 0
                print(f"{name:<20} {assigned:<15} {completed:<15}")

            print("="*60 + "\n")
            return results
        except Exception as e:
            print(f"✗ Failed to retrieve workload: {e}")
            return None


def main():
    """Command line interface for database utilities"""
    db = ServiceDatabase()

    print("\n" + "="*50)
    print("  Teknik Servis Takip - Veritabanı Araçları")
    print("="*50)
    print("\n1. Yedek Oluştur")
    print("2. İstatistikleri Görüntüle")
    print("3. Servis Taleplerini CSV'ye Aktar")
    print("4. Müşterileri CSV'ye Aktar")
    print("5. Teknisyenleri CSV'ye Aktar")
    print("6. Teknisyen İş Yükünü Görüntüle")
    print("0. Çıkış")

    choice = input("\nSeçiminiz: ")

    if choice == "1":
        db.backup_database()
    elif choice == "2":
        db.print_statistics()
    elif choice == "3":
        db.export_service_requests_to_csv()
    elif choice == "4":
        db.export_customers_to_csv()
    elif choice == "5":
        db.export_technicians_to_csv()
    elif choice == "6":
        db.get_technician_workload()
    elif choice == "0":
        print("Çıkılıyor...")
    else:
        print("Geçersiz seçim!")


if __name__ == '__main__':
    main()
