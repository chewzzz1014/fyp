from pydantic import BaseModel

class JobResumeRequest(BaseModel):
    resume_id: int
    job_title: str
    job_link: str
    company_name: str
    application_status: str
    job_desc: str
    
class JobResumeResponse(BaseModel):
    job_resume_id: int
    resume_text: str
    resume_ner_prediction: list
    job_desc: str
    job_ner_prediction: list
    job_resume_score: float