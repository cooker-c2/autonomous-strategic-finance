from pydantic import BaseModel

class ForecastRequest(BaseModel):
    business_unit: str
    months: int
    revenue_per_customer: float | None = None
    sales_per_executive: int | None = None
    marketing_cost: float | None = None
    cac: float | None = None
    conversion_rate: float | None = None
    small_medium_revenue_per_customer: float | None = None
