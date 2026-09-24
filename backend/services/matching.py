"""Simple AI recommendation: keyword overlap scoring (0-100)."""
from models import db, Job, Recommendation


def parse_skills(text):
    return {s.strip().lower() for s in (text or "").replace(";", ",").split(",") if s.strip()}


def score(user_skills, job_skills):
    js = parse_skills(job_skills)
    us = parse_skills(user_skills)
    if not js or not us:
        return 0.0
    return round(len(us & js) / len(js) * 100, 1)


def recommend_for(user, limit=10):
    """Kira score semua job, simpan dalam table recommendations, return top N."""
    results = []
    for job in Job.query.all():
        s = score(user.skills, job.required_skills)
        rec = Recommendation.query.filter_by(user_id=user.id, job_id=job.id).first()
        if rec:
            rec.score = s
        else:
            db.session.add(Recommendation(user_id=user.id, job_id=job.id, score=s))
        results.append((job, s))
    db.session.commit()
    results.sort(key=lambda x: x[1], reverse=True)
    return [{**j.to_dict(), "score": s} for j, s in results[:limit] if s > 0]
