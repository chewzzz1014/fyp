from pydantic import BaseModel

class JobResumeRequest(BaseModel):
    resume_id: int
    job_title: str
    job_link: str
    company_name: str
    application_status: str
    job_desc: str