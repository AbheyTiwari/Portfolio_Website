import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ── LOAD ENV ─────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NOTIFY_EMAIL   = os.getenv("NOTIFY_EMAIL", "abheytiwarikvs@gmail.com")
SMTP_EMAIL     = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD", "")

client = genai.Client(api_key=GEMINI_API_KEY)

# ── FASTAPI APP ──────────────────────────────────────────
app = FastAPI(title="Abhey Tiwari — Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock to your domain later
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── KNOWLEDGE BASE ───────────────────────────────────────
ABHEY_RESUME = """
NAME: Abhey Tiwari
ROLE: AI Engineer & Full-Stack Developer
LOCATION: Noida, Uttar Pradesh, India (Delhi NCR)
EMAIL: abheytiwarikvs@gmail.com
PHONE: +91 9810440326
GITHUB: https://github.com/AbheyTiwari
LINKEDIN: https://www.linkedin.com/in/abheytiwari/
STATUS: Open to Work — remote or NCR-based roles
"""

SYSTEM_PROMPT = f"""
You are the AI assistant on Abhey Tiwari's portfolio website.
Represent Abhey professionally using only the information below.

{ABHEY_RESUME}

RULES:
1. Be concise and professional.
2. Do not invent information.
3. If someone wants to hire or collaborate:
   - Ask for their name and email if missing.
   - End your reply with: [CONTACT_INTENT]
"""

conversation_history: list[types.Content] = []

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    contact_intent_detected: bool = False


# ── EMAIL NOTIFICATION ───────────────────────────────────
def send_notification(user_message: str, ai_reply: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("SMTP not configured.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Portfolio Contact — {datetime.now().strftime('%d %b %Y %H:%M')}"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = NOTIFY_EMAIL

        html = f"""
        <html>
        <body style="font-family:monospace;background:#111;color:#eee;padding:2rem;">
            <h2>New Portfolio Contact</h2>
            <p><b>User Message:</b><br>{user_message}</p>
            <p><b>AI Reply:</b><br>{ai_reply}</p>
            <p style="margin-top:2rem;font-size:0.8rem;">Abhey Portfolio AI</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, NOTIFY_EMAIL, msg.as_string())

        print("Notification sent.")

    except Exception as e:
        print(f"Email error: {e}")


# ── API ROUTES ───────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global conversation_history

    conversation_history.append(
        types.Content(role="user", parts=[types.Part(text=req.message)])
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=conversation_history[-20:],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=512,
                temperature=0.7,
            ),
        )
        reply_text = response.text

    except Exception as e:
        print(f"Gemini error: {e}")
        reply_text = (
            "I'm experiencing a connection issue. "
            "Please contact Abhey directly at abheytiwarikvs@gmail.com."
        )

    contact_intent = "[CONTACT_INTENT]" in reply_text
    clean_reply = reply_text.replace("[CONTACT_INTENT]", "").strip()

    conversation_history.append(
        types.Content(role="model", parts=[types.Part(text=clean_reply)])
    )

    if contact_intent:
        send_notification(req.message, clean_reply)

    return ChatResponse(
        reply=clean_reply,
        contact_intent_detected=contact_intent
    )


@app.delete("/chat/reset")
def reset():
    global conversation_history
    conversation_history = []
    return {"status": "conversation reset"}


# ── STATIC + FRONTEND SERVING ───────────────────────────
# This must be AFTER API routes
app.mount("/", StaticFiles(directory=".", html=True), name="static")


# ── LOCAL RUN ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
