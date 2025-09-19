# models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ForecastRequest(BaseModel):
    query: str
    months: int

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    excel_download_url: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    forecast_query: Optional[str] = None
    forecast_months: Optional[int] = None