import re
from langdetect import detect
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models import Chatbots, ChatbotLeads
import logging

logger = logging.getLogger("MedusaApp")

ENGLISH_KEYWORDS = [
    "demo", "pricing", "quote", "purchase", "subscribe", "interested", "get started", "how much?", "buy",
    "callback", "contact me", "request a call", "schedule a meeting", "more info", "cost?", "billing", "sign up",
    "enroll", "product details", "want to buy", "plans", "offer", "free trial", "get a call", "schedule consultation",
    "customer service", "order", "register", "pricing details", "request info", "request quote", "service options",
    "monthly plan", "yearly plan", "can I buy?", "partner with us", "special offer", "customer support", "get started",
    "join now", "corporate deal", "group discount", "training session", "AI chatbot demo"
]

PORTUGUESE_KEYWORDS = [
    "demonstração", "demonstracao", "preços", "precos", "orçamento", "orcamento", "comprar", "assinar", "interessado",
    "começar", "comecar", "quanto custa?", "adquirir", "me ligue", "ligação", "ligacao", "entre em contato",
    "agendar reunião", "agendar reuniao", "solicitar chamada", "solicitação", "solicitacao", "detalhes do produto",
    "quero comprar", "planos", "oferta", "teste grátis", "teste gratis", "receber proposta", "solicitar orçamento",
    "planos disponíveis", "planos disponiveis", "consultoria", "atendimento ao cliente", "assinatura", "serviço",
    "servico", "cadastro", "plano mensal", "plano anual", "posso comprar?", "parceria", "suporte técnico",
    "promoção especial", "desconto exclusivo", "desconto empresa", "suporte ao cliente", "treinamento de IA"
]

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d{9,15}"

router = APIRouter(prefix="/leads", tags=["Leads"])

def detect_lead(chatbot_id: int, user_message: str, db: Session):
    try:
        lang = detect(user_message)
        keywords = PORTUGUESE_KEYWORDS if lang == "pt" else ENGLISH_KEYWORDS
    except Exception as e:
        logger.warning(f"Language detection failed for message: {user_message}. Defaulting to English. Error: {str(e)}")
        keywords = ENGLISH_KEYWORDS

    if any(word in user_message.lower() for word in keywords) or re.search(EMAIL_REGEX, user_message) or re.search(PHONE_REGEX, user_message):
        store_lead(chatbot_id, user_message, db)
        return True
    return False

def store_lead(chatbot_id: int, user_message: str, db: Session):
    lead = ChatbotLeads(
        chatbot_id=chatbot_id,
        user_id="unknown",
        user_name="Anonymous",
        lead_source="Chatbot",
        message=user_message
    )
    db.add(lead)
    db.commit()
    logger.info(f"✅ Lead Stored: {user_message}")

@router.post("/{id}/process_message")
def process_message(id: int, message: str, db: Session = Depends(get_db)):
    from app.models import Chatbots  # Import here to avoid circular import if needed
    chatbot = db.query(Chatbots).filter(Chatbots.id == id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    is_lead = detect_lead(id, message.lower(), db)
    return {
        "chatbot_id": id,
        "user_message": message,
        "lead_detected": is_lead
    }
