from pydantic import BaseModel

class UpdateApplicationStatusRequest(BaseModel):
    job_id: int
    new_status: int