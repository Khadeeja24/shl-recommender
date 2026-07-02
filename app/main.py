from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import os
from app.agent import chat
from app.retriever import build_vectorstore

app = FastAPI(title="SHL Assessment Recommender Agent")

@app.on_event("startup")
async def startup_event():
    try:
        build_vectorstore()
        print("Vector store ready ✅")
    except Exception as e:
        print(f"Startup error: {e}")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [
            {"role": m.role, "content": m.content}
            for m in request.messages
        ]
        result = chat(messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)