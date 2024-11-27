from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.connection import SessionLocal
from backend.db.models import Resume
from backend.resume.utils import parse_resume_text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import HTTPException

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), resume_name: str = "", db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        resume_text = await parse_resume_text(file)
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded resume is empty or unreadable.")

        # Save resume to the database
        db_resume = Resume(resume_name=resume_name, resume_text=resume_text)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        return {"resume_text": resume_text, "resume_id": db_resume.resume_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
