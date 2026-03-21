# Automated Reporting & Email System - Implementation Guide

## 📧 Complete Email & Report Automation Setup

This guide shows how to implement **automatic report generation and email sending** in the Service Management System using Celery, Redis, and email services.

---

## 🎯 Overview

The system can automatically:
- ✅ Generate daily/weekly/monthly reports
- ✅ Send emails with reports attached
- ✅ Send notifications for service requests, payments, and SLA alerts
- ✅ Schedule recurring tasks
- ✅ Track email delivery status
- ✅ Create PDF reports from templates
- ✅ Send invoice reminders and payment notifications

---

## 🛠️ Technology Stack

| Component | Purpose |
|-----------|---------|
| **Celery** | Distributed task queue for background jobs |
| **Redis** | Message broker and result backend |
| **APScheduler** | Scheduled task execution |
| **Flask-Mail** | Email sending from Flask |
| **Jinja2** | Email template rendering |
| **ReportLab** | PDF generation |
| **Pandas** | Excel report generation |

---

## 1️⃣ Installation & Setup

### Step 1: Update Requirements

Add to `backend_requirements.txt`:

```
celery==5.3.1
redis==5.0.0
flask-mail==0.9.1
APScheduler==3.10.4
reportlab==4.0.7
pandas==2.0.3
jinja2==3.1.2
python-dotenv==1.0.0
```

Install:
```bash
pip install -r backend_requirements.txt
```

### Step 2: Configure Environment Variables

Update `.env.example`:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@servicemanagement.com

