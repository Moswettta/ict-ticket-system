# ICT Ticket System

Full-stack IT helpdesk / ticket management system.

- **Backend**: Python 3 + Flask + PostgreSQL
- **Frontend**: AngularJS 1.8 + Bootstrap 5
- **Docker**: One-command startup with PostgreSQL

**Repo:** https://github.com/Moswettta/ict-ticket-system

---

## Features

| Module | Description |
|--------|-------------|
| **Tickets** | Users report computer problems → Admin approves/rejects → IT staff assigns & resolves |
| **Assets / Workdesk** | Laptops, printers, computer parts, full computers, monitors |
| **Preventive Maintenance** | Schedule maintenance with **expiry / next-due dates**; overdue alerts |
| **Dashboard** | Role-based statistics |
| **Sidebar + Profile** | Collapsible sidebar, avatar, profile editing |
| **Auth** | JWT login with roles: `user`, `it_staff`, `admin` |

### Demo Accounts (seeded automatically)

| Username | Password  | Role     |
|----------|-----------|----------|
| admin    | admin123  | Admin    |
| tech1    | tech123   | IT Staff |
| tech2    | tech123   | IT Staff |
| user1    | user123   | User     |
| user2    | user123   | User     |

---

## Quick Start with Docker (recommended)

```bash
git clone https://github.com/Moswettta/ict-ticket-system.git
cd ict-ticket-system
docker compose up --build -d
```

Open **http://localhost:5000**

```bash
docker compose logs -f web   # logs
docker compose down          # stop
docker compose down -v       # stop + delete DB volume
```

---

## Run Locally (without Docker)

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### Create database

```bash
sudo -u postgres psql -c "CREATE USER ict_user WITH PASSWORD 'ict_pass';"
sudo -u postgres psql -c "CREATE DATABASE ict_tickets OWNER ict_user;"
```

Or Docker Postgres only:

```bash
docker run -d --name ict-postgres \
  -e POSTGRES_USER=ict_user \
  -e POSTGRES_PASSWORD=ict_pass \
  -e POSTGRES_DB=ict_tickets \
  -p 5432:5432 postgres:16
```

### App setup

```bash
cd ict-ticket-system/backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python app.py
```

Open **http://localhost:5000**

Optional SQLite (no Postgres):

```
# in .env
DATABASE_URL=sqlite:///ict_tickets.db
```

---

## Deploy Online

### Render.com
1. New → Web Service → connect this repo
2. Build: `cd backend && pip install -r requirements.txt`
3. Start: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
4. Add PostgreSQL addon; set `DATABASE_URL` and `JWT_SECRET_KEY`
5. Shell: `cd backend && python init_db.py`

### Railway.app
1. Deploy from GitHub + add PostgreSQL plugin
2. `DATABASE_URL=${{Postgres.DATABASE_URL}}`, set `JWT_SECRET_KEY`
3. Start: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
4. Shell: `cd backend && python init_db.py`

### Heroku
```bash
heroku create your-app
heroku addons:create heroku-postgresql:essential-0
heroku config:set JWT_SECRET_KEY=your-long-secret
git push heroku main
heroku run "cd backend && python init_db.py"
```

### VPS (Nginx + Gunicorn)
See full guide in the repository README history or use Docker Compose on the server.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | `postgresql://user:pass@host:5432/dbname` |
| `JWT_SECRET_KEY` | Yes (prod) | Secret for JWT signing |
| `PORT` | Auto | Set by hosting platforms |

---

## Project Structure

```
ict-ticket-system/
├── backend/          # Flask API, models, seed
├── frontend/         # AngularJS SPA
├── Dockerfile
├── docker-compose.yml
├── Procfile
└── README.md
```

## License

MIT
