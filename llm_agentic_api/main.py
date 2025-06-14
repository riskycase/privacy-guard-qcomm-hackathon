from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio

from llm.llmstudio_client import chat_with_llm
from agents.face_detection import get_face_count
from agents.browser_extension import process_browser_extension_input

app = FastAPI()

class AgenticChatRequest(BaseModel):
    prompt: str
    face_image_url: Optional[str] = None
    browser_data: Optional[Dict[str, Any]] = None

class AgenticChatResponse(BaseModel):
    response: str
    agent_results: Optional[Dict[str, Any]] = None

@app.post("/v1/agentic-chat", response_model=AgenticChatResponse)
async def agentic_chat(req: AgenticChatRequest):
    messages = [
        {"role": "system", "content": "You are an agentic assistant. You can use tools: face-detection, browser-extension."},
        {"role": "user", "content": req.prompt}
    ]

    # NOTE: ONNX-based LLM does not support tool-calling natively.
    # You must implement tool-calling logic in this orchestration loop if needed.
    # For now, just run the LLM and return its response.
    llm_response = chat_with_llm(messages)

    return AgenticChatResponse(
        response=llm_response.get("content", ""),
        agent_results=None
    ) 