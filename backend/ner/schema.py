from pydantic import BaseModel

class NERRequest(BaseModel):
    text: str

# Define output schema (optional, for structured response)
class NERResponse(BaseModel):
    entities: list