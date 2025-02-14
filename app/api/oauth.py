from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import jwt
import datetime
import os

from app.database import get_db  # Correct import
from app.models import UserDB     # Updated import

router = APIRouter()

# OAuth Credentials
CLIENT_ID = os.getenv("MEDUSA_CLIENT_ID")
CLIENT_SECRET = os.getenv("MEDUSA_CLIENT_SECRET")
REDIRECT_URI = "https://www.fusemoz.com/oauth-callback"

# Temporary storage for auth codes (simulating DB storage)
auth_codes = {}

@router.get("/oauth/authorize", response_class=HTMLResponse)
async def authorize_page(request: Request, user_id: str):
    """
    Serves the OAuth authorization page with Medusa branding.
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Authorize Medusa</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #111;
                color: white;
                padding: 50px;
            }}
            .container {{
                max-width: 400px;
                margin: auto;
                padding: 20px;
                background: #222;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
            }}
            h2 {{ color: #FF0FFB; }}
            .permissions {{ margin: 20px 0; }}
            .button {{
                display: inline-block;
                padding: 12px 20px;
                margin: 15px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s ease-in-out;
            }}
            .authorize {{
                background: linear-gradient(145deg, #6a00ff, #ae00ff);
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(255, 15, 251, 0.6);
            }}
            .authorize:hover {{ transform: scale(1.05); }}
            .cancel {{
                background-color: red;
                color: white;
                border: none;
                cursor: pointer;
            }}
            .cancel:hover {{ opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Authorize Medusa</h2>
            <p>Medusa needs permission to manage your automation workflows.</p>
            <div class="permissions">
                <ul>
                    <li>Access Instagram Data</li>
                    <li>Manage Automations</li>
                    <li>Read & Write Webflow Forms</li>  
                </ul>
            </div>
            <form action="/oauth/authorize/submit" method="POST">
                <input type="hidden" name="user_id" value="{user_id}">
                <button class="button authorize" type="submit">Authorize</button>
            </form>
            <a href="/" class="button cancel">Cancel</a>
        </div>
    </body>
    </html>
    """

@router.post("/oauth/authorize/submit")
async def authorize_user(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    
    auth_code = jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},
        CLIENT_SECRET,
        algorithm="HS256"
    )
    auth_codes[user_id] = auth_code
    return RedirectResponse(url=f"{REDIRECT_URI}?code={auth_code}")

@router.post("/oauth/token")
async def exchange_token(code: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(code, CLIENT_SECRET, algorithms=["HS256"])
        user_id = payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Authorization code expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid authorization code")

    access_token = jwt.encode(
        {"user_id": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        CLIENT_SECRET,
        algorithm="HS256"
    )
    
    user = db.query(UserDB).filter(UserDB.email == user_id).first()
    if user:
        user.access_token = access_token
        db.commit()

    return {"access_token": access_token, "token_type": "Bearer"}
