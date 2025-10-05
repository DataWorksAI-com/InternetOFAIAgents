from fastapi import FastAPI
from transformers import pipeline
import requests

app = FastAPI()
text_generator = pipeline('text-generation', model='gpt2')

AGENT_ID = "cake_agent"
AGENT_ENDPOINT = "http://127.0.0.1:8003"
REGISTRY_URL = "http://127.0.0.1:8000/agents"
AGENT_INFO = {
    "agent_id": AGENT_ID,
    "name": "Cake Ordering Agent",
    "endpoint": AGENT_ENDPOINT,
    "description": "Returns dummy cake order info and LLM replies"
}

@app.on_event("startup")
def register():
    requests.post(REGISTRY_URL, json=AGENT_INFO)

@app.post("/a2a")
def handle_message(data: dict):
    # If it's a cake order request
    if "cake_type" in data and "delivery_date" in data:
        options = [
            {"cake": "Chocolate", "price": 20, "delivery": data["delivery_date"]},
            {"cake": "Vanilla", "price": 18, "delivery": data["delivery_date"]}
        ]
        prompt = f"Received cake order for {data['cake_type']} on {data['delivery_date']}. Here are some options: {options}"
        confirmation = text_generator(prompt, max_new_tokens=50, num_return_sequences=1)[0]['generated_text']
        return {"options": options, "confirmation": confirmation}
    # Otherwise, treat as a general LLM prompt
    else:
        prompt = data.get("text", "")
        reply = text_generator(prompt, max_new_tokens=50, num_return_sequences=1)[0]['generated_text']
        return {"reply": reply}
