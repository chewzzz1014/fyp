import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .schema import JobResumeRequest, UpdateApplicationStatusRequest
from backend.ner.utils import make_prediction
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import Resume, Job, JobResume
from backend.ner.utils import remove_non_alphanumeric
from .utils import calculate_job_resume_score
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
async def get_all_job_resume(
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        result = []
        async with db.begin():
            query = select(JobResume).options(
                joinedload(JobResume.job),
                joinedload(JobResume.resume)
            ).filter(JobResume.user_id == user_id)
            job_resumes = (await db.execute(query)).scalars().all()

            for job_resume in job_resumes:
                result.append({
                    "job_resume_id": job_resume.job_resume_id,
                    "user_id": job_resume.user_id,
                    "job_resume_score": job_resume.job_resume_score,
                    "application_status": job_resume.application_status,
                    "created_at": job_resume.created_at,
                    "job": {
                        "job_id": job_resume.job.job_id,
                        "job_title": job_resume.job.job_title,
                        "job_link": job_resume.job.job_link,
                        "company_name": job_resume.job.company_name,
                        "job_desc": job_resume.job.job_desc,
                        "ner_prediction": json.loads(job_resume.job.ner_prediction) if job_resume.job.ner_prediction else None,
                        "created_at": job_resume.job.created_at,
                    } if job_resume.job else None,
                    "resume": {
                        "resume_id": job_resume.resume.resume_id,
                        "resume_name": job_resume.resume.resume_name,
                        "resume_text": job_resume.resume.resume_text,
                        "uploaded_on": job_resume.resume.uploaded_on,
                        "ner_prediction": json.loads(job_resume.resume.ner_prediction) if job_resume.resume.ner_prediction else None,
                    } if job_resume.resume else None,
                })

        return result
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{job_resume_id}")
async def get_job_resume_by_id(
    job_resume_id: int,
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        logger.info(f"job_resume_id = {job_resume_id}")
        async with db.begin():
            query = select(JobResume).filter(JobResume.job_resume_id == job_resume_id, JobResume.user_id == user_id)
            job_resume = (await db.execute(query)).scalars().first()
            if not job_resume:
                raise HTTPException(status_code=404, detail="Job Resume not found.")

            resume_query = select(Resume).filter(Resume.resume_id == job_resume.resume_id, Resume.user_id == user_id)
            resume = (await db.execute(resume_query)).scalars().first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found.")

            job_query = select(Job).filter(Job.job_id == job_resume.job_id, Job.user_id == user_id)
            job = (await db.execute(job_query)).scalars().first()
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

@router.post("/")
async def add_job_resume(
    request: JobResumeRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        async with db.begin():
            resume_query = select(Resume).filter(
                Resume.resume_id == request.resume_id,
                Resume.user_id == user_id
            )
            resume = (await db.execute(resume_query)).scalars().first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found.")

            job_resume = None

            if request.job_id:
                job_query = select(Job).filter(
                    Job.job_id == request.job_id,
                    Job.user_id == user_id
                )
                job = (await db.execute(job_query)).scalars().first()
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found.")

                job_resume_query = select(JobResume).filter(
                    JobResume.job_id == job.job_id,
                    JobResume.resume_id == resume.resume_id,
                    JobResume.user_id == user_id
                )
                job_resume = (await db.execute(job_resume_query)).scalars().first()

                updated_score = calculate_job_resume_score(resume.ner_prediction, job.ner_prediction)

                if not job_resume:
                    job_resume = JobResume(
                        user_id=user_id,
                        resume_id=resume.resume_id,
                        job_id=job.job_id,
                        job_resume_score=updated_score,
                        application_status=request.application_status
                    )
                    db.add(job_resume)
                else:
                    job_resume.job_resume_score = updated_score

            else:
                cleaned_job_desc = remove_non_alphanumeric(request.job_desc)
                job_ner_prediction = make_prediction(cleaned_job_desc)

                job = Job(
                    user_id=user_id,
                    job_title=request.job_title,
                    job_link=request.job_link,
                    company_name=request.company_name,
                    job_desc=cleaned_job_desc,
                    ner_prediction=json.dumps(job_ner_prediction) if job_ner_prediction else None
                )
                db.add(job)

                await db.flush()

                updated_score = calculate_job_resume_score(resume.ner_prediction, job.ner_prediction)

                job_resume = JobResume(
                    user_id=user_id,
                    resume_id=resume.resume_id,
                    job_id=job.job_id,
                    job_resume_score=updated_score,
                    application_status=request.application_status,
                )
                db.add(job_resume)

        await db.commit()

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

@router.put("/application-status")
async def update_application_status(
    request: UpdateApplicationStatusRequest, 
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        async with db.begin():
            job_resume_query = select(JobResume).filter(JobResume.job_resume_id == request.job_resume_id, JobResume.user_id == user_id)
            job_resume = (await db.execute(job_resume_query)).scalars().first()

            if not job_resume:
                raise HTTPException(status_code=404, detail="Job resume not found.")

            job_resume.application_status = request.new_status
            await db.commit()

        return {"message": "Status updated successfully"}
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")