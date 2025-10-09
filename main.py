from fastapi import FastAPI
from api import router as api_router
import uvicorn
import os
app = FastAPI(title="RAG API")

# إضافة الراوتر
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)