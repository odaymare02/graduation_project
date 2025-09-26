from fastapi import APIRouter
from pydantic import BaseModel
from RAG import get_answer

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    major: str | None = None

@router.post("/ask")
async def ask_question(request: QueryRequest):
    result = get_answer(request.query, request.major)
    return result
