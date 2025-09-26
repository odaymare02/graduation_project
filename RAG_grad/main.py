from fastapi import FastAPI
from api import router as api_router

app = FastAPI(title="RAG API")

# إضافة الراوتر
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
