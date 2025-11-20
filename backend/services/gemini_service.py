# backend/services/gemini_service.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

def ask_gemini(prompt: str) -> str:
    """
    Send a text prompt to Gemini and return the model's response text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") else str(response)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I couldn't process your request right now."
