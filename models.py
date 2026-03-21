#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Models for Enterprise Service Management System
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
import uuid

class User(db.Model):
    """User/Employee model"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='technician')  # admin, manager, technician, customer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    technician = db.relationship('Technician', uselist=False, backref='user')
    customer = db.relationship('Customer', uselist=False, backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Customer(db.Model):
    """Customer model"""
    __tablename__ = 'customers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(120))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    tax_id = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade='all, delete-orphan')
    contracts = db.relationship('ServiceContract', backref='customer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'location': {'lat': self.latitude, 'lng': self.longitude},
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Technician(db.Model):
    """Technician model"""
    __tablename__ = 'technicians'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(200))  # Branş/Uzmanlık
    license_number = db.Column(db.String(100))
    certification = db.Column(db.String(200))
    hourly_rate = db.Column(db.Float, default=0.0)
    vehicle = db.Column(db.String(100))
    status = db.Column(db.String(20), default='available')  # available, busy, on_leave, inactive
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    last_location_update = db.Column(db.DateTime)
    total_hours = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = db.relationship('ServiceRequest', backref='technician', lazy=True)
    service_logs = db.relationship('ServiceLog', backref='technician', lazy=True)
    available_hours = db.relationship('TechnicianAvailability', backref='technician', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.user.full_name,
            'email': self.user.email,
            'phone': self.user.phone,
            'specialization': self.specialization,
            'status': self.status,
            'location': {'lat': self.latitude, 'lng': self.longitude},
            'rating': self.rating,
            'total_hours': self.total_hours
        }


class ServiceRequest(db.Model):
    """Service Request/Work Order model"""
    __tablename__ = 'service_requests'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    technician_id = db.Column(db.String(36), db.ForeignKey('technicians.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, assigned, in_progress, on_hold, completed, cancelled
    service_type = db.Column(db.String(50))  # maintenance, repair, installation, emergency
    scheduled_date = db.Column(db.DateTime)
    scheduled_duration = db.Column(db.Integer)  # minutes
    actual_start_time = db.Column(db.DateTime)
    actual_end_time = db.Column(db.DateTime)
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    parts_used = db.Column(db.Text)
    notes = db.Column(db.Text)
    customer_notes = db.Column(db.Text)
    sla_end_time = db.Column(db.DateTime)
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_logs = db.relationship('ServiceLog', backref='request', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'request_number': self.request_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.company_name if self.customer else None,
            'technician_id': self.technician_id,
            'technician_name': self.technician.user.full_name if self.technician else None,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'service_type': self.service_type,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'location': {'lat': self.location_latitude, 'lng': self.location_longitude},
            'created_at': self.created_at.isoformat()
        }


class ServiceLog(db.Model):
    """Service Log - Record of completed work"""
    __tablename__ = 'service_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey('service_requests.id'), nullable=False)
    technician_id = db.Column(db.String(36), db.ForeignKey('technicians.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    work_description = db.Column(db.Text)
    duration_hours = db.Column(db.Float)
    labor_cost = db.Column(db.Float)
    signature = db.Column(db.LargeBinary)  # Customer signature
    photo_urls = db.Column(db.Text)  # JSON array of photo URLs
    rating = db.Column(db.Float)
    customer_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'technician_id': self.technician_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_hours': self.duration_hours,
            'labor_cost': self.labor_cost,
            'rating': self.rating,
            'feedback': self.customer_feedback
        }


class Invoice(db.Model):
    """Invoice/Bill model"""
    __tablename__ = 'invoices'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    labor_cost = db.Column(db.Float, default=0.0)
    parts_cost = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue, cancelled
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='invoice', lazy=True, cascade='all, delete-orphan')
    service_requests = db.relationship('ServiceRequest', backref='invoice', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'issue_date': self.issue_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'labor_cost': self.labor_cost,
            'parts_cost': self.parts_cost,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = db.Column(db.String(36), db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)  # credit_card, bank_transfer, cash, check
    reference_number = db.Column(db.String(100))
    status = db.Column(db.String(20), default='completed')  # completed, pending, failed, refunded
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat(),
            'payment_method': self.payment_method,
            'status': self.status
        }


class Inventory(db.Model):
    """Inventory management"""
    __tablename__ = 'inventory'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    part_id = db.Column(db.String(36), db.ForeignKey('parts.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    min_quantity = db.Column(db.Integer, default=0)
    max_quantity = db.Column(db.Integer, default=100)
    last_restocked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    part = db.relationship('Part', backref='inventory', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'part_id': self.part_id,
            'quantity': self.quantity,
            'location': self.location,
            'low_stock': self.quantity < self.min_quantity
        }


class Part(db.Model):
    """Parts/Components catalog"""
    __tablename__ = 'parts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    part_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    cost = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    unit = db.Column(db.String(20))  # pcs, kg, m, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'part_number': self.part_number,
            'name': self.name,
            'category': self.category,
            'cost': self.cost,
            'selling_price': self.selling_price
        }


class TechnicianAvailability(db.Model):
    """Technician working hours and availability"""
    __tablename__ = 'technician_availability'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    technician_id = db.Column(db.String(36), db.ForeignKey('technicians.id'), nullable=False)
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'technician_id': self.technician_id,
            'day_of_week': self.day_of_week,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'is_available': self.is_available
        }


class ServiceContract(db.Model):
    """Service Contract/SLA"""
    __tablename__ = 'service_contracts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    contract_type = db.Column(db.String(50))  # annual, monthly, emergency
    response_time_hours = db.Column(db.Integer)  # SLA response time
    coverage_area = db.Column(db.Text)
    monthly_cost = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'customer_id': self.customer_id,
            'contract_type': self.contract_type,
            'response_time_hours': self.response_time_hours,
            'monthly_cost': self.monthly_cost,
            'status': self.status
        }
