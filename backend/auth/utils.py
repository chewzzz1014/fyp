from passlib.context import CryptContext
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from backend.db.models import User
from jose import JWTError, jwt

from backend.db.models import User
from backend.db.db_session import SessionLocal
from backend.core.config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to get user ID from token
def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> int:
    try:
        logger.info(f'token {token}')
        user = get_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user.user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_user_from_token(token: str) -> User:
    try:
        # Decode token and get user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f'payload {payload}')
        user_id: int = payload.get("sub")
        logger.info(f'user_id {user_id}')
        if user_id is None:
            raise JWTError("User ID not found in token")
        
        # Query the user from the database
        db = SessionLocal()
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise JWTError("User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET_KEY
    # authjwt_access_token_expires: int = ACCESS_TOKEN_EXPIRE_MINUTES
    # authjwt_access_token_expires: int = 60

@AuthJWT.load_config
def get_config():
    return Settings()