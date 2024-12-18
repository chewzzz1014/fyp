import json
from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import JobStatus, Job
from .schema import AddJobRequest, UpdateJobRequest
from backend.ner.utils import remove_non_alphanumeric, make_prediction
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
async def get_all_jobs(
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        result = await db.execute(select(Job).filter(Job.user_id == user_id))
        jobs = result.scalars().all()
        
        logger.info(jobs)
        
        return [
            {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_link": job.job_link,
                "company_name": job.company_name,
                "job_desc": job.job_desc,
                "ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None,
                "created_at": job.created_at,
                "user_id": job.user_id,
            }
            for job in jobs
        ]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
@router.get("/job-statuses")
async def get_all_job_statuses(
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        
        result = await db.execute(select(JobStatus))
        job_statuses = result.scalars().all()
        
        return [
            {"status_id": job_status.status_id, "status_name": job_status.status_name} 
            for job_status in job_statuses]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.post("/")
async def add_job(
    request: AddJobRequest, 
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

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
        await db.commit()
        await db.refresh(job)

        return {
            "job_id": job.job_id,
            "job_title": job.job_title,
            "job_link": job.job_link,
            "company_name": job.company_name,
            "job_desc": job.job_desc,
            "ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.put("/{job_id}")
async def update_job(
    request: UpdateJobRequest,
    job_id: int = Path(..., description="The job_id of the job to be updated"),
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        result = await db.execute(select(Job).filter(Job.job_id == job_id, Job.user_id == user_id))
        job = result.scalars().first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.job_title = request.job_title or job.job_title
        job.job_link = request.job_link or job.job_link
        job.company_name = request.company_name or job.company_name

        if request.job_desc and request.job_desc != job.job_desc:
            job.job_desc = remove_non_alphanumeric(request.job_desc)
            job.ner_prediction = json.dumps(make_prediction(job.job_desc))

        await db.commit()
        await db.refresh(job)

        return {
            "job_id": job.job_id,
            "job_title": job.job_title,
            "job_link": job.job_link,
            "company_name": job.company_name,
            "job_desc": job.job_desc,
            "ner_prediction": json.loads(job.ner_prediction) if job.ner_prediction else None,
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")