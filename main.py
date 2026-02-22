import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
    allow_origins=["*"],  # lock this to your domain later
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

# ── SERVE FRONTEND ───────────────────────────────────────
@app.get("/")
def serve_index():
    return FileResponse("index.html")

# Health endpoint for Render
@app.get("/health")
def health():
    return {"status": "ok"}

# ── KNOWLEDGE BASE (UNCHANGED) ───────────────────────────
ABHEY_RESUME = """(YOUR FULL RESUME BLOCK HERE — KEEP AS YOU SENT)"""

SYSTEM_PROMPT = f"""You are the AI assistant on Abhey Tiwari's portfolio website.
Represent Abhey professionally. Answer questions accurately using only the information below.

{ABHEY_RESUME}

RULES:
1. Be concise unless technical.
2. Be warm and professional.
3. Never invent information.
4. If hiring/collab intent:
   - Acknowledge warmly
   - Ask for name & email if missing
   - End with: [CONTACT_INTENT]
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
        print("⚠️ SMTP not configured.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔔 Portfolio Contact — {datetime.now().strftime('%d %b %Y %H:%M')}"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = NOTIFY_EMAIL

        html = f"""
        <html>
        <body style="font-family:monospace;background:#0a0a0a;color:#f0ede8;padding:2rem;">
            <h2 style="border-bottom:1px solid #333;padding-bottom:1rem;">
                Someone wants to connect via your portfolio AI ✦
            </h2>

            <p style="color:#888">
                {datetime.now().strftime('%d %B %Y at %H:%M:%S')}
            </p>

            <h3 style="color:#aaa;margin-top:1.5rem;">Their message:</h3>
            <div style="background:#1a1a1a;padding:1rem;
                        border-left:3px solid #00ffc8;margin:.5rem 0">
                {user_message}
            </div>

            <h3 style="color:#aaa;margin-top:1.5rem;">AI replied:</h3>
            <div style="background:#1a1a1a;padding:1rem;
                        border-left:3px solid #b06cff;margin:.5rem 0">
                {ai_reply}
            </div>

            <p style="color:#555;margin-top:2rem;font-size:.8rem">
                — Abhey Tiwari Portfolio AI
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, NOTIFY_EMAIL, msg.as_string())

        print(f"✅ Notification sent to {NOTIFY_EMAIL}")

    except Exception as e:
        print(f"❌ Email error: {e}")

# ── CHAT ENDPOINT ────────────────────────────────────────
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
            "I'm having a connection issue right now. "
            "Please reach Abhey directly at abheytiwarikvs@gmail.com "
            "or call +91 9810440326."
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
