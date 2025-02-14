import requests
import os
import logging
from fastapi import APIRouter, HTTPException

# ✅ Load environment variables
AGENTIVE_API_KEY = os.getenv("AGENTIVE_API_KEY", "5f06fd08-0011-4747-904b-6425c24c4b35")
AGENTIVE_ASSISTANT_ID = os.getenv("AGENTIVE_ASSISTANT_ID", "d6ae978a-1ee4-420f-86a5-e286247a4ed7")
BASE_URL = "https://agentivehub.com/api"

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ 1️⃣ Create a new chat session
@router.post("/agentive/create-session")
def create_chat_session():
    """
    Creates a new chat session using Agentive's API.
    """
    url = f"{BASE_URL}/chat/session"
    payload = {
        "api_key": AGENTIVE_API_KEY,
        "assistant_id": AGENTIVE_ASSISTANT_ID
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        session_data = response.json()
        logger.info(f"Session Created: {session_data}")
        return session_data  # Expected output: {"session_id": "your-session-id"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


# ✅ 2️⃣ Send a chat message
@router.post("/agentive/send-message")
def send_chat_message(session_id: str, message: str):
    """
    Sends a chat message using the provided session_id.
    """
    url = f"{BASE_URL}/chat"
    payload = {
        "api_key": AGENTIVE_API_KEY,
        "session_id": session_id,
        "type": "custom_code",
        "assistant_id": AGENTIVE_ASSISTANT_ID,
        "messages": [{"role": "user", "content": message}]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        chat_response = response.json()
        logger.info(f"Chat Response: {chat_response}")
        return chat_response

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send chat message: {str(e)}")


# ✅ 3️⃣ Standalone Test (Remove in Production)
if __name__ == "__main__":
    session_data = create_chat_session()
    if "session_id" in session_data:
        print("Session Created:", session_data)
        chat_response = send_chat_message(session_data["session_id"], "Say Hello!")
        print("Chat Response:", chat_response)
    else:
        print("Error creating session:", session_data)
