import os
# fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# db
from backend.db.connection import init_db
# ner
from backend.ner.routes import router as ner_router
# from backend.ner.utils import download_model_from_gcs
# auth
from backend.auth.routes import router as auth_router
# resume
from backend.resume.routes import router as resume_router
#job-resume
from backend.job_resume.routes import router as job_resume_router
# job
from backend.job.routes import router as job_router
# user
from backend.profile.routes import router as profile_router

from backend.core.config import LOCAL_MODEL_PATH
from backend.core.logger import logger

app = FastAPI()

origins = [
    "http://localhost:3000",  # Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.on_event("startup")
async def on_startup():
    # if not os.path.exists(LOCAL_MODEL_PATH):
    #     download_model_from_gcs()
    # else:
    #     logger.info('NER Model was downloaded.')
    await init_db()
    
app.include_router(auth_router, prefix="/auth")
app.include_router(ner_router, prefix="/ner")
app.include_router(resume_router, prefix="/resume")
app.include_router(job_resume_router, prefix="/job-resume")
app.include_router(job_router, prefix="/job")
app.include_router(profile_router, prefix="/profile")