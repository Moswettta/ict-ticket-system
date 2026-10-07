from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta, date
from models import db, User, Ticket, Asset, Maintenance
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Load .env if present (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Database: PostgreSQL by default; falls back to SQLite only if DATABASE_URL is unset
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://ict_user:ict_pass@localhost:5432/ict_tickets'
)
# Heroku / some hosts use postgres:// — SQLAlchemy needs postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY',
    'ict-ticket-system-secret-key-change-in-production'
)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

CORS(app)
db.init_app(app)
jwt = JWTManager(app)


# ---------- Helpers ----------
def role_required(roles):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


# ---------- Auth Routes ----------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['username', 'email', 'password', 'full_name']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data.get('role', 'user'),
        department=data.get('department'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


# ---------- User / Profile ----------
@app.route('/api/users', methods=['GET'])
@role_required(['admin', 'it_staff'])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current = get_current_user()
    if current.role not in ['admin', 'it_staff'] and current.id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current = get_current_user()
    if current.role != 'admin' and current.id != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if current.role == 'admin':
        for field in ['full_name', 'email', 'department', 'phone', 'role', 'is_active']:
            if field in data:
                setattr(user, field, data[field])
    else:
        for field in ['full_name', 'email', 'department', 'phone']:
            if field in data:
                setattr(user, field, data[field])

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    db.session.commit()
    return jsonify(user.to_dict())


# ---------- Tickets ----------
@app.route('/api/tickets', methods=['GET'])
@jwt_required()
def list_tickets():
    user = get_current_user()
    status = request.args.get('status')
    query = Ticket.query

    if user.role == 'user':
        query = query.filter_by(created_by=user.id)
    elif user.role == 'it_staff':
        query = query.filter(
            (Ticket.assigned_to == user.id) | (Ticket.status.in_(['approved', 'in_progress']))
        )

    if status:
        query = query.filter_by(status=status)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets])


