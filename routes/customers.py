#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Customer management routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Customer, User, ServiceRequest
from sqlalchemy import func

customers_bp = Blueprint('customers', __name__)


@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """Create new customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Create customer user account
    customer_user = User(
        username=data.get('email'),
        email=data['email'],
        full_name=data['company_name'],
        phone=data.get('phone'),
        role='customer',
        is_active=True
    )
    customer_user.set_password(data.get('password', 'defaultpassword123'))

    db.session.add(customer_user)
    db.session.flush()

    # Create customer record
    customer = Customer(
        user_id=customer_user.id,
        company_name=data['company_name'],
        contact_person=data.get('contact_person'),
        phone=data['phone'],
        email=data['email'],
        address=data.get('address'),
        city=data.get('city'),
        zip_code=data.get('zip_code'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        tax_id=data.get('tax_id'),
        industry=data.get('industry'),
        status='active'
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify({
        'message': 'Customer created successfully',
        'customer': customer.to_dict()
    }), 201


@customers_bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    """Get all customers"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')

    query = Customer.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'customers': [c.to_dict() for c in pagination.items]
    }), 200


@customers_bp.route('/<customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get customer details"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    customer_data = customer.to_dict()

    # Add service requests count
    customer_data['total_requests'] = len(customer.service_requests)
    customer_data['completed_requests'] = len([r for r in customer.service_requests if r.status == 'completed'])

    # Add invoices count
    customer_data['total_invoices'] = len(customer.invoices)

    return jsonify(customer_data), 200


@customers_bp.route('/<customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    if user.role not in ['admin', 'manager'] and user_id != customer.user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'company_name' in data:
        customer.company_name = data['company_name']
    if 'contact_person' in data:
        customer.contact_person = data['contact_person']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    if 'city' in data:
        customer.city = data['city']
    if 'zip_code' in data:
        customer.zip_code = data['zip_code']
    if 'latitude' in data:
        customer.latitude = data['latitude']
    if 'longitude' in data:
        customer.longitude = data['longitude']
    if 'status' in data:
        customer.status = data['status']

    db.session.commit()

    return jsonify({
        'message': 'Customer updated successfully',
        'customer': customer.to_dict()
    }), 200


@customers_bp.route('/<customer_id>/requests', methods=['GET'])
@jwt_required()
def get_customer_requests(customer_id):
    """Get service requests for a customer"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    status_filter = request.args.get('status')
    query = ServiceRequest.query.filter_by(customer_id=customer_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    requests = query.all()

    return jsonify([r.to_dict() for r in requests]), 200


@customers_bp.route('/<customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """Delete customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Don't actually delete, just deactivate
    customer.status = 'inactive'
    db.session.commit()

    return jsonify({'message': 'Customer deactivated successfully'}), 200
