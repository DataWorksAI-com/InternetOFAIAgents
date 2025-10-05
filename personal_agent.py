from fastapi import FastAPI
from transformers import pipeline
import requests
import threading

app = FastAPI()
text_generator = pipeline('text-generation', model='gpt2')

AGENT_ID = "personal_agent"
AGENT_ENDPOINT = "http://127.0.0.1:8001"
REGISTRY_URL = "http://127.0.0.1:8000/agents"
FBA_ENDPOINT = "http://127.0.0.1:8002/a2a"
AGENT_INFO = {
    "agent_id": AGENT_ID,
    "name": "Personal Agent",
    "endpoint": AGENT_ENDPOINT,
    "description": "Handles user requests and talks to flight agent"
}

@app.on_event("startup")
def register_and_start():
    requests.post(REGISTRY_URL, json=AGENT_INFO)
    threading.Thread(target=user_interaction, daemon=True).start()

def user_interaction():
    print("Hi! What would you like to do?")
    while True:
        user_input = input("> ").strip().lower()
        # Book a flight
        if "book" in user_input and "flight" in user_input:
            dest = input("Destination: ")
            start = input("Start date (YYYY-MM-DD): ")
            end = input("End date (YYYY-MM-DD): ")
            booking_data = {
                "from": "Boston",
                "to": dest,
                "dates": [start, end],
                "preferences": {"window_seat": True}
            }
            # Discover flight agent from registry
            agents = requests.get("http://127.0.0.1:8000/agents").json()
            flight_agent = next((a for a in agents if "flight" in a["name"].lower()), None)
            if flight_agent:
                response = requests.post(f"{flight_agent['endpoint']}/a2a", json=booking_data)
                print(response.json())
            else:
                print("No flight booking agent found.")
        # Order a cake
        elif "order" in user_input and "cake" in user_input:
            cake_type = input("Cake type: ")
            delivery_date = input("Delivery date (YYYY-MM-DD): ")
            cake_data = {
                "cake_type": cake_type,
                "delivery_date": delivery_date
            }
            # Discover cake agent from registry
            agents = requests.get("http://127.0.0.1:8000/agents").json()
            cake_agent = next((a for a in agents if "cake" in a["name"].lower()), None)
            if cake_agent:
                response = requests.post(f"{cake_agent['endpoint']}/a2a", json=cake_data)
                print(response.json())
            else:
                print("No cake ordering agent found.")
        # General LLM prompt
        else:
            reply = text_generator(user_input, max_new_tokens=50, num_return_sequences=1)[0]['generated_text']
            print(reply)


@app.post("/a2a")
def receive_message(data: dict):
    prompt = data.get('text', '')
    result = text_generator(prompt, max_length=50, num_return_sequences=1)
    return {"reply": result[0]['generated_text']}
