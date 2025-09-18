# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ForecastRequest  # Correct import from models
from app.logic_engine import generate_forecast  # Correct import from app package
import tempfile
import os
import pandas as pd

app = FastAPI()

# Add CORS middleware to allow requests from your frontend
origins = [
    "http://127.0.0.1:5500",  # Your frontend's address
    "http://localhost:5500",
    "http://localhost:8000",   # Added for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/forecast_excel")
def forecast_excel(request: ForecastRequest):
    """
    Generates a financial forecast and returns it as a downloadable Excel file.
    """
    file_path = None
    try:
        print(f"Received request: {request.dict()}")
        
        # Generate the forecast DataFrame by passing the entire request object
        forecast_df = generate_forecast(request)

        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            forecast_df.to_excel(tmp.name, index=False)
            file_path = tmp.name
            print(f"Excel file created at: {file_path}")

        # Return downloadable file - FileResponse handles file deletion after sending
        return FileResponse(
            path=file_path,
            filename=f"forecast_saas_company_{request.months}m.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        # Clean up the temporary file if it was created but an error occurred
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
            
        # Raise an HTTPException to return a proper error response
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the forecast: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Autonomous CFO API is running! Visit /docs for API documentation."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "autonomous-cfo-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)