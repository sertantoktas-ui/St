# Enterprise Service Management System - API Documentation

## 🏢 Enterprise-Level Service Management System

Servissoft, FieldCo, ServiceSoft, Negrum, IFS gibi profesyonel yazılımlar gibi kapsamlı ve ölçeklenebilir bir sistem.

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Database Models](#database-models)
5. [Features](#features)
6. [Installation](#installation)
7. [Deployment](#deployment)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 ENTERPRISE SERVICE SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │    Flask REST API (Backend)                            │  │
│  │    - User Management & Authentication (JWT)            │  │
│  │    - Service Request Management                        │  │
│  │    - Technician Scheduling & GPS Tracking             │  │
│  │    - Invoicing & Payment Processing                   │  │
│  │    - Inventory Management                             │  │
│  │    - Analytics & Reporting                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                    ↓                                         │
│  ┌────────────────┬───────────────┬──────────────────────┐  │
│  │ PostgreSQL DB  │  Redis Cache  │  File Storage        │  │
│  │ - Users        │ - Sessions    │ - Photos             │  │
│  │ - Customers    │ - Queues      │ - Signatures         │  │
│  │ - Technicians  │ - Cache       │ - Documents          │  │
│  │ - Requests     │               │                      │  │
│  │ - Invoices     │               │                      │  │
│  │ - Parts        │               │                      │  │
│  └────────────────┴───────────────┴──────────────────────┘  │
│                                                              │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │  React Web App       │  React Native Mobile App     │   │
│  │  (Admin Panel)       │  (Technician Field App)      │   │
│  │  (Customer Portal)   │  (Offline Support)           │   │
│  └──────────────────────┴──────────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  External Integrations                                 │  │
│  │  - Google Maps (Routing & Geolocation)                │  │
│  │  - Stripe (Payment Processing)                        │  │
│  │  - SMS Gateway (Notifications)                        │  │
│  │  - Email Service (Communication)                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "technician@example.com",
  "password": "password123"
}

Response:
{
  "message": "Login successful",
  "access_token": "eyJhbGc...",
  "user": {
    "id": "uuid",
    "username": "technician@example.com",
    "full_name": "John Doe",
    "role": "technician"
  }
}
```

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newtechnician@example.com",
  "email": "newtechnician@example.com",
  "password": "securepassword",
  "full_name": "Jane Smith",
  "phone": "+905551234567",
  "role": "technician"
}
```

### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer {access_token}
```

---

## 📡 API Endpoints

### Customers

#### Create Customer
```http
POST /api/customers
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "company_name": "ABC Manufacturing",
  "contact_person": "Ali Yilmaz",
  "phone": "+905551234567",
  "email": "ali@abcmanufacturing.com",
  "address": "Industrial Zone, Istanbul",
  "city": "Istanbul",
  "zip_code": "34000",
  "latitude": 41.0082,
  "longitude": 28.9784,
  "tax_id": "1234567890",
  "industry": "Manufacturing"
}
```

#### List Customers
```http
GET /api/customers?page=1&per_page=10&status=active
Authorization: Bearer {access_token}
```

#### Get Customer Details
```http
GET /api/customers/{customer_id}
Authorization: Bearer {access_token}
```

#### Get Customer Service Requests
```http
GET /api/customers/{customer_id}/requests?status=open
Authorization: Bearer {access_token}
```

---

### Service Requests (Work Orders)

#### Create Service Request
```http
POST /api/requests
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": "customer-uuid",
  "title": "Printer Repair - Model XYZ",
  "description": "Printer not printing, error code: E201",
  "priority": "high",
  "service_type": "repair",
  "scheduled_date": "2026-03-25T10:00:00",
  "latitude": 41.0082,
  "longitude": 28.9784,
  "notes": "Customer available after 9 AM"
}
```

#### List Service Requests
```http
GET /api/requests?page=1&status=open&priority=high
Authorization: Bearer {access_token}
```

#### Get Request Details
```http
GET /api/requests/{request_id}
Authorization: Bearer {access_token}
```

#### Assign Technician
```http
POST /api/requests/{request_id}/assign
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "technician_id": "technician-uuid"
}
```

#### Start Service Work
```http
POST /api/requests/{request_id}/start
Authorization: Bearer {access_token}
```

#### Complete Service
```http
POST /api/requests/{request_id}/complete
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "work_description": "Replaced paper feed roller",
  "parts_used": "Part #123456",
  "notes": "Printer working normally now"
}
```

#### Rate Service
```http
POST /api/requests/{request_id}/rate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rating": 5,
  "feedback": "Excellent service, technician was professional"
}
```

---

### Technicians

#### Create Technician
```http
POST /api/technicians
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Mehmet Aslan",
  "email": "mehmet.aslan@service.com",
  "phone": "+905551234567",
  "specialization": "Printer Repair",
  "license_number": "LIC-2024-001",
  "hourly_rate": 250,
  "vehicle": "Ford Transit 2023"
}
```

#### List Technicians
```http
GET /api/technicians?page=1&status=available&specialization=Printer
Authorization: Bearer {access_token}
```

#### Update Technician Location (GPS)
```http
POST /api/technicians/{technician_id}/location
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "latitude": 41.0082,
  "longitude": 28.9784
}
```

#### Search Available Technicians
```http
GET /api/technicians/search?latitude=41.0082&longitude=28.9784&radius=10&specialization=Printer
Authorization: Bearer {access_token}
```

#### Get Technician Statistics
```http
GET /api/technicians/{technician_id}/stats
Authorization: Bearer {access_token}
```

Response:
```json
{
  "total_requests": 145,
  "completed_requests": 138,
  "active_requests": 3,
  "completion_rate": 95.17,
  "rating": 4.8,
  "total_hours": 580.5,
  "status": "busy"
}
```

---

### Invoicing

#### Create Invoice from Service Request
```http
POST /api/invoicing/invoices
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "request_id": "request-uuid",
  "parts_cost": 500.00,
  "tax_rate": 0.18,
  "discount": 0,
  "notes": "Invoice for printer repair service"
}
```

#### List Invoices
```http
GET /api/invoicing/invoices?status=sent&customer_id=customer-uuid
Authorization: Bearer {access_token}
```

#### Record Payment
```http
POST /api/invoicing/invoices/{invoice_id}/payments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "amount": 1500.00,
  "payment_method": "bank_transfer",
  "reference_number": "TRANSFER-20260325-001"
}
```

#### Get Aging Report
```http
GET /api/invoicing/reports/aging
Authorization: Bearer {access_token}
```

---

### Inventory

#### Create Part
```http
POST /api/inventory/parts
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "part_number": "PART-001-XYZ",
  "name": "Paper Feed Roller",
  "category": "Printer Components",
  "supplier": "Tech Supply Co",
  "cost": 150.00,
  "selling_price": 200.00,
  "unit": "pcs",
  "quantity": 50,
  "location": "Warehouse A - Shelf 3",
  "min_quantity": 10,
  "max_quantity": 100
}
```

#### List Parts
```http
GET /api/inventory/parts?category=Printer&search=roller
Authorization: Bearer {access_token}
```

#### Get Low Stock Items
```http
GET /api/inventory/inventory/low-stock
Authorization: Bearer {access_token}
```

#### Adjust Inventory
```http
POST /api/inventory/inventory/{inventory_id}/adjust
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 25
}
```

#### Restock
```http
POST /api/inventory/inventory/{inventory_id}/restock
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity_added": 50
}
```

---

### Analytics & Reporting

#### Dashboard
```http
GET /api/analytics/dashboard
Authorization: Bearer {access_token}
```

Response:
```json
{
  "service_requests": {
    "total": 245,
    "open": 18,
    "in_progress": 12,
    "completed": 215,
    "completion_rate": 87.76
  },
  "revenue": {
    "total_received": 125000.00,
    "pending": 18500.00,
    "total_potential": 143500.00
  },
  "technicians": {
    "active": 8,
    "busy": 5,
    "utilization_rate": 62.5
  }
}
```

#### Technician Performance
```http
GET /api/analytics/performance/technicians
Authorization: Bearer {access_token}
```

#### Revenue by Customer
```http
GET /api/analytics/revenue/by-customer
Authorization: Bearer {access_token}
```

#### Monthly Report
```http
GET /api/analytics/reports/monthly?month=3&year=2026
Authorization: Bearer {access_token}
```

#### SLA Compliance
```http
GET /api/analytics/requests/sla-compliance
Authorization: Bearer {access_token}
```

#### System Health Check
```http
GET /api/analytics/health-check
Authorization: Bearer {access_token}
```

---

## 🗄️ Database Models

### User Model
- id (UUID primary key)
- username (unique)
- email (unique)
- password_hash
- full_name
- phone
- role (admin, manager, technician, customer)
- is_active
- created_at, updated_at

### Customer Model
- id (UUID primary key)
- user_id (foreign key)
- company_name
- contact_person
- phone, email
- address, city, zip_code
- latitude, longitude (GPS)
- tax_id
- industry
- status (active, inactive, suspended)

### Technician Model
- id (UUID primary key)
- user_id (foreign key)
- specialization
- license_number, certification
- hourly_rate
- vehicle
- status (available, busy, on_leave, inactive)
- latitude, longitude (GPS)
- rating
- total_hours

### ServiceRequest Model
- id (UUID primary key)
- request_number (unique)
- customer_id, technician_id (foreign keys)
- title, description
- priority, status
- service_type
- scheduled_date
- actual_start_time, actual_end_time
- location (latitude, longitude)
- sla_end_time
- parts_used, notes

### ServiceLog Model
- id (UUID primary key)
- request_id, technician_id (foreign keys)
- start_time, end_time
- duration_hours
- labor_cost
- work_description
- signature (binary)
- rating, feedback

### Invoice Model
- id (UUID primary key)
- invoice_number (unique)
- customer_id (foreign key)
- issue_date, due_date
- labor_cost, parts_cost
- subtotal, tax_rate, tax_amount
- total_amount, discount
- status

### Payment Model
- id (UUID primary key)
- invoice_id (foreign key)
- amount, payment_date
- payment_method
- reference_number
- status

### Part Model
- id (UUID primary key)
- part_number (unique)
- name, description
- category, supplier
- cost, selling_price
- unit

### Inventory Model
- id (UUID primary key)
- part_id (foreign key)
- quantity, location
- min_quantity, max_quantity
- last_restocked

---

## ✨ Key Features

### 1. Service Request Management
✅ Work order creation and tracking
✅ Priority and status management
✅ SLA monitoring
✅ GPS location tracking
✅ Customer notes and history

### 2. Technician Management
✅ Skill-based scheduling
✅ GPS tracking and routing
✅ Workload balancing
✅ Performance metrics
✅ Availability management

### 3. Dynamic Assignment
✅ Auto-assignment by location
✅ Skill-based matching
✅ Workload balancing
✅ Real-time optimization

### 4. Invoicing & Billing
✅ Automatic invoice generation
✅ Labor and parts cost calculation
✅ Tax management
✅ Payment tracking
✅ Accounts receivable aging

### 5. GPS & Mapping
✅ Real-time technician location
✅ Distance calculation
✅ Route optimization
✅ Service area coverage

### 6. Mobile Application
✅ Offline functionality
✅ Photo and signature capture
✅ Time tracking
✅ Customer rating

### 7. Analytics & Reporting
✅ Dashboard metrics
✅ Performance KPIs
✅ Revenue analysis
✅ SLA compliance
✅ Technician utilization

### 8. Inventory Management
✅ Stock level tracking
✅ Low stock alerts
✅ Part categorization
✅ Supplier management
✅ Cost analysis

---

## 💾 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 5+
- Node.js 14+ (for frontend)

### Backend Setup

1. **Clone Repository**
```bash
git clone https://github.com/your-org/service-management.git
cd service-management
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r backend_requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize Database**
```bash
flask db upgrade
```

6. **Create Admin User**
```bash
python
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@example.com',
        full_name='Administrator',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
```

7. **Run Application**
```bash
flask run
```

API will be available at `http://localhost:5000`

---

## 🚀 Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

Build and run:
```bash
docker build -t service-management-api .
docker run -p 5000:5000 service-management-api
```

---

## 📞 Support

For API documentation, visit: `/api/docs`
For support issues: support@example.com

---

**Version:** 1.0.0
**Last Updated:** March 2026
**Developed by:** Claude AI
