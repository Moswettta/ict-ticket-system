from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user, it_staff, admin
    department = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    avatar = db.Column(db.String(255), default='default.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets_created = db.relationship('Ticket', backref='creator', lazy=True, foreign_keys='Ticket.created_by')
    tickets_assigned = db.relationship('Ticket', backref='assignee', lazy=True, foreign_keys='Ticket.assigned_to')

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
            'role': self.role,
            'department': self.department,
            'phone': self.phone,
            'avatar': self.avatar,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # laptop, printer, computer_parts, full_computer, monitor, other
    serial_number = db.Column(db.String(100), unique=True)
    model = db.Column(db.String(100))
    status = db.Column(db.String(30), default='available')  # available, assigned, maintenance, retired
    location = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_user = db.relationship('User', backref='assigned_assets')
    maintenances = db.relationship('Maintenance', backref='asset', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'asset_type': self.asset_type,
            'serial_number': self.serial_number,
            'model': self.model,
            'status': self.status,
            'location': self.location,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'assigned_to_user_id': self.assigned_to_user_id,
            'assigned_to': self.assigned_user.full_name if self.assigned_user else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # hardware, software, network, other
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(30), default='pending')  # pending, approved, in_progress, resolved, rejected, closed
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    resolution_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = db.relationship('Asset', backref='tickets')
    approver = db.relationship('User', foreign_keys=[approved_by])

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'assigned_to': self.assigned_to,
            'assignee_name': self.assignee.full_name if self.assignee else None,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'asset_type': self.asset.asset_type if self.asset else None,
            'resolution_notes': self.resolution_notes,
            'admin_notes': self.admin_notes,
            'approved_by': self.approved_by,
            'approver_name': self.approver.full_name if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Maintenance(db.Model):
    __tablename__ = 'maintenances'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), default='preventive')  # preventive, corrective
    description = db.Column(db.Text)
    scheduled_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date)
    next_due_date = db.Column(db.Date)  # Expiry / next preventive maintenance date
    status = db.Column(db.String(30), default='scheduled')  # scheduled, in_progress, completed, overdue
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    performer = db.relationship('User', backref='performed_maintenances')

    def is_expired(self):
        if self.next_due_date:
            return datetime.utcnow().date() > self.next_due_date
        return False

    def days_until_due(self):
        if self.next_due_date:
            delta = self.next_due_date - datetime.utcnow().date()
            return delta.days
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'asset_type': self.asset.asset_type if self.asset else None,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'status': self.status,
            'is_expired': self.is_expired(),
            'days_until_due': self.days_until_due(),
            'performed_by': self.performed_by,
            'performer_name': self.performer.full_name if self.performer else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
