from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.connection import SessionLocal
from backend.db.models import User
from .schema import UserCreate, UserLogin
from .utils import hash_password, verify_password, AuthJWT

router = APIRouter()

# Dependency for Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User Signup
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # create new user
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate tokens
    Authorize = AuthJWT()
    access_token = Authorize.create_access_token(subject=str(db_user.id))
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "msg": "User created successfully"
    }

# User Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Fetch user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_user.last_login = func.now()
    db.commit()
    db.refresh(db_user)
    
    # Generate tokens
    access_token = Authorize.create_access_token(subject=str(db_user.id))
    refresh_token = Authorize.create_refresh_token(subject=str(db_user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "msg": "Login successful"
    }

# Protected Route
@router.get("/protected")
def protected(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        return {"msg": "You are authorized!", "current_user": current_user}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")