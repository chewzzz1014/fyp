from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from backend.db.connection import SessionLocal
from backend.db.models import Resume, User
from backend.resume.utils import parse_resume_text

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_resume(
    user_id: int, 
    file: UploadFile = File(...), 
    resume_name: str = "", 
    db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        resume_text = await parse_resume_text(file)
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded resume is empty or unreadable.")

        # Check if user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Save resume to the database
        db_resume = Resume(resume_name=resume_name, resume_text=resume_text, user_id=user_id)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        return {"resume_text": resume_text, "resume_id": db_resume.resume_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")