from sqlalchemy.orm import SessionLocal
from backend.db.models import JobStatus

def preload_job_statuses():
    statuses = ["Applied", "Interview Scheduled", "Offer Extended", "Rejected", "Withdrawn"]
    session = SessionLocal()
    try:
        for status_name in statuses:
            existing_status = session.query(JobStatus).filter_by(status_name=status_name).first()
            if not existing_status:
                session.add(JobStatus(status_name=status_name))
        session.commit()
    except Exception as e:
        print(f"Error preloading job statuses: {e}")
        session.rollback()
    finally:
        session.close()