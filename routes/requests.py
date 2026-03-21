#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Service request routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import ServiceRequest, ServiceLog, Customer, Technician, User, Invoice
from datetime import datetime, timedelta
import uuid

requests_bp = Blueprint('requests', __name__)


@requests_bp.route('', methods=['POST'])
@jwt_required()
def create_service_request():
    """Create new service request"""
    data = request.get_json()

    # Generate request number
    request_number = f"REQ-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    service_request = ServiceRequest(
        request_number=request_number,
        customer_id=data['customer_id'],
        title=data['title'],
        description=data.get('description'),
        priority=data.get('priority', 'medium'),
        status='open',
        service_type=data.get('service_type', 'maintenance'),
        scheduled_date=datetime.fromisoformat(data['scheduled_date']) if data.get('scheduled_date') else None,
        scheduled_duration=data.get('scheduled_duration'),
        location_latitude=data.get('latitude'),
        location_longitude=data.get('longitude'),
        notes=data.get('notes')
    )

    # Calculate SLA end time
    customer = Customer.query.get(data['customer_id'])
    if customer.contracts:
        contract = customer.contracts[0]
        service_request.sla_end_time = datetime.utcnow() + timedelta(hours=contract.response_time_hours)

    db.session.add(service_request)
    db.session.commit()

    return jsonify({
        'message': 'Service request created',
        'request': service_request.to_dict()
    }), 201


@requests_bp.route('', methods=['GET'])
@jwt_required()
def list_service_requests():
    """Get all service requests"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    customer_id = request.args.get('customer_id')

    query = ServiceRequest.query

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'page': page,
        'requests': [r.to_dict() for r in pagination.items]
    }), 200


@requests_bp.route('/<request_id>', methods=['GET'])
@jwt_required()
def get_service_request(request_id):
    """Get service request details"""
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    request_data = service_request.to_dict()
    request_data['service_logs'] = [log.to_dict() for log in service_request.service_logs]

    return jsonify(request_data), 200


@requests_bp.route('/<request_id>', methods=['PUT'])
@jwt_required()
def update_service_request(request_id):
    """Update service request"""
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    data = request.get_json()

    if 'title' in data:
        service_request.title = data['title']
    if 'description' in data:
        service_request.description = data['description']
    if 'priority' in data:
        service_request.priority = data['priority']
    if 'status' in data:
        service_request.status = data['status']
        if data['status'] == 'completed' and not service_request.actual_end_time:
            service_request.actual_end_time = datetime.utcnow()
    if 'scheduled_date' in data:
        service_request.scheduled_date = datetime.fromisoformat(data['scheduled_date'])
    if 'technician_id' in data:
        service_request.technician_id = data['technician_id']
        if data['technician_id']:
            service_request.status = 'assigned'

    db.session.commit()

    return jsonify({
        'message': 'Request updated',
        'request': service_request.to_dict()
    }), 200


@requests_bp.route('/<request_id>/assign', methods=['POST'])
@jwt_required()
def assign_technician(request_id):
    """Assign technician to service request"""
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    data = request.get_json()
    technician_id = data.get('technician_id')

    if not technician_id:
        return jsonify({'error': 'technician_id required'}), 400

    technician = Technician.query.get(technician_id)
    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    service_request.technician_id = technician_id
    service_request.status = 'assigned'

    db.session.commit()

    return jsonify({
        'message': 'Technician assigned',
        'request': service_request.to_dict()
    }), 200


@requests_bp.route('/<request_id>/start', methods=['POST'])
@jwt_required()
def start_service(request_id):
    """Start service work"""
    user_id = get_jwt_identity()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    service_request.status = 'in_progress'
    service_request.actual_start_time = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Service started',
        'request': service_request.to_dict()
    }), 200


@requests_bp.route('/<request_id>/complete', methods=['POST'])
@jwt_required()
def complete_service(request_id):
    """Complete service request"""
    user_id = get_jwt_identity()
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    data = request.get_json()

    service_request.status = 'completed'
    service_request.actual_end_time = datetime.utcnow()
    service_request.notes = data.get('notes')
    service_request.parts_used = data.get('parts_used')

    # Create service log
    if service_request.actual_start_time:
        duration = (service_request.actual_end_time - service_request.actual_start_time).total_seconds() / 3600

        service_log = ServiceLog(
            request_id=request_id,
            technician_id=service_request.technician_id,
            start_time=service_request.actual_start_time,
            end_time=service_request.actual_end_time,
            duration_hours=duration,
            labor_cost=service_request.technician.hourly_rate * duration if service_request.technician else 0,
            work_description=data.get('work_description')
        )
        db.session.add(service_log)

    db.session.commit()

    return jsonify({
        'message': 'Service completed',
        'request': service_request.to_dict()
    }), 200


@requests_bp.route('/<request_id>/rate', methods=['POST'])
@jwt_required()
def rate_service(request_id):
    """Rate completed service"""
    data = request.get_json()

    # Get service log
    service_log = ServiceLog.query.filter_by(request_id=request_id).first()
    if not service_log:
        return jsonify({'error': 'Service log not found'}), 404

    service_log.rating = data.get('rating')
    service_log.customer_feedback = data.get('feedback')

    # Update technician rating
    if service_log.technician:
        service_log.technician.rating = (service_log.technician.rating + data.get('rating', 5)) / 2

    db.session.commit()

    return jsonify({'message': 'Service rated successfully'}), 200


@requests_bp.route('/<request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_service_request(request_id):
    """Cancel service request"""
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'error': 'Request not found'}), 404

    service_request.status = 'cancelled'
    db.session.commit()

    return jsonify({'message': 'Request cancelled'}), 200


@requests_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_requests():
    """Get overdue service requests"""
    now = datetime.utcnow()

    overdue = ServiceRequest.query.filter(
        ServiceRequest.sla_end_time < now,
        ServiceRequest.status != 'completed'
    ).all()

    return jsonify([r.to_dict() for r in overdue]), 200
