from pydantic import BaseModel

class JobBase(BaseModel):
    job_title: str
    job_link: str
    company_name: str
    job_desc: str

class AddJobRequest(JobBase):
    pass

class UpdateJobRequest(JobBase):
    job_id: int