@app.route('/api/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    user = get_current_user()
    data = request.get_json()
    required = ['title', 'description', 'category']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    ticket = Ticket(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        priority=data.get('priority', 'medium'),
        created_by=user.id,
        asset_id=data.get('asset_id')
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket.to_dict()), 201


@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = get_current_user()
    if user.role == 'user' and ticket.created_by != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(ticket.to_dict())


@app.route('/api/tickets/<int:ticket_id>/approve', methods=['POST'])
@role_required(['admin'])
def approve_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    action = data.get('action', 'approve')

    if action == 'approve':
        ticket.status = 'approved'
        ticket.approved_by = get_current_user().id
        ticket.approved_at = datetime.utcnow()
        ticket.admin_notes = data.get('notes')
    elif action == 'reject':
        ticket.status = 'rejected'
        ticket.admin_notes = data.get('notes', 'Rejected by admin')
    else:
        return jsonify({'error': 'Invalid action'}), 400

    db.session.commit()
    return jsonify(ticket.to_dict())


@app.route('/api/tickets/<int:ticket_id>/assign', methods=['POST'])
@role_required(['admin', 'it_staff'])
def assign_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()

    if 'assigned_to' in data:
        ticket.assigned_to = data['assigned_to']
    if 'asset_id' in data:
        asset = Asset.query.get(data['asset_id'])
        if asset:
            ticket.asset_id = asset.id
            if asset.status == 'available':
                asset.status = 'assigned'
                asset.assigned_to_user_id = ticket.created_by
    if data.get('status'):
        ticket.status = data['status']
    if data.get('resolution_notes'):
        ticket.resolution_notes = data['resolution_notes']
        if data.get('status') == 'resolved':
            ticket.resolved_at = datetime.utcnow()

    db.session.commit()
    return jsonify(ticket.to_dict())


@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = get_current_user()
    data = request.get_json()

    if user.role == 'user' and ticket.created_by != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    if user.role in ['admin', 'it_staff']:
        for field in ['title', 'description', 'category', 'priority', 'status', 'resolution_notes', 'admin_notes']:
            if field in data:
                setattr(ticket, field, data[field])
        if data.get('status') == 'resolved' and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
    else:
        if ticket.status != 'pending':
            return jsonify({'error': 'Cannot edit ticket after submission'}), 400
        for field in ['title', 'description', 'category', 'priority']:
            if field in data:
                setattr(ticket, field, data[field])

    db.session.commit()
    return jsonify(ticket.to_dict())


# ---------- Assets (Workdesk) ----------
@app.route('/api/assets', methods=['GET'])
@jwt_required()
def list_assets():
    asset_type = request.args.get('type')
    status = request.args.get('status')
    query = Asset.query
    if asset_type:
        query = query.filter_by(asset_type=asset_type)
    if status:
        query = query.filter_by(status=status)
    assets = query.order_by(Asset.created_at.desc()).all()
    return jsonify([a.to_dict() for a in assets])


@app.route('/api/assets', methods=['POST'])
@role_required(['admin', 'it_staff'])
def create_asset():
    data = request.get_json()
    if not data.get('name') or not data.get('asset_type'):
        return jsonify({'error': 'Name and asset_type required'}), 400

    asset = Asset(
        name=data['name'],
        asset_type=data['asset_type'],
        serial_number=data.get('serial_number'),
        model=data.get('model'),
        status=data.get('status', 'available'),
        location=data.get('location'),
        notes=data.get('notes')
    )
    if data.get('purchase_date'):
        asset.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()

    db.session.add(asset)
    db.session.commit()
    return jsonify(asset.to_dict()), 201


@app.route('/api/assets/<int:asset_id>', methods=['PUT'])
@role_required(['admin', 'it_staff'])
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json()
    for field in ['name', 'asset_type', 'serial_number', 'model', 'status', 'location', 'notes']:
        if field in data:
            setattr(asset, field, data[field])
    if 'assigned_to_user_id' in data:
        asset.assigned_to_user_id = data['assigned_to_user_id']
        if data['assigned_to_user_id']:
            asset.status = 'assigned'
        else:
            asset.status = 'available'
    if data.get('purchase_date'):
        asset.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(asset.to_dict())


@app.route('/api/assets/<int:asset_id>/assign', methods=['POST'])
@role_required(['admin', 'it_staff'])
def assign_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json()
    user_id = data.get('user_id')
    if user_id:
        user = User.query.get_or_404(user_id)
        asset.assigned_to_user_id = user.id
        asset.status = 'assigned'
    else:
        asset.assigned_to_user_id = None
        asset.status = 'available'
    db.session.commit()
    return jsonify(asset.to_dict())


# ---------- Maintenance (Preventive with Expiry) ----------
@app.route('/api/maintenances', methods=['GET'])
@jwt_required()
def list_maintenances():
    status = request.args.get('status')
    expired_only = request.args.get('expired') == 'true'
    query = Maintenance.query
    if status:
        query = query.filter_by(status=status)
    maintenances = query.order_by(Maintenance.next_due_date.asc()).all()

    result = []
    for m in maintenances:
        d = m.to_dict()
        if expired_only and not d['is_expired']:
            continue
        if m.next_due_date and m.next_due_date < date.today() and m.status != 'completed':
            m.status = 'overdue'
            db.session.commit()
            d['status'] = 'overdue'
            d['is_expired'] = True
        result.append(d)
    return jsonify(result)


@app.route('/api/maintenances', methods=['POST'])
@role_required(['admin', 'it_staff'])
def create_maintenance():
    data = request.get_json()
    required = ['asset_id', 'scheduled_date']
    if not all(k in data for k in required):
        return jsonify({'error': 'asset_id and scheduled_date required'}), 400

    maint = Maintenance(
        asset_id=data['asset_id'],
        maintenance_type=data.get('maintenance_type', 'preventive'),
        description=data.get('description'),
        scheduled_date=datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date(),
        notes=data.get('notes')
    )
    if data.get('next_due_date'):
        maint.next_due_date = datetime.strptime(data['next_due_date'], '%Y-%m-%d').date()
    else:
        maint.next_due_date = maint.scheduled_date + timedelta(days=180)

    db.session.add(maint)
    db.session.commit()
    return jsonify(maint.to_dict()), 201


@app.route('/api/maintenances/<int:maint_id>', methods=['PUT'])
@role_required(['admin', 'it_staff'])
def update_maintenance(maint_id):
    maint = Maintenance.query.get_or_404(maint_id)
    data = request.get_json()
    for field in ['description', 'status', 'notes', 'maintenance_type']:
        if field in data:
            setattr(maint, field, data[field])
    if data.get('completed_date'):
        maint.completed_date = datetime.strptime(data['completed_date'], '%Y-%m-%d').date()
        maint.status = 'completed'
    if data.get('next_due_date'):
        maint.next_due_date = datetime.strptime(data['next_due_date'], '%Y-%m-%d').date()
    if data.get('performed_by'):
        maint.performed_by = data['performed_by']
    db.session.commit()
    return jsonify(maint.to_dict())


@app.route('/api/maintenances/expiring', methods=['GET'])
@jwt_required()
def expiring_maintenances():
    today = date.today()
    threshold = today + timedelta(days=30)
    maints = Maintenance.query.filter(
        Maintenance.next_due_date != None,
        Maintenance.status != 'completed'
    ).all()
    result = []
    for m in maints:
        if m.next_due_date <= threshold:
            d = m.to_dict()
            result.append(d)
    return jsonify(sorted(result, key=lambda x: x['next_due_date'] or ''))


# ---------- Dashboard Stats ----------
@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    user = get_current_user()
    stats = {}

    if user.role == 'admin':
        stats = {
            'total_tickets': Ticket.query.count(),
            'pending_tickets': Ticket.query.filter_by(status='pending').count(),
            'approved_tickets': Ticket.query.filter_by(status='approved').count(),
            'in_progress': Ticket.query.filter_by(status='in_progress').count(),
            'resolved': Ticket.query.filter_by(status='resolved').count(),
            'total_users': User.query.count(),
            'total_assets': Asset.query.count(),
            'available_assets': Asset.query.filter_by(status='available').count(),
            'overdue_maintenance': Maintenance.query.filter_by(status='overdue').count(),
            'expiring_soon': Maintenance.query.filter(
                Maintenance.next_due_date <= date.today() + timedelta(days=30),
                Maintenance.status != 'completed'
            ).count()
        }
    elif user.role == 'it_staff':
        stats = {
            'my_assigned': Ticket.query.filter_by(assigned_to=user.id).count(),
            'open_tickets': Ticket.query.filter(Ticket.status.in_(['approved', 'in_progress'])).count(),
            'resolved_by_me': Ticket.query.filter_by(assigned_to=user.id, status='resolved').count(),
            'assets_to_maintain': Maintenance.query.filter(
                Maintenance.status.in_(['scheduled', 'overdue'])
            ).count()
        }
    else:
        stats = {
            'my_tickets': Ticket.query.filter_by(created_by=user.id).count(),
            'pending': Ticket.query.filter_by(created_by=user.id, status='pending').count(),
            'in_progress': Ticket.query.filter_by(created_by=user.id, status='in_progress').count(),
            'resolved': Ticket.query.filter_by(created_by=user.id, status='resolved').count()
        }
    return jsonify(stats)


# ---------- Serve Frontend ----------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


# ---------- Seed Data ----------
def seed_data():
    if User.query.first():
        return

    admin = User(username='admin', email='admin@ict.com', full_name='System Administrator',
                 role='admin', department='ICT')
    admin.set_password('admin123')
    db.session.add(admin)

    it1 = User(username='tech1', email='tech1@ict.com', full_name='John Technician',
               role='it_staff', department='ICT Support')
    it1.set_password('tech123')
    db.session.add(it1)

    it2 = User(username='tech2', email='tech2@ict.com', full_name='Sarah Support',
               role='it_staff', department='ICT Support')
    it2.set_password('tech123')
    db.session.add(it2)

    u1 = User(username='user1', email='user1@company.com', full_name='Alice Employee',
              role='user', department='Finance')
    u1.set_password('user123')
    db.session.add(u1)

    u2 = User(username='user2', email='user2@company.com', full_name='Bob Worker',
              role='user', department='HR')
    u2.set_password('user123')
    db.session.add(u2)

    db.session.commit()

    assets_data = [
        {'name': 'Dell Latitude 5420', 'asset_type': 'laptop', 'serial_number': 'DL5420-001', 'model': 'Latitude 5420', 'location': 'Store Room A'},
        {'name': 'HP LaserJet Pro', 'asset_type': 'printer', 'serial_number': 'HP-LJ-100', 'model': 'M404dn', 'location': 'Floor 2'},
        {'name': 'Desktop PC - Office 12', 'asset_type': 'full_computer', 'serial_number': 'PC-OFF12', 'model': 'OptiPlex 7090', 'location': 'Office 12'},
        {'name': 'RAM 16GB DDR4', 'asset_type': 'computer_parts', 'serial_number': 'RAM-16-001', 'model': 'Kingston 16GB', 'location': 'Parts Cabinet'},
        {'name': 'SSD 512GB', 'asset_type': 'computer_parts', 'serial_number': 'SSD-512-01', 'model': 'Samsung 870', 'location': 'Parts Cabinet'},
        {'name': 'Monitor 24" Dell', 'asset_type': 'monitor', 'serial_number': 'MON-24-05', 'model': 'P2422H', 'location': 'Store Room B'},
        {'name': 'Lenovo ThinkPad T14', 'asset_type': 'laptop', 'serial_number': 'LT-T14-003', 'model': 'ThinkPad T14', 'location': 'Store Room A'},
        {'name': 'Canon ImageRunner', 'asset_type': 'printer', 'serial_number': 'CN-IR-200', 'model': 'C3525i', 'location': 'Reception'},
    ]
    for a in assets_data:
        asset = Asset(**a)
        db.session.add(asset)
    db.session.commit()

    t1 = Ticket(title='Laptop not powering on', description='My work laptop suddenly stopped turning on. No lights, no fan.',
                category='hardware', priority='high', created_by=u1.id, status='pending')
    t2 = Ticket(title='Printer paper jam', description='The shared printer on floor 2 keeps jamming.',
                category='hardware', priority='medium', created_by=u2.id, status='pending')
    t3 = Ticket(title='Cannot connect to WiFi', description='Laptop shows limited connectivity on company WiFi.',
                category='network', priority='high', created_by=u1.id, status='approved',
                approved_by=admin.id, approved_at=datetime.utcnow(), assigned_to=it1.id)
    db.session.add_all([t1, t2, t3])
    db.session.commit()

    assets = Asset.query.all()
    today = date.today()
    m1 = Maintenance(asset_id=assets[0].id, maintenance_type='preventive',
                     description='Quarterly cleaning and health check',
                     scheduled_date=today - timedelta(days=10),
                     next_due_date=today + timedelta(days=5),
                     status='scheduled')
    m2 = Maintenance(asset_id=assets[1].id, maintenance_type='preventive',
                     description='Toner and roller replacement',
                     scheduled_date=today - timedelta(days=60),
                     next_due_date=today - timedelta(days=5),
                     status='overdue')
    m3 = Maintenance(asset_id=assets[2].id, maintenance_type='preventive',
                     description='Dust cleaning and OS update',
                     scheduled_date=today + timedelta(days=20),
                     next_due_date=today + timedelta(days=200),
                     status='scheduled')
    db.session.add_all([m1, m2, m3])
    db.session.commit()
    print('Seed data created successfully!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
