from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import User, Resume
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
def get_profile(
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        user = db.query(User).filter(User.user_id == user_id).first()
        logger.info(111)
        logger.info(user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        resumes = db.query(Resume).filter(Resume.user_id == user.user_id).all()
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "resumes": resumes
        }
    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")