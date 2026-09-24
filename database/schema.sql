-- Jalankan di Supabase -> SQL Editor
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student','company','admin')),
  skills TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
  id SERIAL PRIMARY KEY,
  company_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(150) NOT NULL,
  description TEXT DEFAULT '',
  required_skills TEXT DEFAULT '',
  location VARCHAR(100),
  salary_range VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS applications (
  id SERIAL PRIMARY KEY,
  job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','accepted','rejected')),
  applied_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (job_id, user_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  score REAL DEFAULT 0,
  UNIQUE (user_id, job_id)
);

-- Untuk jadikan seseorang admin (selepas dia register):
-- UPDATE users SET role='admin' WHERE email='emel_anda@example.com';
