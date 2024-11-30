from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Text, ForeignKey, UniqueConstraint
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

    # Relationship to resumes
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = 'resumes'
    resume_id = Column(Integer, primary_key=True, autoincrement=True)
    resume_name = Column(String, nullable=False)
    resume_text = Column(Text, nullable=False)
    uploaded_on = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    ner_prediction = Column(Text, nullable=True)  # You can add NER predictions here

    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)

    # Relationship to user
    user = relationship("User", back_populates="resumes")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'resume_name', name='uq_user_resume_name'),
    )