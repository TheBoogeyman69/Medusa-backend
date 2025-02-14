from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
import random
import string
import datetime
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
import smtplib
import logging
from fastapi.middleware.cors import CORSMiddleware
import jwt

# ✅ Retrieve API credentials
AGENTIVE_API_KEY = os.getenv("AGENTIVE_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not AGENTIVE_API_KEY or not ASSISTANT_ID:
    raise RuntimeError("Agentive API credentials must be set in .env file.")

# ✅ Initialize FastAPI App
app = FastAPI()

# ✅ Import routers AFTER FastAPI is initialized
from app.api import chatbot_routes, lead_detection_routes, webhooks, websockets
from app.api.oauth import router as oauth_router  # Import oauth directly to avoid circular imports
from app.agentive_integration import router as agentive_router

# ✅ Ensure WebSocket router is included in main.py
from app.api import websockets

app.include_router(websockets.router, prefix="", tags=["Websockets"])
@app.get("/")

async def root():
    return {"message": "Medusa Chatbot API is Running"}

# ✅ Load environment variables (Ensure correct path)
load_dotenv(dotenv_path=os.path.abspath("backend/.env"))

# ✅ Ensure required environment variables are set
required_env_vars = ["AGENTIVE_API_KEY", "ASSISTANT_ID", "DATABASE_URL", "SECRET_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise RuntimeError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

# ✅ Set up SQLAlchemy engine and session (Ensure metadata is created properly)
from app.database import engine, SessionLocal, Base

@app.on_event("startup")
def startup():
    """Initialize database tables at startup."""
    Base.metadata.create_all(bind=engine)
    
# ✅ Include API routers
app.include_router(chatbot_routes.router, tags=["Chatbots"])
app.include_router(lead_detection_routes.router, prefix="/leads", tags=["Leads"])
app.include_router(oauth_router, tags=["OAuth"])
app.include_router(agentive_router, prefix="/agentive", tags=["Agentive"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(websockets.router, prefix="/ws", tags=["Websockets"])

# ✅ Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MedusaApp")

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from app.models import UserDB  # ✅ Import instead of redefining

# ✅ Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Helper function to send emails
def send_email(email: str, subject: str, message: str):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender or not password:
        logger.error("Email credentials are missing in the environment variables.")
        raise RuntimeError("Email credentials are missing in the environment variables.")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
        logger.info(f"Email sent successfully to {email}")
    except smtplib.SMTPException as e:
        logger.error(f"Error sending email to {email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email.")

# ✅ Pydantic Models
class User(BaseModel):
    email: EmailStr
    username: str
    password: str

    @validator("password")
    def password_strength(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value

class SignInModel(BaseModel):
    email: EmailStr
    password: str

class ConfirmationCodeRequest(BaseModel):
    email: EmailStr
    code: str

    @validator("code")
    def validate_code(cls, value):
        if len(value) != 4:
            raise ValueError("Code must be 4 characters long.")
        return value

class RequestPasswordResetModel(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator("new_password")
    def password_strength(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value

# ✅ Utility function to generate short tokens
def generate_short_token(length=4):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ✅ API Endpoints
@app.post("/signup")
def signup(user: User, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    confirmation_code = generate_short_token()
    hashed_password = pwd_context.hash(user.password)
    new_user = UserDB(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_verified=0,
        confirmation_code=confirmation_code,
    )
    db.add(new_user)
    db.commit()

    background_tasks.add_task(
        send_email,
        user.email,
        "Email Confirmation",
        f"Your confirmation code is: {confirmation_code}",
    )

    token = jwt.encode(
        {"email": user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
        SECRET_KEY,
        algorithm="HS256",
    )

    return {
        "success": True,
        "message": "User created successfully. Please check your email for the confirmation code.",
        "token": token,
    }

@app.post("/verify-code")
def verify_code(data: ConfirmationCodeRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.confirmation_code != data.code:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
    db_user.is_verified = 1
    db_user.confirmation_code = None
    db.commit()
    return {"success": True, "message": "Email verified successfully"}

@app.post("/signin")
def signin(user: SignInModel, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = jwt.encode(
        {"email": db_user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
        SECRET_KEY,
        algorithm="HS256",
    )
    return {
        "success": True,
        "message": "Sign in successful",
        "token": token,
        "email": db_user.email,
        "username": db_user.username,
    }

@app.post("/request-password-reset")
def request_password_reset(data: RequestPasswordResetModel, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    reset_token = generate_short_token()
    db_user.reset_token = reset_token
    db_user.reset_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    db.commit()
    send_email(
        db_user.email,
        "Password Reset Request",
        f"Your password reset token is: {reset_token}",
    )
    return {"success": True, "message": "Password reset token sent to your email."}

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.reset_token == data.token).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid reset token")
    if db_user.reset_token_expiry < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token has expired")
    db_user.hashed_password = pwd_context.hash(data.new_password)
    db_user.reset_token = None
    db_user.reset_token_expiry = None
    db.commit()
    return {"success": True, "message": "Password updated successfully"}

@app.post("/validate-reset-token")
def validate_reset_token(data: ConfirmationCodeRequest, db: Session = Depends(get_db)):
    logger.info(f"Validating reset token for email: {data.email}")
    db_user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not db_user:
        logger.error(f"User not found for email: {data.email}")
        raise HTTPException(status_code=404, detail="User not found.")
    if db_user.reset_token != data.code:
        logger.warning(f"Invalid reset token for email: {data.email} - Provided: {data.code}")
        raise HTTPException(status_code=400, detail="Invalid reset token.")
    if db_user.reset_token_expiry and db_user.reset_token_expiry < datetime.datetime.utcnow():
        logger.warning(f"Expired reset token for email: {data.email} - Expired At: {db_user.reset_token_expiry}")
        raise HTTPException(status_code=400, detail="Reset token has expired.")
    logger.info(f"Reset token validated successfully for email: {data.email}")
    return {"success": True, "message": "Reset token is valid."}

@app.post("/resend-code")
def resend_code(data: RequestPasswordResetModel, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    confirmation_code = generate_short_token()
    db_user.confirmation_code = confirmation_code
    db.commit()
    send_email(
        db_user.email,
        "Email Confirmation Resent",
        f"Your new confirmation code is: {confirmation_code}",
    )
    return {"success": True, "message": "A new confirmation code has been sent to your email."}
