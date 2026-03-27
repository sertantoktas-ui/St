#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enterprise Servis Yönetim Sistemi - Backend API
Professional Service Management System - Flask REST API
"""

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/service_management'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400 * 30  # 30 days

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Import models
    from models import (
        User, Customer, Technician, ServiceRequest,
        ServiceLog, Invoice, Payment, Inventory, Part
    )

    # Register blueprints
    from routes.auth import auth_bp
    from routes.customers import customers_bp
    from routes.technicians import technicians_bp
    from routes.requests import requests_bp
    from routes.invoicing import invoicing_bp
    from routes.inventory import inventory_bp
    from routes.analytics import analytics_bp
    from routes.world_clock import world_clock_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(technicians_bp, url_prefix='/api/technicians')
    app.register_blueprint(requests_bp, url_prefix='/api/requests')
    app.register_blueprint(invoicing_bp, url_prefix='/api/invoicing')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(world_clock_bp, url_prefix='/api/clock')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500

    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'service': 'Service Management API'}), 200

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
