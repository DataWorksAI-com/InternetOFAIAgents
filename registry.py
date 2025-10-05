from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Agent(BaseModel):
    agent_id: str
    name: str
    endpoint: str
    description: str

agents_registry = []

@app.get("/agents", response_model=List[Agent])
def get_agents():
    return agents_registry

@app.post("/agents")
def register_agent(agent: Agent):
    if any(existing.agent_id == agent.agent_id for existing in agents_registry):
        raise HTTPException(status_code=400, detail="Agent ID already registered")
    agents_registry.append(agent)
    return {"status": "registered", "agent_id": agent.agent_id}
