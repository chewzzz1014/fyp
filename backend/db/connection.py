from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases import Database
from backend.core.config import DATABASE_URL
from .models import Base
from .utils import preload_job_statuses

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = Database(DATABASE_URL)

Base.metadata.create_all(bind=engine)

preload_job_statuses()