import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agents.debater import Debater

from core.rag_service import get_rag_service

app = FastAPI(title="Climate Policy Debate Simulator")

@app.on_event("startup")
async def startup_event():
    import asyncio
    print("Main: Starting background RAG initialization...")
    rs = get_rag_service()
    asyncio.create_task(rs.initialize())
    print("Main: Startup event finished.")

# Request/Response Models
class DebateRequest(BaseModel):
    topic: str
    rounds: int = Field(ge=1, le=5)

class Message(BaseModel):
    round: int
    agent: str
    message: str
    stance: str
    timestamp: str

class DebateResponse(BaseModel):
    messages: List[Message]

# Endpoints
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/policies/{country_code}")
def get_policy(country_code: str):
    path = f"data/policies/{country_code.lower()}_policy.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Policy not found")
    with open(path, "r") as f:
        return json.load(f)

@app.post("/debate/start", response_model=DebateResponse)
async def start_debate(request: DebateRequest):
    agents = [
        Debater("USA"),
        Debater("EU"),
        Debater("China")
    ]
    
    messages = []
    history = []
    
    for r in range(1, request.rounds + 1):
        for agent in agents:
            content, stance = await agent.generate_response(request.topic, history)
            
            msg = Message(
                round=r,
                agent=agent.country,
                message=content,
                stance=stance,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            messages.append(msg)
            history.append({
                "agent": agent.country,
                "message": content,
                "stance": stance
            })
            
    return DebateResponse(messages=messages)

# Serve Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
