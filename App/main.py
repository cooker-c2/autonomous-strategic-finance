from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Autonomous Strategic Finance API is running!"}

@app.get("/search")
def search(query: str):
    # For now, just echo back the query
    return {"query": query, "result": "This will be replaced with financial logic"}
