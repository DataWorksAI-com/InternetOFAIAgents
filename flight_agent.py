from fastapi import FastAPI
from transformers import pipeline
import requests

app = FastAPI()
text_generator = pipeline('text-generation', model='gpt2')

AGENT_ID = "flight_agent"
AGENT_ENDPOINT = "http://127.0.0.1:8002"
REGISTRY_URL = "http://127.0.0.1:8000/agents"
AGENT_INFO = {
    "agent_id": AGENT_ID,
    "name": "Flight Booking Agent",
    "endpoint": AGENT_ENDPOINT,
    "description": "Returns dummy flight options and LLM replies"
}

@app.on_event("startup")
def register():
    requests.post(REGISTRY_URL, json=AGENT_INFO)

@app.post("/a2a")
def handle_message(data: dict):
    # If it's a flight booking request
    if "to" in data and "dates" in data:
        options = [
            {"flight": "AF123", "price": 800, "depart": "2025-06-10 10:00"},
            {"flight": "BA456", "price": 750, "depart": "2025-06-10 15:00"}
        ]
        prompt = f"Received booking request for {data['to']} on {data['dates']}. Here are some options: {options}"
        confirmation = text_generator(prompt, max_new_tokens=50, num_return_sequences=1)[0]['generated_text']
        return {"options": options, "confirmation": confirmation}
    # Otherwise, treat as a general LLM prompt
    else:
        prompt = data.get("text", "")
        reply = text_generator(prompt, max_new_tokens=50, num_return_sequences=1)[0]['generated_text']
        return {"reply": reply}
