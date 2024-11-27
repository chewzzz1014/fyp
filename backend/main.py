# fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ner
from backend.ner.routes import router as ner_router
# auth
from backend.auth.routes import router as auth_router
# resume
from backend.resume.routes import router as resume_router

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

app.include_router(auth_router, prefix="/auth")
app.include_router(ner_router, prefix="/ner")
app.include_router(resume_router, prefix="/resume")