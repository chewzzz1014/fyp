from pydantic import BaseModel
from typing import Optional

class JobResumeRequest(BaseModel):
    job_id: Optional[int] = None
    resume_id: int
    job_title: str
    job_link: str
    company_name: str
    application_status: str
    job_desc: str
    
class UpdateApplicationStatusRequest(BaseModel):
    job_resume_id: int
    new_status: int