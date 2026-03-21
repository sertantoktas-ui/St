#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teknik Servis Takip ve Planlama Programı
Technical Service Tracking and Planning Application
"""

import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QMessageBox,
    QTabWidget, QFormLayout, QHeaderView, QDateTimeEdit
)
from PyQt5.QtCore import Qt, QDate, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QColor, QFont

# Database initialization
DB_PATH = "service_tracking.db"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Customers table
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT, address TEXT)''')

    # Technicians table
    c.execute('''CREATE TABLE IF NOT EXISTS technicians
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, specialty TEXT, status TEXT)''')

    # Service requests table
    c.execute('''CREATE TABLE IF NOT EXISTS service_requests
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, description TEXT,
                  priority TEXT, status TEXT, created_date TEXT, scheduled_date TEXT,
                  completed_date TEXT, technician_id INTEGER, notes TEXT,
                  FOREIGN KEY(customer_id) REFERENCES customers(id),
                  FOREIGN KEY(technician_id) REFERENCES technicians(id))''')

    # Service log table
    c.execute('''CREATE TABLE IF NOT EXISTS service_log
                 (id INTEGER PRIMARY KEY, request_id INTEGER, technician_id INTEGER,
                  work_description TEXT, duration INTEGER, completed_date TEXT,
                  FOREIGN KEY(request_id) REFERENCES service_requests(id),
                  FOREIGN KEY(technician_id) REFERENCES technicians(id))''')

    conn.commit()
    conn.close()


class AddCustomerDialog(QDialog):
    """Dialog for adding new customer"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Yeni Müşteri Ekle")
        self.setGeometry(100, 100, 400, 250)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QTextEdit()

        layout.addRow("Ad Soyad:", self.name_input)
        layout.addRow("Telefon:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Adres:", self.address_input)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        cancel_btn = QPushButton("İptal")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'email': self.email_input.text(),
            'address': self.address_input.toPlainText()
        }


