from datetime import datetime, timezone
from . import db


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    skills = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email,
                "role": self.role, "skills": self.skills}


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    required_skills = db.Column(db.Text, default="")
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    company = db.relationship("User")

    def to_dict(self):
        return {"id": self.id, "company_id": self.company_id, "company": self.company.name,
                "title": self.title, "description": self.description,
                "required_skills": self.required_skills, "location": self.location,
                "salary_range": self.salary_range}


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    applied_at = db.Column(db.DateTime(timezone=True), default=now)
    job = db.relationship("Job")
    user = db.relationship("User")
    __table_args__ = (db.UniqueConstraint("job_id", "user_id"),)


class Recommendation(db.Model):
    __tablename__ = "recommendations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Float, default=0)
    __table_args__ = (db.UniqueConstraint("user_id", "job_id"),)
