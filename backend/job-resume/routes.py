import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .schema import JobResumeRequest
from .utils import make_prediction
from backend.db.connection import SessionLocal
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import Resume, Job, JobResume
from backend.ner.utils import remove_non_alphanumeric, make_prediction
from .utils import calculate_job_resume_score

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
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
            title=request.job_title,
            link=request.job_link,
            company_name=request.company_name,
            application_status=request.application_status,
            description=cleaned_job_desc,
            ner_prediction=json.dumps(job_ner_prediction) if job_ner_prediction else None
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Calculate job-resume score (implement scoring in utils)
        score = calculate_job_resume_score(resume.ner_prediction, job_ner_prediction)

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
            "message": "Job added successfully and linked to the resume.",
            "job_id": job.job_id,
            "score": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")