# Alternative: SendGrid
SENDGRID_API_KEY=sg_xxxxxxxx

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Report Settings
REPORTS_TIMEZONE=Europe/Istanbul
REPORT_EMAIL_HOUR=09
REPORT_EMAIL_MINUTE=00
```

---

## 2️⃣ Celery Task Configuration

### Create `celery_app.py`:

```python
from celery import Celery
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery(app: Flask) -> Celery:
    """Create Celery instance with Flask app context"""
    celery = Celery(
        app.import_name,
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
```

### Update `app.py`:

```python
from flask import Flask
from celery_app import make_celery
from flask_mail import Mail
import os

def create_app(config_name='development'):
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')

    # Email Configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Initialize extensions
    from models import db
    db.init_app(app)

    mail = Mail(app)
    celery = make_celery(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.customers import customers_bp
    from routes.requests import requests_bp
    from routes.invoicing import invoicing_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(requests_bp, url_prefix='/api/requests')
    app.register_blueprint(invoicing_bp, url_prefix='/api/invoicing')

    return app, mail, celery

app, mail, celery = create_app()
```

---

## 3️⃣ Email Tasks

### Create `tasks/email_tasks.py`:

```python
from celery import shared_task
from flask_mail import Message
from flask import render_template_string, current_app
from models import db, Invoice, ServiceRequest, User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email(self, recipients, subject, html_body, attachments=None):
    """Send email with retry logic"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body
        )

        if attachments:
            for filename, content, mimetype in attachments:
                msg.attach(filename, mimetype, content)

        from app import mail
        mail.send(msg)
        logger.info(f"Email sent to {recipients} with subject: {subject}")
        return {'status': 'sent', 'recipients': recipients}

    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        # Retry in 60 seconds
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_invoice_email(invoice_id):
    """Send invoice to customer"""
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return {'error': 'Invoice not found'}

    # Generate PDF
    pdf_content = generate_invoice_pdf(invoice)

    html_template = """
    <h2>Invoice #{invoice_number}</h2>
    <p>Dear {customer_name},</p>
    <p>Your service invoice is attached. Please process payment within 30 days.</p>
    <p><strong>Total Amount:</strong> ${total}</p>
    <p>Thank you for your business!</p>
    """

    html_body = html_template.format(
        invoice_number=invoice.id,
        customer_name=invoice.customer.name,
        total=invoice.total_amount
    )

    attachments = [
        (f'Invoice-{invoice.id}.pdf', pdf_content, 'application/pdf')
    ]

    send_email.delay(
        recipients=invoice.customer.email,
        subject=f'Invoice #{invoice.id}',
        html_body=html_body,
        attachments=attachments
    )


@shared_task
def send_service_request_notification(request_id, event_type):
    """Notify technician about service request assignment/update"""
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return {'error': 'Request not found'}

    templates = {
        'assigned': """
            <h2>New Service Assignment</h2>
            <p>You have been assigned to service request #{id}</p>
            <p><strong>Customer:</strong> {customer}</p>
            <p><strong>Location:</strong> {location}</p>
            <p><strong>Scheduled:</strong> {scheduled_date}</p>
        """,
        'completed': """
            <h2>Service Request Completed</h2>
            <p>Service request #{id} has been marked complete</p>
            <p><strong>Hours Worked:</strong> {hours}</p>
            <p><strong>Parts Used:</strong> {parts}</p>
        """,
        'payment_received': """
            <h2>Payment Received</h2>
            <p>Payment received for invoice #{invoice_id}</p>
            <p><strong>Amount:</strong> ${amount}</p>
            <p>Thank you!</p>
        """
    }

    template = templates.get(event_type, '')
    html_body = template.format(
        id=service_request.id,
        customer=service_request.customer.name,
        location=service_request.location,
        scheduled_date=service_request.scheduled_date,
        hours=getattr(service_request, 'hours_worked', 0),
        parts=getattr(service_request, 'parts_used', 'N/A'),
        invoice_id=getattr(service_request, 'invoice_id', 'N/A'),
        amount=getattr(service_request, 'invoice_amount', 0)
    )

    recipient = service_request.assigned_technician.email if service_request.assigned_technician else None
    if recipient:
        send_email.delay(
            recipients=recipient,
            subject=f'{event_type.replace("_", " ").title()} - Request #{service_request.id}',
            html_body=html_body
        )


@shared_task
def send_daily_summary_email(user_id):
    """Send daily summary to user"""
    user = User.query.get(user_id)
    if not user or not user.email:
        return {'error': 'User not found'}

    # Get today's data
    from datetime import date
    today = date.today()

    pending_requests = ServiceRequest.query.filter(
        ServiceRequest.status == 'pending',
        ServiceRequest.created_date.cast(db.Date) == today
    ).count()

    completed_requests = ServiceRequest.query.filter(
        ServiceRequest.status == 'completed',
        ServiceRequest.completed_date.cast(db.Date) == today
    ).count()

    html_body = f"""
    <h2>Daily Service Summary - {today}</h2>
    <p>Hello {user.full_name},</p>
    <ul>
        <li><strong>New Requests Today:</strong> {pending_requests}</li>
        <li><strong>Completed Today:</strong> {completed_requests}</li>
    </ul>
    <p><a href="https://yourapp.com/dashboard">View Full Dashboard</a></p>
    """

    send_email.delay(
        recipients=user.email,
        subject=f'Daily Summary - {today}',
        html_body=html_body
    )
```

---

## 4️⃣ Report Generation

### Create `tasks/report_tasks.py`:

```python
from celery import shared_task
from models import db, Invoice, ServiceRequest, Technician
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd
import io
from tasks.email_tasks import send_email

@shared_task
def generate_daily_report(report_date=None):
    """Generate daily service report"""
    if not report_date:
        report_date = datetime.now().date()

    # Fetch data
    daily_requests = ServiceRequest.query.filter(
        ServiceRequest.created_date.cast(db.Date) == report_date
    ).all()

    completed_requests = ServiceRequest.query.filter(
        ServiceRequest.completed_date.cast(db.Date) == report_date,
        ServiceRequest.status == 'completed'
    ).all()

    # Generate PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=30
    )

    # Title
    story.append(Paragraph(f"Daily Service Report - {report_date}", title_style))
    story.append(Spacer(1, 0.3*inch))

    # Summary
    summary_data = [
        ['Metric', 'Count'],
        ['New Requests', str(len(daily_requests))],
        ['Completed', str(len(completed_requests))],
        ['Pending', str(len([r for r in daily_requests if r.status == 'pending']))],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))

    # Details
    if daily_requests:
        story.append(Paragraph("Request Details", styles['Heading2']))

        details_data = [['ID', 'Customer', 'Type', 'Status']]
        for req in daily_requests[:10]:  # Limit to 10
            details_data.append([
                str(req.id),
                req.customer.name[:20],
                req.request_type,
                req.status
            ])

        details_table = Table(details_data, colWidths=[0.8*inch, 2*inch, 1.5*inch, 1*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(details_table)

    # Build PDF
    doc.build(story)
    pdf_content = pdf_buffer.getvalue()

    return {
        'status': 'generated',
        'report_date': str(report_date),
        'requests_count': len(daily_requests),
        'completed_count': len(completed_requests)
    }


@shared_task
def generate_weekly_report(end_date=None):
    """Generate weekly analytics report"""
    if not end_date:
        end_date = datetime.now().date()

    start_date = end_date - timedelta(days=7)

    # Fetch data
    weekly_requests = ServiceRequest.query.filter(
        ServiceRequest.created_date >= start_date
    ).all()

    completed = len([r for r in weekly_requests if r.status == 'completed'])
    pending = len([r for r in weekly_requests if r.status == 'pending'])
    total_revenue = sum([r.invoice.total_amount for r in weekly_requests if r.invoice])

    # Technician performance
    technicians = Technician.query.all()
    tech_stats = []
    for tech in technicians:
        assigned = ServiceRequest.query.filter(
            ServiceRequest.assigned_technician_id == tech.id,
            ServiceRequest.created_date >= start_date
        ).count()

        completed_by_tech = ServiceRequest.query.filter(
            ServiceRequest.assigned_technician_id == tech.id,
            ServiceRequest.status == 'completed',
            ServiceRequest.completed_date >= start_date
        ).count()

        tech_stats.append({
            'name': tech.full_name,
            'assigned': assigned,
            'completed': completed_by_tech
        })

    # Create Excel report
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([{
            'Week': f'{start_date} to {end_date}',
            'Total Requests': len(weekly_requests),
            'Completed': completed,
            'Pending': pending,
            'Total Revenue': f'${total_revenue:.2f}'
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Technician stats
        tech_df = pd.DataFrame(tech_stats)
        tech_df.to_excel(writer, sheet_name='Technicians', index=False)

    excel_content = excel_buffer.getvalue()

    return {
        'status': 'generated',
        'period': f'{start_date} to {end_date}',
        'total_requests': len(weekly_requests),
        'revenue': float(total_revenue)
    }


@shared_task
def generate_monthly_report(year, month):
    """Generate comprehensive monthly report"""
    from dateutil.relativedelta import relativedelta

    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month, 1) + relativedelta(months=1) - timedelta(days=1)).date()

    # Fetch data
    monthly_requests = ServiceRequest.query.filter(
        ServiceRequest.created_date >= start_date,
        ServiceRequest.created_date <= end_date
    ).all()

    monthly_invoices = Invoice.query.filter(
        Invoice.created_date >= start_date,
        Invoice.created_date <= end_date
    ).all()

    # Calculations
    total_requests = len(monthly_requests)
    completed_requests = len([r for r in monthly_requests if r.status == 'completed'])
    pending_requests = len([r for r in monthly_requests if r.status == 'pending'])
    total_revenue = sum([inv.total_amount for inv in monthly_invoices])
    paid_amount = sum([inv.paid_amount for inv in monthly_invoices if inv.payment_status == 'paid'])
    pending_amount = total_revenue - paid_amount

    report_data = {
        'month': f'{month}/{year}',
        'total_requests': total_requests,
        'completed': completed_requests,
        'pending': pending_requests,
        'completion_rate': f'{(completed_requests/total_requests*100):.1f}%' if total_requests > 0 else '0%',
        'total_revenue': float(total_revenue),
        'paid_amount': float(paid_amount),
        'pending_amount': float(pending_amount)
    }

    return report_data
```

---

## 5️⃣ Scheduled Tasks

### Create `tasks/scheduler.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import os
import logging

logger = logging.getLogger(__name__)

def init_scheduler(app):
    """Initialize APScheduler for scheduled tasks"""
    scheduler = BackgroundScheduler()

    # Daily Report - Every day at 9 AM
    scheduler.add_job(
        func=send_daily_reports,
        trigger=CronTrigger(hour=9, minute=0),
        id='daily_report_job',
        name='Daily Report Generation',
        replace_existing=True
    )

    # Weekly Report - Every Monday at 9 AM
    scheduler.add_job(
        func=send_weekly_reports,
        trigger=CronTrigger(day_of_week=0, hour=9, minute=0),  # Monday
        id='weekly_report_job',
        name='Weekly Report Generation',
        replace_existing=True
    )

    # Monthly Report - First day of month at 9 AM
    scheduler.add_job(
        func=send_monthly_reports,
        trigger=CronTrigger(day=1, hour=9, minute=0),
        id='monthly_report_job',
        name='Monthly Report Generation',
        replace_existing=True
    )

    # Invoice Reminders - Every Friday at 10 AM
    scheduler.add_job(
        func=send_invoice_reminders,
        trigger=CronTrigger(day_of_week=4, hour=10, minute=0),  # Friday
        id='invoice_reminder_job',
        name='Invoice Reminder Emails',
        replace_existing=True
    )

    # SLA Alerts - Every hour
    scheduler.add_job(
        func=check_sla_breaches,
        trigger=CronTrigger(minute=0),
        id='sla_alert_job',
        name='SLA Breach Check',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name} ({job.id}): {job.trigger}")

    return scheduler


def send_daily_reports():
    """Send daily reports to all admin users"""
    from app import celery
    from models import User
    from tasks.report_tasks import generate_daily_report

    with celery.app.app_context():
        admins = User.query.filter_by(role='admin').all()

        for admin in admins:
            if admin.email:
                generate_daily_report.delay()
                logger.info(f"Daily report queued for {admin.email}")


def send_weekly_reports():
    """Send weekly reports"""
    from app import celery
    from models import User
    from tasks.report_tasks import generate_weekly_report

    with celery.app.app_context():
        managers = User.query.filter(User.role.in_(['admin', 'manager'])).all()

        for manager in managers:
            if manager.email:
                generate_weekly_report.delay()
                logger.info(f"Weekly report queued for {manager.email}")


def send_monthly_reports():
    """Send monthly reports"""
    from app import celery
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from models import User
    from tasks.report_tasks import generate_monthly_report

    with celery.app.app_context():
        last_month = datetime.now() - relativedelta(months=1)
        year = last_month.year
        month = last_month.month

        admins = User.query.filter_by(role='admin').all()

        for admin in admins:
            if admin.email:
                generate_monthly_report.delay(year, month)
                logger.info(f"Monthly report queued for {admin.email}")


def send_invoice_reminders():
    """Send reminders for unpaid invoices older than 7 days"""
    from app import celery
    from models import Invoice
    from datetime import datetime, timedelta
    from tasks.email_tasks import send_email

    with celery.app.app_context():
        cutoff_date = datetime.now() - timedelta(days=7)

        unpaid_invoices = Invoice.query.filter(
            Invoice.payment_status != 'paid',
            Invoice.created_date <= cutoff_date
        ).all()

        for invoice in unpaid_invoices:
            email_body = f"""
            <h2>Payment Reminder</h2>
            <p>Dear {invoice.customer.name},</p>
            <p>This is a reminder that invoice #{invoice.id} totaling ${invoice.total_amount:.2f} is still outstanding.</p>
            <p>Please process payment at your earliest convenience.</p>
            """

            send_email.delay(
                recipients=invoice.customer.email,
                subject=f'Payment Reminder - Invoice #{invoice.id}',
                html_body=email_body
            )

            logger.info(f"Invoice reminder sent for invoice {invoice.id}")


def check_sla_breaches():
    """Check for SLA breaches and send alerts"""
    from app import celery
    from models import ServiceRequest, ServiceContract
    from datetime import datetime
    from tasks.email_tasks import send_email

    with celery.app.app_context():
        active_contracts = ServiceContract.query.filter_by(is_active=True).all()

        for contract in active_contracts:
            requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == contract.customer_id,
                ServiceRequest.status != 'completed'
            ).all()

            for req in requests:
                elapsed_hours = (datetime.utcnow() - req.created_date).total_seconds() / 3600

                if elapsed_hours > contract.response_time_hours:
                    # SLA breach!
                    alert_email = f"""
                    <h2>⚠️ SLA Breach Alert</h2>
                    <p>Service request #{req.id} has exceeded SLA response time.</p>
                    <p><strong>Customer:</strong> {req.customer.name}</p>
                    <p><strong>Time Elapsed:</strong> {elapsed_hours:.1f} hours</p>
                    <p><strong>SLA Target:</strong> {contract.response_time_hours} hours</p>
                    """

                    send_email.delay(
                        recipients=[u.email for u in [req.customer.contact_person] if u],
                        subject=f'⚠️ SLA Breach - Request #{req.id}',
                        html_body=alert_email
                    )

                    logger.warning(f"SLA breach detected for request {req.id}")
```

---

## 6️⃣ Running Celery Workers

### Start Celery Worker:

```bash
# In production environment
celery -A celery_app worker --loglevel=info

# Or with concurrency
celery -A celery_app worker --loglevel=info --concurrency=4
```

### Start Celery Beat (Scheduler):

```bash
# In separate terminal/process
celery -A celery_app beat --loglevel=info
```

### Or Combined (for development):

```bash
celery -A celery_app worker --beat --loglevel=info
```

---

## 7️⃣ Docker Deployment

### Updated `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: service_management
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/service_management
      REDIS_URL: redis://redis:6379
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      MAIL_SERVER: ${MAIL_SERVER}
      MAIL_PORT: ${MAIL_PORT}
      MAIL_USERNAME: ${MAIL_USERNAME}
      MAIL_PASSWORD: ${MAIL_PASSWORD}
    depends_on:
      - postgres
      - redis
    ports:
      - "5000:5000"

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: celery -A celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/service_management
      REDIS_URL: redis://redis:6379
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      MAIL_SERVER: ${MAIL_SERVER}
      MAIL_PORT: ${MAIL_PORT}
      MAIL_USERNAME: ${MAIL_USERNAME}
      MAIL_PASSWORD: ${MAIL_PASSWORD}
    depends_on:
      - postgres
      - redis
      - api

  celery_beat:
    build:
      context: .
      dockerfile: Dockerfile.backend
    command: celery -A celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/service_management
      REDIS_URL: redis://redis:6379
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
      - api

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

### Updated Dockerfile for Celery:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Default to API, can be overridden in docker-compose
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "wsgi:app"]
```

---

## 8️⃣ Integration Routes

### Add Email Endpoints to Flask:

Create `routes/notifications.py`:

```python
from flask import Blueprint, jsonify, request
from models import db, Invoice, ServiceRequest, User
from tasks.email_tasks import send_email, send_invoice_email, send_service_request_notification
from tasks.report_tasks import generate_daily_report, generate_weekly_report, generate_monthly_report
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/send-test-email', methods=['POST'])
def send_test_email():
    """Test email sending"""
    data = request.json

    send_email.delay(
        recipients=data['email'],
        subject='Test Email',
        html_body='<p>This is a test email from Service Management System</p>'
    )

    return jsonify({'status': 'email queued', 'recipient': data['email']})


@notifications_bp.route('/invoices/<int:invoice_id>/send-email', methods=['POST'])
def email_invoice(invoice_id):
    """Send invoice email"""
    send_invoice_email.delay(invoice_id)
    return jsonify({'status': 'email queued', 'invoice_id': invoice_id})


@notifications_bp.route('/requests/<int:request_id>/notify-technician', methods=['POST'])
def notify_technician(request_id):
    """Notify technician about assignment"""
    data = request.json
    event_type = data.get('event_type', 'assigned')

    send_service_request_notification.delay(request_id, event_type)
    return jsonify({'status': 'notification queued', 'request_id': request_id})


@notifications_bp.route('/reports/daily', methods=['POST'])
def trigger_daily_report():
    """Manually trigger daily report"""
    report_date = request.json.get('date') if request.json else None
    generate_daily_report.delay(report_date)
    return jsonify({'status': 'report generation queued'})


@notifications_bp.route('/reports/weekly', methods=['POST'])
def trigger_weekly_report():
    """Manually trigger weekly report"""
    generate_weekly_report.delay()
    return jsonify({'status': 'report generation queued'})


@notifications_bp.route('/reports/monthly', methods=['POST'])
def trigger_monthly_report():
    """Manually trigger monthly report"""
    data = request.json
    year = data.get('year', datetime.now().year)
    month = data.get('month', datetime.now().month)

    generate_monthly_report.delay(year, month)
    return jsonify({'status': 'report generation queued'})
```

---

## 9️⃣ Usage Examples

### Trigger Email on Invoice Creation:

In `routes/invoicing.py`:

```python
@invoicing_bp.route('/invoices', methods=['POST'])
def create_invoice():
    """Create invoice and send email"""
    data = request.json

    invoice = Invoice(
        customer_id=data['customer_id'],
        service_request_id=data['service_request_id'],
        total_amount=data['total_amount']
    )

    db.session.add(invoice)
    db.session.commit()

    # Queue email task
    from tasks.email_tasks import send_invoice_email
    send_invoice_email.delay(invoice.id)

    return jsonify(invoice.to_dict()), 201
```

### Trigger Notification on Service Request Assignment:

```python
@requests_bp.route('/requests/<int:request_id>/assign', methods=['PUT'])
def assign_technician(request_id):
    """Assign technician and notify them"""
    data = request.json
    service_request = ServiceRequest.query.get(request_id)

    service_request.assigned_technician_id = data['technician_id']
    db.session.commit()

    # Queue notification
    from tasks.email_tasks import send_service_request_notification
    send_service_request_notification.delay(request_id, 'assigned')

    return jsonify(service_request.to_dict())
```

---

## 🔟 Monitoring & Admin

### Create Admin Dashboard for Tasks:

```python
@notifications_bp.route('/tasks/status', methods=['GET'])
def get_tasks_status():
    """Get status of all scheduled tasks"""
    from celery_app import celery

    inspector = celery.control.inspect()

    return jsonify({
        'active_tasks': inspector.active(),
        'scheduled_tasks': inspector.scheduled(),
        'registered_tasks': inspector.registered(),
        'stats': inspector.stats()
    })


@notifications_bp.route('/scheduler/jobs', methods=['GET'])
def get_scheduled_jobs():
    """Get all scheduled jobs"""
    from tasks.scheduler import scheduler

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'trigger': str(job.trigger),
            'next_run_time': str(job.next_run_time)
        })

    return jsonify({'jobs': jobs})
```

---

## ✅ Quick Start Checklist

- [ ] Install Celery, Redis, Flask-Mail dependencies
- [ ] Create `.env` file with email configuration
- [ ] Create `celery_app.py` configuration
- [ ] Create task files in `tasks/` directory
- [ ] Create scheduler in `tasks/scheduler.py`
- [ ] Update Flask `app.py` to initialize Celery
- [ ] Add notification routes
- [ ] Start Redis server: `redis-server`
- [ ] Start Celery worker: `celery -A celery_app worker`
- [ ] Start Celery Beat: `celery -A celery_app beat`
- [ ] Test email sending via `/send-test-email` endpoint
- [ ] Verify scheduled tasks in admin dashboard

---

## 🎯 Common Use Cases

| Use Case | Implementation |
|----------|-----------------|
| **Send invoice email** | `send_invoice_email(invoice_id)` |
| **Notify technician** | `send_service_request_notification(request_id, 'assigned')` |
| **Daily report to admins** | Scheduled via `send_daily_reports()` at 9 AM |
| **Invoice reminders** | Scheduled via `send_invoice_reminders()` Friday 10 AM |
| **SLA breach alerts** | Scheduled via `check_sla_breaches()` every hour |
| **Weekly analytics** | Scheduled via `send_weekly_reports()` Mondays 9 AM |
| **Monthly reports** | Scheduled via `send_monthly_reports()` 1st of month 9 AM |

---

## 🚀 Production Tips

1. **Use managed services:**
   - SendGrid or AWS SES for reliable email delivery
   - AWS RDS for PostgreSQL
   - AWS ElastiCache for Redis
   - AWS SQS alternative to Redis for message queue

2. **Email delivery:**
   - Set up SPF, DKIM, DMARC records
   - Monitor bounce and complaint rates
   - Implement unsubscribe functionality
   - Use email templates with proper branding

3. **Monitoring:**
   - Monitor Celery worker status
   - Track email delivery rates
   - Monitor scheduled task execution
   - Set up alerts for task failures

4. **Scaling:**
   - Run multiple Celery workers for concurrency
   - Use connection pooling for database
   - Implement task rate limiting
   - Archive old task results to reduce Redis memory

---

**Version:** 1.0.0
**Last Updated:** March 2026
**Ready to implement automated reporting and email!** 📧📊

