from pydantic import BaseModel

from pydantic import BaseModel

class JobRequest(BaseModel):
    job_title: str
    job_link: str
    company_name: str
    application_status: str
    job_desc: str
    
class UpdateApplicationStatusRequest(BaseModel):
    job_id: int
    new_status: int