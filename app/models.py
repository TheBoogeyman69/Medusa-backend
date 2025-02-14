from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# User model for authentication
class UserDB(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Integer, nullable=False, default=0)
    confirmation_code = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    __table_args__ = {'extend_existing': True}  # ✅ Fix: Prevents duplicate table error

# Chatbot models
class Chatbots(Base):
    __tablename__ = "chatbots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    knowledge_base = Column(Text, nullable=False)
    tools = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

class ChatbotAnalytics(Base):
    __tablename__ = "chatbot_analytics"
    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    messages_processed = Column(Integer, nullable=False)
    avg_response_time = Column(Integer, nullable=False)
    engagement_score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    chatbot = relationship("Chatbots", back_populates="analytics")

class ChatbotConversations(Base):
    __tablename__ = "chatbot_conversations"
    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    platform = Column(String, nullable=True)  # New field for platform (e.g., WhatsApp, Web)
    timestamp = Column(DateTime, default=func.now())

    chatbot = relationship("Chatbots", back_populates="conversations")

class ChatbotLeads(Base):
    __tablename__ = "chatbot_leads"
    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    lead_source = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    chatbot = relationship("Chatbots", back_populates="leads")

# Define relationships
Chatbots.analytics = relationship("ChatbotAnalytics", back_populates="chatbot")
Chatbots.conversations = relationship("ChatbotConversations", back_populates="chatbot")
Chatbots.leads = relationship("ChatbotLeads", back_populates="chatbot")
