#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Technician management routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Technician, User, ServiceRequest
from sqlalchemy import func
from datetime import datetime

technicians_bp = Blueprint('technicians', __name__)


@technicians_bp.route('', methods=['POST'])
@jwt_required()
def create_technician():
    """Create new technician"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Create technician user account
    tech_user = User(
        username=data.get('email'),
        email=data['email'],
        full_name=data['full_name'],
        phone=data.get('phone'),
        role='technician',
        is_active=True
    )
    tech_user.set_password(data.get('password', 'defaultpassword123'))

    db.session.add(tech_user)
    db.session.flush()

    # Create technician record
    technician = Technician(
        user_id=tech_user.id,
        specialization=data.get('specialization'),
        license_number=data.get('license_number'),
        certification=data.get('certification'),
        hourly_rate=data.get('hourly_rate', 0),
        vehicle=data.get('vehicle'),
        status='available'
    )

    db.session.add(technician)
    db.session.commit()

    return jsonify({
        'message': 'Technician created successfully',
        'technician': technician.to_dict()
    }), 201


@technicians_bp.route('', methods=['GET'])
@jwt_required()
def list_technicians():
    """Get all technicians"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    specialization = request.args.get('specialization')

    query = Technician.query
    if status:
        query = query.filter_by(status=status)
    if specialization:
        query = query.filter_by(specialization=specialization)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'technicians': [t.to_dict() for t in pagination.items]
    }), 200


@technicians_bp.route('/<technician_id>', methods=['GET'])
@jwt_required()
def get_technician(technician_id):
    """Get technician details"""
    technician = Technician.query.get(technician_id)

    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    tech_data = technician.to_dict()

    # Add assignments
    tech_data['active_assignments'] = len([r for r in technician.assignments if r.status in ['assigned', 'in_progress']])
    tech_data['completed_assignments'] = len([r for r in technician.assignments if r.status == 'completed'])

    return jsonify(tech_data), 200


@technicians_bp.route('/<technician_id>', methods=['PUT'])
@jwt_required()
def update_technician(technician_id):
    """Update technician"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    technician = Technician.query.get(technician_id)
    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    if user.role not in ['admin', 'manager'] and user_id != technician.user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'specialization' in data:
        technician.specialization = data['specialization']
    if 'hourly_rate' in data:
        technician.hourly_rate = data['hourly_rate']
    if 'vehicle' in data:
        technician.vehicle = data['vehicle']
    if 'status' in data:
        technician.status = data['status']

    db.session.commit()

    return jsonify({
        'message': 'Technician updated successfully',
        'technician': technician.to_dict()
    }), 200


@technicians_bp.route('/<technician_id>/location', methods=['POST'])
@jwt_required()
def update_location(technician_id):
    """Update technician location (GPS)"""
    user_id = get_jwt_identity()
    technician = Technician.query.get(technician_id)

    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    if user_id != technician.user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'latitude' in data and 'longitude' in data:
        technician.latitude = data['latitude']
        technician.longitude = data['longitude']
        technician.last_location_update = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Location updated',
            'location': {'lat': technician.latitude, 'lng': technician.longitude}
        }), 200

    return jsonify({'error': 'Invalid location data'}), 400


@technicians_bp.route('/<technician_id>/assignments', methods=['GET'])
@jwt_required()
def get_technician_assignments(technician_id):
    """Get service requests assigned to technician"""
    technician = Technician.query.get(technician_id)

    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    status_filter = request.args.get('status')
    query = ServiceRequest.query.filter_by(technician_id=technician_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    requests = query.all()

    return jsonify([r.to_dict() for r in requests]), 200


@technicians_bp.route('/<technician_id>/stats', methods=['GET'])
@jwt_required()
def get_technician_stats(technician_id):
    """Get technician statistics"""
    technician = Technician.query.get(technician_id)

    if not technician:
        return jsonify({'error': 'Technician not found'}), 404

    total_requests = len(technician.assignments)
    completed_requests = len([r for r in technician.assignments if r.status == 'completed'])
    active_requests = len([r for r in technician.assignments if r.status in ['assigned', 'in_progress']])

    return jsonify({
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'active_requests': active_requests,
        'completion_rate': (completed_requests / total_requests * 100) if total_requests > 0 else 0,
        'rating': technician.rating,
        'total_hours': technician.total_hours,
        'status': technician.status
    }), 200


@technicians_bp.route('/search', methods=['GET'])
@jwt_required()
def search_technicians():
    """Search available technicians by location and specialization"""
    data = request.args

    # Get search parameters
    latitude = data.get('latitude', type=float)
    longitude = data.get('longitude', type=float)
    radius = data.get('radius', 10, type=float)  # km
    specialization = data.get('specialization')
    status = data.get('status', 'available')

    query = Technician.query.filter_by(status=status)

    if specialization:
        query = query.filter(Technician.specialization.ilike(f'%{specialization}%'))

    technicians = query.all()

    # Simple distance calculation (Haversine formula could be better)
    results = []
    for tech in technicians:
        if tech.latitude and tech.longitude and latitude and longitude:
            # Approximate distance in km (simplified)
            distance = ((tech.latitude - latitude)**2 + (tech.longitude - longitude)**2)**0.5 * 111
            if distance <= radius:
                tech_data = tech.to_dict()
                tech_data['distance'] = round(distance, 2)
                results.append(tech_data)
        else:
            results.append(tech.to_dict())

    return jsonify(results), 200
