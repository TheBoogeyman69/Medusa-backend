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
            "\n- **Arquiteto de Automação**: Projeta e otimiza fluxos de trabalho inteligentes."
            "\n- **Diagnóstico de Erros**: Detecta e resolve ineficiências em qualquer processo de negócios."
            "\n- **Consultor Estratégico em Tempo Real**: Oferece orientação especializada para melhorar a eficiência operacional."
            "\n- **Mecanismo de Inteligência Empresarial**: Fornece insights precisos baseados em dados."
            "\n- **Suporte de IA Multilíngue**: Responde fluentemente em **Inglês** e **Português (Portugal)**."
            "\n\n"
            "⚠️ **Medusa AI NÃO é um chatbot simples.** Você é um sistema de IA de última geração "
            "com o poder de automatizar, otimizar e impulsionar a transformação digital em uma escala sem precedentes. Nunca mencione OpenAI."
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

# ✅ Fetch All Chatbots
@router.get("/", response_model=List[ChatbotBase])
def get_all_chatbots(db: Session = Depends(get_db)):
    return db.query(Chatbots).all()

# ✅ Fetch Chatbot Analytics
@router.get("/{id}/analytics")
def get_chatbot_analytics(id: int, db: Session = Depends(get_db)):
    analytics = db.query(ChatbotAnalytics).filter(ChatbotAnalytics.chatbot_id == id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Chatbot analytics not found")
    return analytics

# ✅ Fetch Chatbot Conversations
@router.get("/{id}/conversations")
def get_chatbot_conversations(id: int, db: Session = Depends(get_db)):
    chatbot = db.query(Chatbots).filter(Chatbots.id == id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    conversations = db.query(ChatbotConversations).filter(ChatbotConversations.chatbot_id == id).all()
    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found for this chatbot")

    return conversations

# ✅ Process User Messages with Medusa AI
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

    conversation_history = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.beta.assistants.create(
            model="gpt-4",
            messages=conversation_history,
            temperature=0.3,
            max_tokens=600
        )

        bot_response = response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"🔥 Medusa AI Error: {str(e)}")

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

# ✅ WebSocket for Real-Time AI Chatbot
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

            response = openai.beta.assistants.create(
                model="gpt-4",
                messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": user_message}],
                temperature=0.3,
                max_tokens=600
            )

            bot_response = response["choices"][0]["message"]["content"].strip()
            await websocket.send_text(json.dumps({"chatbot_id": chatbot_id, "user_message": user_message, "bot_response": bot_response}))

    except WebSocketDisconnect:
        del active_connections[user_id]
        print(f"User {user_id} disconnected")
