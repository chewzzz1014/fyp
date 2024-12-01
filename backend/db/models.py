from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Text, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    last_login = Column(TIMESTAMP, nullable=True)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    job_resumes = relationship("JobResume", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = 'resumes'
    resume_id = Column(Integer, primary_key=True, autoincrement=True)
    resume_name = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    uploaded_on = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    ner_prediction = Column(Text, nullable=True)  # You can add NER predictions here

    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    job_resumes = relationship("JobResume", back_populates="resume", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'resume_name', name='uq_user_resume_name'),
    )
    
class JobStatus(Base):
    __tablename__ = "job_status"
    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String, unique=True, nullable=False)

    # Relationship to jobs
    jobs = relationship("Job", back_populates="status")
    
class Job(Base):
    __tablename__ = "jobs"
    job_id = Column(Integer, primary_key=True, autoincrement=True)
    job_title = Column(String, nullable=False)
    job_link = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    job_desc = Column(Text, nullable=False)
    ner_prediction = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    application_status = Column(Integer, ForeignKey("job_status.status_id", ondelete="SET NULL"), nullable=True)
    

    # Relationships
    user = relationship("User", back_populates="jobs")
    status = relationship("JobStatus", back_populates="jobs")
    job_resumes = relationship("JobResume", back_populates="job", cascade="all, delete-orphan")


class JobResume(Base):
    __tablename__ = "job_resumes"
    job_resume_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    job_resume_score = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="job_resumes")
    resume = relationship("Resume", back_populates="job_resumes")
    job = relationship("Job", back_populates="job_resumes")

    __table_args__ = (
        UniqueConstraint("user_id", "resume_id", "job_id", name="uq_user_resume_job"),
    )