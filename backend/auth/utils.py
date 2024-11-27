from passlib.context import CryptContext
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from backend.core.config import JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET_KEY

@AuthJWT.load_config
def get_config():
    return Settings()