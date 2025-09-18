from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from App.models import ForecastQuery
from App.services import forecast_large_customers, forecast_small_medium_customers, generate_excel
from io import BytesIO

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Autonomous Strategic Finance API is running!"}

@app.post("/forecast")
def forecast(query: ForecastQuery):
    if query.business_unit.lower() == "large":
        df = forecast_large_customers(
            months=query.months,
            sales_per_executive=query.sales_per_executive,
            revenue_per_customer=query.revenue_per_customer
        )
    elif query.business_unit.lower() == "small_medium":
        df = forecast_small_medium_customers(
            months=query.months,
            marketing_cost=query.marketing_cost,
            cac=query.cac,
            conversion_rate=query.conversion_rate,
            revenue_per_customer=query.revenue_per_customer
        )
    else:
        return {"error": "Invalid business unit. Use 'large' or 'small_medium'"}

    excel_bytes = generate_excel(df)
    return StreamingResponse(BytesIO(excel_bytes), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=forecast.xlsx"})
