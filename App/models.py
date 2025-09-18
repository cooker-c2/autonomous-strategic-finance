from pydantic import BaseModel
from typing import Optional

class ForecastQuery(BaseModel):
    business_unit: str  # 'large' or 'small_medium'
    months: int = 12  # number of months to forecast
    sales_per_executive: Optional[int] = 2  # for large customers
    revenue_per_customer: Optional[float] = 16500  # for large customers
    marketing_cost: Optional[float] = 10000  # for small/medium
    cac: Optional[float] = 1500
    conversion_rate: Optional[float] = 0.45
