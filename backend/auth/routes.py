from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.utils import get_db
from backend.db.models import User
from .schema import UserCreate, UserLogin
from .utils import hash_password, verify_password, AuthJWT
from sqlalchemy import func

router = APIRouter()

# signup
@router.post("/signup")
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Generate tokens
    Authorize = AuthJWT()
    access_token = Authorize.create_access_token(subject=str(db_user.user_id))
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "msg": "User created successfully"
    }


# login
@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db), Authorize: AuthJWT = Depends()):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_user.last_login = func.now()
    await db.commit()
    await db.refresh(db_user)
    
    # Generate tokens
    access_token = Authorize.create_access_token(subject=str(db_user.user_id))
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "msg": "Login successful"
    }

@router.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        return {"msg": "You are authorized!", "current_user": current_user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")