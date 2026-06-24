from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    match_id: str = None


@router.post("")
async def send_chat_message(chat: ChatMessage) -> dict:
    """AI chat Q&A using RAG to answer questions about matches and predictions."""
    return {
        "success": True,
        "data": {
            "user_message": chat.message,
            "assistant_response": "AI-generated response based on RAG context...",
            "match_id": chat.match_id,
            "sources": []
        },
        "error": None,
        "meta": {}
    }
