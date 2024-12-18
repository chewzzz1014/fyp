from passlib.context import CryptContext
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from backend.db.models import User
from jose import JWTError, jwt
from sqlalchemy.future import select

from backend.db.models import User
from backend.db.db_session import AsyncSessionLocal
from backend.core.config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_SECONDS
from backend.core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to get user ID from token
async def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> int:
    try:
        logger.info(f'token {token}')
        user = await get_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user.user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_user_from_token(token: str) -> User:
    try:
        # Decode token and get user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f'payload {payload}')
        user_id: int = int(payload.get("sub"))
        logger.info(f'user_id {user_id}')
        if user_id is None:
            raise JWTError("User ID not found in token")
        
        # Query the user from the database
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).filter(User.user_id == user_id)
            )
            user = result.scalars().first()
        
        if user is None:
            raise JWTError("User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET_KEY
    authjwt_access_token_expires: int = ACCESS_TOKEN_EXPIRE_SECONDS

@AuthJWT.load_config
def get_config():
    logger.info(f'token expires in {ACCESS_TOKEN_EXPIRE_SECONDS} seconds')
    return Settings()