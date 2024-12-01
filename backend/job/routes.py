from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.db_session import SessionLocal
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import JobStatus

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/job-statuses")
def protected(
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        job_statuses = db.query(JobStatus).all()
        
        return [{"status_id": job_status.status_id, "status_name": job_status.status_name} for job_status in job_statuses]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")