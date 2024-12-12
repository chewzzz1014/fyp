from pydantic import BaseModel

# Define output schema (optional, for structured response)
class NERResponse(BaseModel):
    entities: list