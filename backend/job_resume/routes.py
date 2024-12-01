import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .schema import JobResumeRequest
from backend.ner.utils import make_prediction
from backend.db.db_session import SessionLocal
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import Resume, Job, JobResume
from backend.ner.utils import remove_non_alphanumeric, make_prediction
from .utils import calculate_job_resume_score
from backend.core.logger import logger

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{job_resume_id}")
def get_job_resume(
    job_resume_id: int,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        logger.info(f"job_resume_id = {job_resume_id}")
        job_resume = db.query(JobResume).filter(JobResume.job_resume_id == job_resume_id, JobResume.user_id == user_id).first()
        if not job_resume:
            raise HTTPException(status_code=404, detail="Job Resume not found.")
        
        resume = db.query(Resume).filter(Resume.resume_id == job_resume.resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found.")
        
        job = db.query(Job).filter(Job.job_id == job_resume.job_id, Job.user_id == user_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        return {
            "job_resume_id": job_resume.job_resume_id,
            "job_resume_score": job_resume.job_resume_score,
            "resume": {
                "resume_id": resume.resume_id,
                "resume_text": resume.resume_text,
                "ner_prediction": json.loads(resume.ner_prediction) if resume.ner_prediction else None
            },
            "job": {
                "job_id": job.job_id,
                "job_desc": job.job_desc,
                "ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
       
# add job
@router.post("/", response_model=JobResumeRequest)
def predict(
    request: JobResumeRequest, 
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        # Fetch resume
        resume = db.query(Resume).filter(
            Resume.resume_id == request.resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found.")

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

        # Calculate job-resume score (implement scoring in utils)
        score = calculate_job_resume_score(resume.ner_prediction, job.ner_prediction)

        # Save job-resume relationship
        job_resume = JobResume(
            user_id=user_id,
            resume_id=resume.resume_id,
            job_id=job.job_id,
            job_resume_score=score
        )
        db.add(job_resume)
        db.commit()

        return {
            "job_resume_id": job_resume.job_resume_id,
            "resume_text": resume.resume_text,
            "resume_ner_prediction": json.loads(resume.ner_prediction) if resume.ner_prediction else None,
            "job_ner_prediction": job_ner_prediction,
            "job_resume_score": job_resume.job_resume_score
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")