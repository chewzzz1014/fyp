# backend/db/init_db.py
from .models import Base
from .db_session import engine
from .utils import preload_job_statuses

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Preload job status
    await preload_job_statuses()