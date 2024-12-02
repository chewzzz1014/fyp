from pydantic import BaseModel

class JobResumeRequest(BaseModel):
    job_id: int
    resume_id: int
    job_title: str
    job_link: str
    company_name: str
    application_status: str
    job_desc: str