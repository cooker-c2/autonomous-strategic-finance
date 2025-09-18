import pandas as pd
from typing import Dict
from io import BytesIO

def forecast_large_customers(months: int, sales_per_executive: int, revenue_per_customer: float) -> pd.DataFrame:
    data = []
    total_customers = 0
    for month in range(1, months + 1):
        # For simplicity, assume 1 sales executive added per month
        total_customers += sales_per_executive
        revenue = total_customers * revenue_per_customer
        data.append({"Month": month, "Customers": total_customers, "Revenue": revenue})
    df = pd.DataFrame(data)
    return df

def forecast_small_medium_customers(months: int, marketing_cost: float, cac: float, conversion_rate: float, revenue_per_customer: float) -> pd.DataFrame:
    data = []
    total_customers = 0
    for month in range(1, months + 1):
        # Estimate paying customers
        new_customers = (marketing_cost / cac) * conversion_rate
        total_customers += new_customers
        revenue = total_customers * revenue_per_customer
        data.append({"Month": month, "Customers": total_customers, "Revenue": revenue})
    df = pd.DataFrame(data)
    return df

def generate_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Forecast")
    return output.getvalue()
