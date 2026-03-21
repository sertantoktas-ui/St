#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Invoicing and billing routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Invoice, Payment, ServiceRequest, ServiceLog
from datetime import datetime, timedelta
import uuid

invoicing_bp = Blueprint('invoicing', __name__)


@invoicing_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create invoice from service request"""
    data = request.get_json()
    request_id = data.get('request_id')

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return jsonify({'error': 'Service request not found'}), 404

    # Calculate costs
    service_log = ServiceLog.query.filter_by(request_id=request_id).first()
    labor_cost = service_log.labor_cost if service_log else 0
    parts_cost = data.get('parts_cost', 0)
    tax_rate = data.get('tax_rate', 0.18)  # Default 18% VAT

    subtotal = labor_cost + parts_cost
    tax_amount = subtotal * tax_rate
    discount = data.get('discount', 0)
    total_amount = subtotal + tax_amount - discount

    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=service_request.customer_id,
        issue_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        labor_cost=labor_cost,
        parts_cost=parts_cost,
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        discount=discount,
        status='sent',
        notes=data.get('notes')
    )

    # Link service request to invoice
    service_request.invoice_id = invoice.id

    db.session.add(invoice)
    db.session.commit()

    return jsonify({
        'message': 'Invoice created',
        'invoice': invoice.to_dict()
    }), 201


@invoicing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def list_invoices():
    """Get all invoices"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    customer_id = request.args.get('customer_id')

    query = Invoice.query

    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'invoices': [inv.to_dict() for inv in pagination.items]
    }), 200


@invoicing_bp.route('/invoices/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get invoice details"""
    invoice = Invoice.query.get(invoice_id)

    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    inv_data = invoice.to_dict()
    inv_data['payments'] = [p.to_dict() for p in invoice.payments]

    return jsonify(inv_data), 200


@invoicing_bp.route('/invoices/<invoice_id>/payments', methods=['POST'])
@jwt_required()
def record_payment(invoice_id):
    """Record payment for invoice"""
    invoice = Invoice.query.get(invoice_id)

    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    data = request.get_json()
    amount = data.get('amount')

    if not amount or amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_date=datetime.utcnow(),
        payment_method=data.get('payment_method', 'bank_transfer'),
        reference_number=data.get('reference_number'),
        status='completed'
    )

    # Update invoice status
    total_paid = sum(p.amount for p in invoice.payments) + amount

    if total_paid >= invoice.total_amount:
        invoice.status = 'paid'
    else:
        invoice.status = 'sent'

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        'message': 'Payment recorded',
        'payment': payment.to_dict(),
        'invoice': invoice.to_dict()
    }), 201


@invoicing_bp.route('/invoices/<invoice_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_invoice(invoice_id):
    """Cancel invoice"""
    invoice = Invoice.query.get(invoice_id)

    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    invoice.status = 'cancelled'
    db.session.commit()

    return jsonify({'message': 'Invoice cancelled'}), 200


@invoicing_bp.route('/reports/aging', methods=['GET'])
@jwt_required()
def get_aging_report():
    """Get accounts receivable aging report"""
    invoices = Invoice.query.filter(Invoice.status != 'paid').all()

    current = []
    days_30 = []
    days_60 = []
    days_90 = []

    now = datetime.utcnow()

    for inv in invoices:
        days_overdue = (now - inv.due_date).days if inv.due_date else 0

        if days_overdue <= 0:
            current.append(inv)
        elif days_overdue <= 30:
            days_30.append(inv)
        elif days_overdue <= 60:
            days_60.append(inv)
        else:
            days_90.append(inv)

    return jsonify({
        'current': {
            'count': len(current),
            'total': sum(inv.total_amount for inv in current)
        },
        'days_30': {
            'count': len(days_30),
            'total': sum(inv.total_amount for inv in days_30)
        },
        'days_60': {
            'count': len(days_60),
            'total': sum(inv.total_amount for inv in days_60)
        },
        'days_90': {
            'count': len(days_90),
            'total': sum(inv.total_amount for inv in days_90)
        }
    }), 200
