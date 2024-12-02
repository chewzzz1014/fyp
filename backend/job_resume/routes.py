import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from .schema import JobResumeRequest
from backend.ner.utils import make_prediction
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import Resume, Job, JobResume
from backend.ner.utils import remove_non_alphanumeric, make_prediction
from .utils import calculate_job_resume_score
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
def get_all_job_resume(
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        job_resumes = (
            db.query(JobResume)
            .options(
                joinedload(JobResume.job),
                joinedload(JobResume.resume)
            )
            .filter(JobResume.user_id == user_id)
            .all()
        )

        result = [
            {
                "job_resume_id": job_resume.job_resume_id,
                "user_id": job_resume.user_id,
                "job_resume_score": job_resume.job_resume_score,
                "created_at": job_resume.created_at,
                "job": {
                    "job_id": job_resume.job.job_id,
                    "job_title": job_resume.job.job_title,
                    "job_link": job_resume.job.job_link,
                    "company_name": job_resume.job.company_name,
                    "job_desc": job_resume.job.job_desc,
                    "ner_prediction": json.loads(job_resume.job.ner_prediction) if job_resume.job.ner_prediction else None,
                    "created_at": job_resume.job.created_at,
                    "application_status": job_resume.job.application_status
                } if job_resume.job else None,
                "resume": {
                    "resume_id": job_resume.resume.resume_id,
                    "resume_name": job_resume.resume.resume_name,
                    "resume_text": job_resume.resume.resume_text,
                    "uploaded_on": job_resume.resume.uploaded_on,
                    "ner_prediction": json.loads(job_resume.resume.ner_prediction) if job_resume.resume.ner_prediction else None,
                } if job_resume.resume else None,
            }
            for job_resume in job_resumes
        ]

        return result
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{job_resume_id}")
def get_job_resume_by_id(
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
@router.post("/")
def add_job_resume(
    request: JobResumeRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        # Fetch resume and validate
        resume = db.query(Resume).filter(
            Resume.resume_id == request.resume_id,
            Resume.user_id == user_id
        ).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found.")

        # case when job_id is provided
        # find job, find/add job resume
        if request.job_id:
            job = db.query(Job).filter(
                Job.job_id == request.job_id,
                Job.user_id == user_id
            ).first()
            if not job:
                raise HTTPException(status_code=404, detail="Job not found.")

            job_resume = db.query(JobResume).filter(
                JobResume.job_id == job.job_id,
                JobResume.resume_id == resume.resume_id,
                JobResume.user_id == user_id
            ).first()
            # Update job-resume score
            updated_score = calculate_job_resume_score(resume.ner_prediction, job.ner_prediction)
            if not job_resume:
                job_resume = JobResume(
                    user_id=user_id,
                    resume_id=resume.resume_id,
                    job_id=job.job_id,
                    job_resume_score=updated_score
                )
                db.add(job_resume)
                db.commit()

            job_resume.job_resume_score = updated_score
            db.commit()

        # case when job_id is not provided
        # add job,add job resume
        else:
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

            # Create job-resume relationship
            score = calculate_job_resume_score(resume.ner_prediction, job.ner_prediction)
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
            "job_ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None,
            "job_resume_score": job_resume.job_resume_score
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
