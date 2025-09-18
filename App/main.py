from fastapi import FastAPI
from fastapi.responses import FileResponse
import tempfile
from .models import ForecastRequest
from .services import generate_forecast


app = FastAPI()

@app.post("/forecast_excel")
def forecast_excel(request: ForecastRequest):
    try:
        # Generate the forecast DataFrame
        forecast_df = generate_forecast(request)

        # Save to temporary Excel file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            forecast_df.to_excel(tmp.name, index=False)
            file_path = tmp.name

        # Return downloadable file
        return FileResponse(
            path=file_path,
            filename=f"forecast_{request.business_unit}_{request.months}m.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return {"error": str(e)}