class AddTechnicianDialog(QDialog):
    """Dialog for adding new technician"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Yeni Teknisyen Ekle")
        self.setGeometry(100, 100, 400, 250)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.specialty_input = QLineEdit()

        layout.addRow("Ad Soyad:", self.name_input)
        layout.addRow("Telefon:", self.phone_input)
        layout.addRow("Uzmanlık Alanı:", self.specialty_input)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        cancel_btn = QPushButton("İptal")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'specialty': self.specialty_input.text(),
            'status': 'Aktif'
        }


class AddServiceRequestDialog(QDialog):
    """Dialog for adding new service request"""
    def __init__(self, parent=None, customers=None, technicians=None):
        super().__init__(parent)
        self.customers = customers or []
        self.technicians = technicians or []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Yeni Servis Talebi Ekle")
        self.setGeometry(100, 100, 500, 450)

        layout = QFormLayout()

        # Customer selection
        self.customer_combo = QComboBox()
        self.customer_combo.addItems([f"{c[0]}: {c[1]}" for c in self.customers])

        # Description
        self.description_input = QTextEdit()

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Düşük", "Orta", "Yüksek", "Acil"])

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Açık", "Atandı", "İnceleme Altında", "Tamamlandı"])

        # Scheduled date
        self.scheduled_date = QDateTimeEdit()
        self.scheduled_date.setDateTime(QDateTime.currentDateTime())

        # Technician assignment
        self.technician_combo = QComboBox()
        self.technician_combo.addItem("Henüz Atanmadı")
        self.technician_combo.addItems([f"{t[0]}: {t[1]}" for t in self.technicians])

        # Notes
        self.notes_input = QTextEdit()

        layout.addRow("Müşteri:", self.customer_combo)
        layout.addRow("Açıklama:", self.description_input)
        layout.addRow("Öncelik:", self.priority_combo)
        layout.addRow("Durum:", self.status_combo)
        layout.addRow("Planlanan Tarih:", self.scheduled_date)
        layout.addRow("Teknisyen:", self.technician_combo)
        layout.addRow("Notlar:", self.notes_input)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Kaydet")
        cancel_btn = QPushButton("İptal")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        customer_id = self.customers[self.customer_combo.currentIndex()][0]
        technician_id = None if self.technician_combo.currentIndex() == 0 else \
                       self.technicians[self.technician_combo.currentIndex() - 1][0]

        return {
            'customer_id': customer_id,
            'description': self.description_input.toPlainText(),
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'scheduled_date': self.scheduled_date.dateTime().toString("yyyy-MM-dd HH:mm"),
            'technician_id': technician_id,
            'notes': self.notes_input.toPlainText(),
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }


class ServiceTrackingApp(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        init_database()
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle("Teknik Servis Takip ve Planlama Programı")
        self.setGeometry(50, 50, 1200, 800)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Service Requests
        self.service_tab = QWidget()
        service_layout = QVBoxLayout()

        service_button_layout = QHBoxLayout()
        add_service_btn = QPushButton("Yeni Servis Talebi")
        add_service_btn.clicked.connect(self.add_service_request)
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_service_requests)
        complete_btn = QPushButton("Tamamla")
        complete_btn.clicked.connect(self.complete_service_request)

        service_button_layout.addWidget(add_service_btn)
        service_button_layout.addWidget(complete_btn)
        service_button_layout.addWidget(refresh_btn)
        service_button_layout.addStretch()

        self.service_table = QTableWidget()
        self.service_table.setColumnCount(8)
        self.service_table.setHorizontalHeaderLabels([
            "ID", "Müşteri", "Açıklama", "Öncelik", "Durum", "Planlanan Tarih", "Teknisyen", "Notlar"
        ])
        self.service_table.horizontalHeader().setStretchLastSection(True)
        self.service_table.setSelectionBehavior(self.service_table.SelectRows)
        self.service_table.setSelectionMode(self.service_table.SingleSelection)

        service_layout.addLayout(service_button_layout)
        service_layout.addWidget(self.service_table)
        self.service_tab.setLayout(service_layout)

        # Tab 2: Customers
        self.customer_tab = QWidget()
        customer_layout = QVBoxLayout()

        customer_button_layout = QHBoxLayout()
        add_customer_btn = QPushButton("Yeni Müşteri")
        add_customer_btn.clicked.connect(self.add_customer)
        refresh_customer_btn = QPushButton("Yenile")
        refresh_customer_btn.clicked.connect(self.refresh_customers)

        customer_button_layout.addWidget(add_customer_btn)
        customer_button_layout.addWidget(refresh_customer_btn)
        customer_button_layout.addStretch()

        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(5)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Telefon", "Email", "Adres"])
        self.customer_table.horizontalHeader().setStretchLastSection(True)

        customer_layout.addLayout(customer_button_layout)
        customer_layout.addWidget(self.customer_table)
        self.customer_tab.setLayout(customer_layout)

        # Tab 3: Technicians
        self.technician_tab = QWidget()
        technician_layout = QVBoxLayout()

        technician_button_layout = QHBoxLayout()
        add_technician_btn = QPushButton("Yeni Teknisyen")
        add_technician_btn.clicked.connect(self.add_technician)
        refresh_technician_btn = QPushButton("Yenile")
        refresh_technician_btn.clicked.connect(self.refresh_technicians)

        technician_button_layout.addWidget(add_technician_btn)
        technician_button_layout.addWidget(refresh_technician_btn)
        technician_button_layout.addStretch()

        self.technician_table = QTableWidget()
        self.technician_table.setColumnCount(4)
        self.technician_table.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Telefon", "Uzmanlık"])
        self.technician_table.horizontalHeader().setStretchLastSection(True)

        technician_layout.addLayout(technician_button_layout)
        technician_layout.addWidget(self.technician_table)
        self.technician_tab.setLayout(technician_layout)

        # Tab 4: Statistics
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel()
        font = QFont()
        font.setPointSize(11)
        self.stats_label.setFont(font)

        refresh_stats_btn = QPushButton("İstatistikleri Yenile")
        refresh_stats_btn.clicked.connect(self.refresh_statistics)

        stats_layout.addWidget(refresh_stats_btn)
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        self.stats_tab.setLayout(stats_layout)

        # Add tabs
        tabs.addTab(self.service_tab, "Servis Talepleri")
        tabs.addTab(self.customer_tab, "Müşteriler")
        tabs.addTab(self.technician_tab, "Teknisyenler")
        tabs.addTab(self.stats_tab, "İstatistikler")

        main_layout.addWidget(tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_data(self):
        """Load all data from database"""
        self.refresh_service_requests()
        self.refresh_customers()
        self.refresh_technicians()
        self.refresh_statistics()

    def refresh_service_requests(self):
        """Refresh service requests table"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT sr.id, c.name, sr.description, sr.priority, sr.status,
                            sr.scheduled_date, t.name, sr.notes
                     FROM service_requests sr
                     LEFT JOIN customers c ON sr.customer_id = c.id
                     LEFT JOIN technicians t ON sr.technician_id = t.id
                     ORDER BY sr.id DESC''')

        rows = c.fetchall()
        conn.close()

        self.service_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data else "")
                self.service_table.setItem(row_idx, col_idx, item)

    def refresh_customers(self):
        """Refresh customers table"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, phone, email, address FROM customers ORDER BY id DESC')

        rows = c.fetchall()
        conn.close()

        self.customer_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data else "")
                self.customer_table.setItem(row_idx, col_idx, item)

    def refresh_technicians(self):
        """Refresh technicians table"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, phone, specialty FROM technicians ORDER BY id DESC')

        rows = c.fetchall()
        conn.close()

        self.technician_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data else "")
                self.technician_table.setItem(row_idx, col_idx, item)

    def refresh_statistics(self):
        """Refresh statistics"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get statistics
        c.execute('SELECT COUNT(*) FROM service_requests')
        total_requests = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM service_requests WHERE status = ?', ("Tamamlandı",))
        completed = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM service_requests WHERE status = ?', ("Açık",))
        open_requests = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM service_requests WHERE priority = ?', ("Acil",))
        urgent = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM technicians')
        technicians_count = c.fetchone()[0]

        c.execute('SELECT COUNT(*) FROM customers')
        customers_count = c.fetchone()[0]

        conn.close()

        stats_text = f"""
        <b>Genel İstatistikler</b><br><br>
        <b>Servis Talepleri:</b> {total_requests}<br>
        • Tamamlanan: {completed}<br>
        • Açık: {open_requests}<br>
        • Acil: {urgent}<br><br>
        <b>Sistem Bilgileri:</b><br>
        • Toplam Müşteri: {customers_count}<br>
        • Toplam Teknisyen: {technicians_count}<br>
        <b>Tamamlanma Oranı:</b> {round((completed / total_requests * 100), 1) if total_requests > 0 else 0}%
        """

        self.stats_label.setText(stats_text)

    def add_customer(self):
        """Add new customer"""
        dialog = AddCustomerDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)',
                     (data['name'], data['phone'], data['email'], data['address']))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Başarı", "Müşteri başarıyla eklendi!")
            self.refresh_customers()

    def add_technician(self):
        """Add new technician"""
        dialog = AddTechnicianDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO technicians (name, phone, specialty, status) VALUES (?, ?, ?, ?)',
                     (data['name'], data['phone'], data['specialty'], data['status']))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Başarı", "Teknisyen başarıyla eklendi!")
            self.refresh_technicians()

    def add_service_request(self):
        """Add new service request"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute('SELECT id, name FROM customers')
        customers = c.fetchall()

        c.execute('SELECT id, name FROM technicians')
        technicians = c.fetchall()

        conn.close()

        if not customers:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir müşteri ekleyin!")
            return

        dialog = AddServiceRequestDialog(self, customers, technicians)
        if dialog.exec_():
            data = dialog.get_data()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''INSERT INTO service_requests
                        (customer_id, description, priority, status, created_date,
                         scheduled_date, technician_id, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['customer_id'], data['description'], data['priority'],
                      data['status'], data['created_date'], data['scheduled_date'],
                      data['technician_id'], data['notes']))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Başarı", "Servis talebi başarıyla eklendi!")
            self.refresh_service_requests()
            self.refresh_statistics()

    def complete_service_request(self):
        """Mark selected service request as completed"""
        selected_row = self.service_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir servis talebini seçin!")
            return

        request_id = int(self.service_table.item(selected_row, 0).text())

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute('UPDATE service_requests SET status = ?, completed_date = ? WHERE id = ?',
                 ("Tamamlandı", completed_date, request_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Başarı", "Servis talebi tamamlandı olarak işaretlendi!")
        self.refresh_service_requests()
        self.refresh_statistics()


def main():
    app = QApplication(sys.argv)
    window = ServiceTrackingApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
