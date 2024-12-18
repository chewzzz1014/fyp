from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.utils import get_db
from backend.auth.utils import AuthJWT, get_user_id_from_token
from backend.db.models import User, Resume
from backend.core.logger import logger

router = APIRouter()

@router.get("/")
async def get_profile(
    user_id: int = Depends(get_user_id_from_token),
    db: AsyncSession = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()

        # Use async context to ensure that the session is properly handled.
        async with db.begin():
            query = select(User).filter(User.user_id == user_id)
            result = await db.execute(query)
            user = result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            # Use a separate query to get resumes for the user
            resumes_query = select(Resume).filter(Resume.user_id == user.user_id)
            result = await db.execute(resumes_query)
            resumes = result.scalars().all()

        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "resumes": resumes
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")