from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.database import SessionLocal
from app.models import ChatbotConversations
import json

router = APIRouter()

@router.post("/webhook/chatbot-sync")
async def chatbot_sync(payload: dict, background_tasks: BackgroundTasks):
    try:
        chatbot_id = payload.get("chatbot_id")
        messages = payload.get("messages", [])
        
        db = SessionLocal()
        for msg in messages:
            conversation = ChatbotConversations(
                chatbot_id=chatbot_id,
                user_message=msg.get("user_message"),
                bot_response=msg.get("bot_response"),
                platform=msg.get("platform"),  # Capture platform info
                timestamp=msg.get("timestamp")
            )
            db.add(conversation)
        db.commit()
        db.close()
        return {"status": "success", "message": "Chatbot data synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
