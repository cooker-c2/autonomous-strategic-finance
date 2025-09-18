# models.py
from pydantic import BaseModel

class ForecastRequest(BaseModel):
    query: str
    business_unit: str  # ADD THIS LINE
    months: int