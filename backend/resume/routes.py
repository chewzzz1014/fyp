from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.utils import get_db
from backend.db.models import Resume, User
from backend.resume.utils import parse_resume_text
from backend.core.logger import logger
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.ner.utils import remove_non_alphanumeric, make_prediction
import json

router = APIRouter()

@router.get("/")
async def get_all_resumes(
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        query = select(Resume).filter(Resume.user_id == user_id)
        result = await db.execute(query)
        resumes = result.scalars().all()

        return [
            {
                "resume_id": resume.resume_id,
                "resume_name": resume.resume_name,
                "resume_text": resume.resume_text,
                "ner_prediction": json.loads(resume.ner_prediction) if resume.ner_prediction else None
            } for resume in resumes
        ]
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    resume_name: str = Form(...),
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        logger.info(f'user_id {user_id}')
        logger.info(f'file {file}')
        logger.info(f'resume_name {resume_name}')
        
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        resume_text = await parse_resume_text(file)
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded resume is empty or unreadable.")
        
        resume_text = remove_non_alphanumeric(resume_text)

        try:
            entities = make_prediction(resume_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during NER prediction: {str(e)}")

        ner_prediction = json.dumps(entities)

        query = select(User).filter(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        db_resume = Resume(
            resume_name=resume_name,
            resume_text=resume_text,
            user_id=user_id,
            ner_prediction=ner_prediction
        )
        db.add(db_resume)
        await db.commit()
        await db.refresh(db_resume)

        return {
            "resume_id": db_resume.resume_id,
            "resume_name": resume_name,
            "resume_text": resume_text,
            "ner_prediction": entities
        }
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")