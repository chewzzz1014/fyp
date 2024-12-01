# backend/db/utils.py

from .models import JobStatus
from .db_session import SessionLocal

def preload_job_statuses():
    statuses = ["Interested", "Applied", "Assessment", "Interviewing", "Offer", "Rejected"]
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