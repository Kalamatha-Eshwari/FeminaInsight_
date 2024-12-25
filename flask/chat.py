import requests
import logging

API_TOKEN = "YOUR-TOKEN"
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def format_prompt(user_input):
    return f"""<s>[INST] You are a knowledgeable PCOS health assistant. Provide accurate, medical information about PCOS (Polycystic Ovary Syndrome). Base your responses on established medical knowledge. Keep responses focused on PCOS and related health topics.

User question: {user_input} [/INST]"""

def get_chat_response(user_input):
    try:
        prompt = format_prompt(user_input)
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        })
        
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            return "I'm experiencing technical difficulties. Please try again."
            
    except Exception as e:
        logging.error(f"Error in chat response: {str(e)}")
        return "Sorry, I'm temporarily unavailable. Please try again later."