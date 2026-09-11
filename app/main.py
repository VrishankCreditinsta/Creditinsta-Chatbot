from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag import chat
from app.db import (
    get_user_conversations,
    get_conversation_messages,
    delete_conversation
)


app = FastAPI(
    title="Vabisor Chatbot API",
    description="API for Vabisor customer support chatbot with conversation history support",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[int] = 1


class ChatResponse(BaseModel):
    session_id: str
    type: str
    message: str
    suggested_chips: Optional[List[str]] = []
    show_manager_connect: Optional[bool] = False
    rewritten_query: Optional[str] = None


class ConversationItem(BaseModel):
    session_id: str
    user_id: int
    title: Optional[str] = None
    created_at: str
    updated_at: str
    last_message: Optional[str] = None


class MessageItem(BaseModel):
    id: int
    sender: str
    message_type: str
    message: str
    created_at: str


class SuggestionsResponse(BaseModel):
    suggestions: List[str]


@app.get("/")
def home():
    return {
        "message": "Vabisor Chatbot API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


from app.db import (
    get_user_conversations,
    get_conversation_messages,
    delete_conversation,
    get_quick_suggestions
)


@app.get("/chat/suggestions", response_model=SuggestionsResponse)
def get_chat_suggestions():
    suggestions = get_quick_suggestions()
    return {
        "suggestions": suggestions
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:
        response = chat(
            message=request.message.strip(),
            session_id=request.session_id,
            user_id=request.user_id or "guest"
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong while processing your request: {str(e)}"
        )


@app.get("/conversations", response_model=List[ConversationItem])
def get_conversations_endpoint(user_id: str = Query(..., description="User ID to fetch conversation history")):
    try:
        return get_user_conversations(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{session_id}/messages", response_model=List[MessageItem])
def get_messages_endpoint(session_id: str):
    try:
        messages = get_conversation_messages(session_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversations/{session_id}")
def delete_conversation_endpoint(session_id: str):
    try:
        delete_conversation(session_id)
        return {"success": True, "message": f"Conversation {session_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))