from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import JobStatus, Job
from .schema import UpdateApplicationStatusRequest

router = APIRouter()
        
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
    
@router.put("/application-status")
def update_status(
    request: UpdateApplicationStatusRequest, 
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        # Fetch the job resume entry by ID
        job = db.query(Job).filter(Job.job_id == request.job_id, Job.user_id == user_id).first()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        job.application_status = request.new_status
        db.commit()

        return {"message": "Status updated successfully"}
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")