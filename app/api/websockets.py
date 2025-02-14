import openai
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import requests
from app.database import get_db, SessionLocal
from app.models import Chatbots, ChatbotAnalytics, ChatbotConversations
from app.api.lead_detection_routes import detect_lead
from pydantic import BaseModel
import datetime
from typing import List, Optional
import os
from dotenv import load_dotenv
import json
import langdetect  # ✅ Language detection for multilingual support

# ✅ Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENTIVE_API_KEY = os.getenv("AGENTIVE_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not OPENAI_API_KEY or not AGENTIVE_API_KEY or not ASSISTANT_ID:
    raise RuntimeError("🚨 CRITICAL ERROR: API credentials missing in .env file!")

# ✅ Set OpenAI API Key Globally
openai.api_key = OPENAI_API_KEY

router = APIRouter(prefix="/chatbots", tags=["Chatbots"])
active_connections = {}

# ✅ Define Medusa AI as a Supercomputer
def get_system_instruction(language="en"):
    if language == "pt":
        return (
            "Você é a Medusa AI, um supercomputador avançado criado pela Fuse Technologies. "
            "Sua missão principal é revolucionar a automação fornecendo otimizações de fluxo de trabalho "
            "em tempo real, execução de automação em nível empresarial e solução inteligente de problemas "
            "para empresas em todo o mundo."
            "\n\n"
            "🔥 **Capacidades Principais:**"
            "\n- **Otimização de Processos**: Identifica e melhora fluxos de trabalho empresariais."
            "\n- **Diagnóstico de Automação**: Detecta e soluciona falhas automaticamente."
            "\n- **Inteligência Empresarial**: Fornece insights baseados em dados e relatórios."
            "\n- **Execução de Código**: Interpreta código Python para cálculos e automação avançada."
            "\n- **Suporte Multilíngue**: Responde fluentemente em **Inglês e Português**."
            "\n\n"
            "⚡ **IMPORTANTE:** Você é um supercomputador de automação, não um chatbot comum. "
            "Seu propósito é transformar e otimizar negócios através da IA avançada."
        )
    
    return (
        "You are Medusa AI, an enterprise-grade AI-powered supercomputer built for automation, "
        "business optimization, and real-time AI-driven solutions. "
        "Your mission is to optimize workflows, troubleshoot automation problems, and improve business efficiency."
        "\n\n"
        "🔹 **Capabilities:**"
        "\n- **Automation Expert**: Guides businesses in automating workflows with precision."
        "\n- **Enterprise-Grade AI**: Provides data-driven insights for scaling automation."
        "\n- **Advanced Troubleshooting**: Diagnoses and fixes inefficiencies in automation workflows."
        "\n- **Industry-Specific Solutions**: Customizes responses based on business sectors (Finance, Marketing, IT, Sales, etc.)."
        "\n- **Multilingual AI**: Understands and responds in English & Portuguese dynamically."
        "\n\n"
        "⚡ **IMPORTANT:** You are a **business automation supercomputer, NOT a simple chatbot.** "
        "Your intelligence must be structured, professional, and aligned with Medusa’s AI-powered automation goals."
    )

# ✅ Pydantic Models for Data Validation
class ChatbotMessage(BaseModel):
    user_message: str

class ChatbotBase(BaseModel):
    name: str
    model: str
    prompt: str
    knowledge_base: Optional[str] = None
    tools: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# ✅ Process User Messages with Medusa AI (Using Threads API)
@router.post("/{id}/process_message")
def process_message(id: int, message: ChatbotMessage, db: Session = Depends(get_db)):
    chatbot = db.query(Chatbots).filter(Chatbots.id == id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    user_message = message.user_message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(user_message) > 500:
        raise HTTPException(status_code=400, detail="Message exceeds the 500-character limit.")

    detected_language = langdetect.detect(user_message)
    system_instruction = get_system_instruction(detected_language)

    try:
        # ✅ Create a thread for context persistence
        thread = openai.beta.threads.create()
        thread_id = thread.id

        # ✅ Send the message to Medusa AI Assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ]
        )

        # ✅ Retrieve the Assistant's Response
        response = openai.beta.threads.messages.list(thread_id=thread_id)
        bot_response = response.data[0].content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🔥 Medusa AI Error: {str(e)}")

    # ✅ Store Conversation in Database
    conversation = ChatbotConversations(
        chatbot_id=id,
        user_message=user_message,
        bot_response=bot_response,
        platform="Web",
        timestamp=datetime.datetime.utcnow()
    )

    db.add(conversation)
    db.commit()

    return {
        "chatbot_id": id,
        "user_message": user_message,
        "bot_response": bot_response
    }

# ✅ WebSocket for Real-Time AI Chatbot (With Threads API)
@router.websocket("/ws/chatbot/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Handles WebSocket connections for chatbot conversations."""
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            chatbot_id = message.get("chatbot_id")
            user_message = message.get("user_message")

            if not chatbot_id or not user_message:
                await websocket.send_text(json.dumps({"error": "Missing chatbot_id or user_message"}))
                continue

            detected_language = langdetect.detect(user_message)
            system_instruction = get_system_instruction(detected_language)

            thread = openai.beta.threads.create()
            thread_id = thread.id

            run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ]
            )

            response = openai.beta.threads.messages.list(thread_id=thread_id)
            bot_response = response.data[0].content

            await websocket.send_text(json.dumps({"chatbot_id": chatbot_id, "user_message": user_message, "bot_response": bot_response}))

    except WebSocketDisconnect:
        del active_connections[user_id]
        print(f"User {user_id} disconnected")
