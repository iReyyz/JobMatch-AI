from flask import Blueprint, request, jsonify
from models import db, Job, Application
from services.auth_utils import role_required
from services.matching import recommend_for

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api")


@jobs_bp.get("/jobs")
def list_jobs():
    q = (request.args.get("q") or "").strip()
    query = Job.query
    if q:
        like = f"%{q}%"
        query = query.filter(Job.title.ilike(like) | Job.required_skills.ilike(like) | Job.location.ilike(like))
    return jsonify([j.to_dict() for j in query.order_by(Job.created_at.desc()).all()])


@jobs_bp.post("/jobs")
@role_required("company")
def create_job(user):
    d = request.get_json() or {}
    if not d.get("title"):
        return jsonify(error="Title wajib"), 400
    j = Job(company_id=user.id, title=d["title"], description=d.get("description", ""),
            required_skills=d.get("required_skills", ""), location=d.get("location"),
            salary_range=d.get("salary_range"))
    db.session.add(j)
    db.session.commit()
    return jsonify(j.to_dict()), 201


@jobs_bp.delete("/jobs/<int:job_id>")
@role_required("company", "admin")
def delete_job(user, job_id):
    j = db.get_or_404(Job, job_id)
    if user.role != "admin" and j.company_id != user.id:
        return jsonify(error="Bukan job anda"), 403
    db.session.delete(j)
    db.session.commit()
    return jsonify(ok=True)


@jobs_bp.get("/company/jobs")
@role_required("company")
def my_jobs(user):
    return jsonify([j.to_dict() for j in Job.query.filter_by(company_id=user.id).all()])


@jobs_bp.post("/jobs/<int:job_id>/apply")
@role_required("student")
def apply(user, job_id):
    db.get_or_404(Job, job_id)
    if Application.query.filter_by(job_id=job_id, user_id=user.id).first():
        return jsonify(error="Anda sudah memohon"), 409
    db.session.add(Application(job_id=job_id, user_id=user.id))
    db.session.commit()
    return jsonify(ok=True), 201


@jobs_bp.get("/my/applications")
@role_required("student")
def my_applications(user):
    apps = Application.query.filter_by(user_id=user.id).all()
    return jsonify([{"id": a.id, "job": a.job.title, "company": a.job.company.name,
                     "status": a.status} for a in apps])


@jobs_bp.get("/jobs/<int:job_id>/applicants")
@role_required("company")
def applicants(user, job_id):
    j = db.get_or_404(Job, job_id)
    if j.company_id != user.id:
        return jsonify(error="Bukan job anda"), 403
    return jsonify([{"id": a.id, "name": a.user.name, "email": a.user.email,
                     "skills": a.user.skills, "status": a.status} for a in
                    Application.query.filter_by(job_id=job_id).all()])


@jobs_bp.patch("/applications/<int:app_id>")
@role_required("company")
def set_status(user, app_id):
    a = db.get_or_404(Application, app_id)
    if a.job.company_id != user.id:
        return jsonify(error="Bukan job anda"), 403
    status = (request.get_json() or {}).get("status")
    if status not in ("pending", "accepted", "rejected"):
        return jsonify(error="Status tidak sah"), 400
    a.status = status
    db.session.commit()
    return jsonify(ok=True)


@jobs_bp.get("/recommendations")
@role_required("student")
def recommendations(user):
    return jsonify(recommend_for(user))
