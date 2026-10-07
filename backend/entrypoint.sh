#!/bin/sh
set -e
echo "Waiting for database..."
python -c "
import time, os
from sqlalchemy import create_engine, text
url = os.environ.get('DATABASE_URL', 'postgresql://ict_user:ict_pass@db:5432/ict_tickets')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
for i in range(30):
    try:
        e = create_engine(url)
        with e.connect() as c:
            c.execute(text('SELECT 1'))
        print('Database is ready!')
        break
    except Exception as ex:
        print(f'Waiting... ({i+1}/30) {ex}')
        time.sleep(2)
else:
    print('Database not available, continuing anyway...')
"

echo "Initializing database..."
python init_db.py || true

echo "Starting gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:5000 --workers 2
