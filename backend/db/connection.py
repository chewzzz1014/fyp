from .models import Base
from .db_session import engine
from .utils import preload_job_statuses

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Preload job status
    preload_job_statuses()