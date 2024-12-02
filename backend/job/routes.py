import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import JobStatus, Job
from .schema import UpdateApplicationStatusRequest, JobRequest
from backend.ner.utils import remove_non_alphanumeric, make_prediction
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
def get_all_jobs(
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        jobs = db.query(Job).filter(Job.user_id == user_id).all()
        
        logger.info(jobs)
        
        return [
            {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_link": job.job_link,
                "company_name": job.company_name,
                "job_desc": job.job_desc,
                "ner_prediction": job.ner_prediction,
                "created_at": job.created_at,
                "user_id": job.user_id,
                "application_status": job.application_status,
            }
            for job in jobs
        ]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
@router.get("/job-statuses")
def get_all_job_statuses(
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        job_statuses = db.query(JobStatus).all()
        
        return [
            {"status_id": job_status.status_id, "status_name": job_status.status_name} 
            for job_status in job_statuses]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.put("/application-status")
def update_application_status(
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
    
@router.post("/")
def add_job(
    request: JobRequest, 
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        # Perform NER on job description
        cleaned_job_desc = remove_non_alphanumeric(request.job_desc)
        job_ner_prediction = make_prediction(cleaned_job_desc)

        # Save job to the database
        job = Job(
            user_id=user_id,
            job_title=request.job_title,
            job_link=request.job_link,
            company_name=request.company_name,
            application_status=request.application_status,
            job_desc=cleaned_job_desc,
            ner_prediction=json.dumps(job_ner_prediction) if job_ner_prediction else None
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        return {
            "job_id": job.job_id,
            "job_title": job.job_title,
            "job_link": job.job_link,
            "company_name": job.company_name,
            "application_status": job.application_status,
            "job_desc": job.job_desc,
            "ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")