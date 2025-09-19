import os
import pathlib
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import tempfile
import pandas as pd

# Correct imports for your business logic
from .logic_engine import generate_forecast, KnowledgeBaseError
from .chat_engine import chatbot
from .models import ForecastRequest, ChatMessage, ChatResponse

# Use a more robust way to get the file path
current_dir = pathlib.Path(__file__).parent
frontend_dir = current_dir.parent / "frontend"

app = FastAPI()

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Main chatbot endpoint for financial conversations"""
    response = await chatbot.generate_response(message.message)
    return ChatResponse(**response)

@app.post("/forecast_excel")
async def forecast_excel(request: ForecastRequest, background_tasks: BackgroundTasks):
    """
    Generates a financial forecast and returns it as a downloadable Excel file.
    """
    try:
        print(f"Received forecast request: {request.dict()}")
        
        llm = chatbot.get_llm()
        if llm is None:
            raise HTTPException(status_code=503, detail="LLM service unavailable. Please check your API key.")
        
        # Use 'await' to handle the asynchronous call
        forecast_df = await generate_forecast(request, llm)
        if forecast_df.empty:
            raise HTTPException(status_code=400, detail="Unable to generate a valid forecast.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            forecast_df.to_excel(tmp.name, index=False)
            file_path = tmp.name
            print(f"Excel file created at: {file_path}")

        # Add cleanup as a background task
        background_tasks.add_task(os.remove, file_path)

        return FileResponse(
            path=file_path,
            filename=f"forecast_saas_company_{request.months}m.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            background=background_tasks,
        )

    except KnowledgeBaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the forecast: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Autonomous CFO API is running! Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
