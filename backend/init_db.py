"""Initialize database tables and seed demo data."""
from app import app, db, seed_data

if __name__ == '__main__':
    with app.app_context():
        print('Creating tables...')
        db.create_all()
        print('Seeding demo data...')
        seed_data()
        print('Done! Database is ready.')
