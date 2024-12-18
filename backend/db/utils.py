# backend/db/db_utils.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import JobStatus
from .db_session import AsyncSessionLocal
from typing import AsyncGenerator

# Async get_db
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db

# Async preload_job_statuses
async def preload_job_statuses():
    statuses = ["Interested", "Applied", "Assessment", "Interviewing", "Offer", "Rejected"]
    
    # Use an async session
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                for status_name in statuses:
                    # Check if the status already exists
                    result = await session.execute(select(JobStatus).filter_by(status_name=status_name))
                    existing_status = result.scalars().first()
                    
                    if not existing_status:
                        # Add the new job status if not already present
                        session.add(JobStatus(status_name=status_name))
                
                # Commit the session to save changes
                await session.commit()
            except Exception as e:
                print(f"Error preloading job statuses: {e}")
                await session.rollback()