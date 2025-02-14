from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText

app = FastAPI()

# Mock database to store user information temporarily
user_db = {}

class User(BaseModel):
    name: str
    email: EmailStr

class ConfirmationCode(BaseModel):
    email: EmailStr
    code: str

@app.post("/signup/")
async def sign_up(user: User, background_tasks: BackgroundTasks):
    # Step 1: Generate a 6-digit confirmation code
    confirmation_code = f"{random.randint(100000, 999999)}"
    
    # Step 2: Save the user's details and confirmation code
    user_db[user.email] = {
        "name": user.name,
        "confirmation_code": confirmation_code,
        "is_verified": False,
    }

    # Step 3: Send the confirmation code via email
    background_tasks.add_task(send_confirmation_email, user.email, confirmation_code)

    return {"message": "A confirmation code has been sent to your email."}

def send_confirmation_email(email: str, confirmation_code: str):
    # Step 4: Configure and send the email
    sender = "your-email@example.com"
    recipient = email
    subject = "Your Confirmation Code"
    body = f"Hello,\n\nYour confirmation code is: {confirmation_code}\n\nThank you for signing up!"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, "your-email-password")  # Replace with your email and password
        server.sendmail(sender, recipient, msg.as_string())

@app.post("/verify-code/")
async def verify_code(data: ConfirmationCode):
    # Step 5: Check if the user's email exists
    if data.email not in user_db:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 6: Verify the confirmation code
    if user_db[data.email]["confirmation_code"] == data.code:
        user_db[data.email]["is_verified"] = True
        return {"message": "Email verified successfully."}
    else:
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
