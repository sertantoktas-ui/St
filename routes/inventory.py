#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inventory management routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Inventory, Part

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/parts', methods=['POST'])
@jwt_required()
def create_part():
    """Create new part/component"""
    data = request.get_json()

    part = Part(
        part_number=data['part_number'],
        name=data['name'],
        description=data.get('description'),
        category=data.get('category'),
        supplier=data.get('supplier'),
        cost=data.get('cost'),
        selling_price=data.get('selling_price'),
        unit=data.get('unit', 'pcs')
    )

    db.session.add(part)
    db.session.flush()

    # Create inventory record
    inventory = Inventory(
        part_id=part.id,
        quantity=data.get('quantity', 0),
        location=data.get('location'),
        min_quantity=data.get('min_quantity', 0),
        max_quantity=data.get('max_quantity', 100)
    )

    db.session.add(inventory)
    db.session.commit()

    return jsonify({
        'message': 'Part created',
        'part': part.to_dict()
    }), 201


@inventory_bp.route('/parts', methods=['GET'])
@jwt_required()
def list_parts():
    """Get all parts"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    search = request.args.get('search')

    query = Part.query

    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Part.name.ilike(f'%{search}%'))

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'parts': [p.to_dict() for p in pagination.items]
    }), 200


@inventory_bp.route('/inventory', methods=['GET'])
@jwt_required()
def list_inventory():
    """Get inventory status"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    low_stock = request.args.get('low_stock', type=bool)

    query = Inventory.query

    if low_stock:
        query = query.filter(Inventory.quantity < Inventory.min_quantity)

    pagination = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'total': pagination.total,
        'inventory': [inv.to_dict() for inv in pagination.items]
    }), 200


@inventory_bp.route('/inventory/<inventory_id>/adjust', methods=['POST'])
@jwt_required()
def adjust_quantity(inventory_id):
    """Adjust inventory quantity"""
    inventory = Inventory.query.get(inventory_id)

    if not inventory:
        return jsonify({'error': 'Inventory not found'}), 404

    data = request.get_json()
    quantity = data.get('quantity')

    if quantity is None:
        return jsonify({'error': 'quantity required'}), 400

    inventory.quantity = quantity

    db.session.commit()

    return jsonify({
        'message': 'Inventory adjusted',
        'inventory': inventory.to_dict()
    }), 200


@inventory_bp.route('/inventory/<inventory_id>/restock', methods=['POST'])
@jwt_required()
def restock(inventory_id):
    """Record restocking"""
    from datetime import datetime

    inventory = Inventory.query.get(inventory_id)

    if not inventory:
        return jsonify({'error': 'Inventory not found'}), 404

    data = request.get_json()
    quantity_added = data.get('quantity_added')

    if not quantity_added or quantity_added <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400

    inventory.quantity += quantity_added
    inventory.last_restocked = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': 'Restocked successfully',
        'inventory': inventory.to_dict()
    }), 200


@inventory_bp.route('/inventory/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock():
    """Get items with low stock"""
    low_stock_items = Inventory.query.filter(
        Inventory.quantity < Inventory.min_quantity
    ).all()

    return jsonify([inv.to_dict() for inv in low_stock_items]), 200


@inventory_bp.route('/inventory/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all inventory categories"""
    categories = db.session.query(Part.category).distinct().all()

    return jsonify([cat[0] for cat in categories if cat[0]]), 200
