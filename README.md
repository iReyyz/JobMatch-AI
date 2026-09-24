# JobMatch AI – Internship & Job Matching System

Web app untuk student cari/mohon internship & job, company post job & urus applicant,
dan sistem cadangan job berdasarkan skills (keyword matching scoring). Admin urus user & job.

**Stack:** Python · Flask · Flask-SQLAlchemy · Supabase (PostgreSQL) · HTML/CSS/JS · Bootstrap 5

## Setup (Windows / VSCode)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
copy .env.example .env      # isi DATABASE_URL & SECRET_KEY
```
1. Buat project di [supabase.com](https://supabase.com)
2. Supabase → SQL Editor → paste & run `database/schema.sql`
3. Run: `cd backend` → `python app.py` → buka http://localhost:5000

Semak sambungan DB: http://localhost:5000/api/health

## Struktur
```
backend/   Flask API (routes, models, services, config)
frontend/  HTML, CSS, JS (dihidang oleh Flask)
database/  schema.sql
```

## Scoring cadangan
`score = (skills user ∩ required_skills job) / jumlah required_skills × 100`

## Roles
- `student`, `company` – boleh daftar sendiri
- `admin` – set manual: `UPDATE users SET role='admin' WHERE email='...';`
