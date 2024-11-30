from pydantic import BaseModel

class JobRequest(BaseModel):
    job_title: str
    job_link: str
    company_name: str
    application_status: int
    job_desc

# Define output schema (optional, for structured response)
class NERResponse(BaseModel):
    entities: list