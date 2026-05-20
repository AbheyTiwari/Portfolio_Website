"""
Abhey Tiwari — Portfolio + AI Assistant
FastAPI backend (google.genai SDK)

PROD DEPLOY on Render:
  1. Push ALL files (main.py, index.html, styles.css, script.js,
     cursor-holo.js, images, sitemap.xml, robots.txt) to one GitHub repo
  2. Create a new Render Web Service
  3. Build command: pip install -r requirements.txt
  4. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
  5. Add env vars in Render dashboard:
       GEMINI_API_KEY  = your key
       NOTIFY_EMAIL    = abheytiwarikvs@gmail.com
       SMTP_EMAIL      = your gmail
       SMTP_PASSWORD   = your 16-char app password

LOCAL DEV:
  - Create .env with your keys
  - uvicorn main:app --reload --port 8000
  - Open http://localhost:8000
"""

import os
import resend
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ── CONFIG ───────────────────────────────────────────────────
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
NOTIFY_EMAIL    = os.getenv("NOTIFY_EMAIL", "abheytiwarikvs@gmail.com")
RESEND_API_KEY  = os.getenv("RESEND_API_KEY", "")
# Legacy SMTP kept as fallback
SMTP_EMAIL      = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD   = os.getenv("SMTP_PASSWORD", "")
PORT            = int(os.getenv("PORT", 8000))

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ── KNOWLEDGE BASE ───────────────────────────────────────────
ABHEY_RESUME = """
NAME: Abhey Tiwari
ROLE: AI Engineer
LOCATION: Noida, Uttar Pradesh, India (Delhi NCR)
EMAIL: abheytiwarikvs@gmail.com
PHONE: +91 9810440326
GITHUB: https://github.com/AbheyTiwari
LINKEDIN: https://www.linkedin.com/in/abheytiwari/
STATUS: Open to Work — remote or NCR-based roles

─── SUMMARY ────────────────────────────────────────────────
AI/ML engineer focused on building production-ready LLM systems — RAG pipelines,
local inference with Ollama, agentic architectures using LangGraph, and real-time
backends with FastAPI and WebSockets. Published research in democratising AI for
low-resource environments. Best Paper Award at NSAC 2026.

─── SKILLS ─────────────────────────────────────────────────
AI/ML:      LLMs, RAG Pipelines, vector search, embeddings, NLP, CNNs,
            agentic systems, LangChain, LangGraph, LlamaIndex, Ollama,
            ChromaDB, DeepFace

Languages:  Python, C++, JavaScript

Frameworks: FastAPI, Flask, Django, Streamlit

Infra:      Docker, Git, Linux, REST APIs, WebSockets, WebRTC

─── PROJECTS ───────────────────────────────────────────────

1. MAITRI AI (Privacy-First Mental Health Companion)
   - Real-time emotionally-aware psychological companion, 100% local inference
   - DeepFace for real-time facial emotion detection
   - Ollama (local LLMs) for dialogue — zero cloud data transmission
   - Stack: FastAPI, DeepFace, Ollama, WebSockets, Python
   - GitHub: https://github.com/AbheyTiwari/Maitri.git

2. INDICA v1.0 (Voice-Controlled Cognitive Assistant)
   - Full voice agent pipeline: STT → intent recognition → dispatcher → skills → TTS
   - Dual memory system: short-term session logs + long-term semantic embeddings
   - Modular dispatcher routes to skills without hallucinated actions
   - Stack: Python, Gemini API, speech_recognition, pyttsx3, asyncio, Playwright
   - GitHub: https://github.com/AbheyTiwari/INDICA

3. BUGFINER AI (Frontend Bug Reproduction Tool)
   - Converts natural language bug reports into executable Playwright browser tests
   - Records video proof of bug reproduction
   - Stack: Flask, Playwright, Gemini API, Asyncio
   - GitHub: https://github.com/AbheyTiwari/AI_bug_finder..git

4. QUIZARD (PDF Q&A Tool)
   - AI-powered PDF Q&A tool for fast document retrieval
   - Built during internship to eliminate manual search through 90+ page documents
   - Stack: FastAPI, Streamlit, Google Gemini, PyMuPDF, Python
   - GitHub: https://github.com/AbheyTiwari/Quizard

5. OUTREACHPRO (Open-Source Cold Email Tool)
   - Open-source alternative to paid cold-email platforms
   - Sends personalised batch emails via Gmail using Google Sheets as contact DB
   - Abhey built the AI layer: Gemini-powered template refinement
   - Stack: Chrome Extension MV3, Gmail API, Google Sheets API, Gemini API, OAuth 2.0
   - GitHub: https://github.com/AbheyTiwari/OutreachPro

6. CANCER DETECTION AI (Medical AI)
   - CNN + XGBoost hybrid for MRI and skin lesion analysis
   - Deployable on standard laptops without GPU
   - Stack: TensorFlow, PyTorch, XGBoost
   - GitHub: https://github.com/AbheyTiwari/MRI-SkinCancer-AI

7. FILESHARE (Privacy-First LAN File Sharing)
   - Zero cloud dependency local network file sharing
   - Stack: FastAPI, Flask, Django
   - GitHub: https://github.com/AbheyTiwari/FileShare

─── EXPERIENCE ─────────────────────────────────────────────

1. Tech, Research & Innovation Intern — Draupadi Dream Trust (Jul–Aug 2025)
   - Multi-source research on Yamuna River (religious, cultural, environmental)
   - Analysed Delhi Jal Board datasets; produced stakeholder-ready reports
   - Built Quizard during internship to accelerate document retrieval

2. Frontend Developer — BeyondRiffs, Remote (Sep–Dec 2024)
   - Rebuilt major React components prior to product launch
   - Coordinated with design and backend teams to ship under tight timelines

3. Website Developer — Mangalam Valley Resort (Jul–Nov 2023)
   - Full booking site with payment gateway, hosting, SSL

─── EDUCATION ───────────────────────────────────────────────
- B.Sc. Mathematical Sciences (3rd Year) — Maharaja Agrasen College, University of Delhi (2023–Present)
- Class XII Science (PCMB) — Kendriya Vidyalaya, Noida Sector 24 (2023)
- Class X — Kendriya Vidyalaya, Noida Sector 24 (2021)

─── AWARDS ──────────────────────────────────────────────────
- Best Paper Award — 9th National Student Academic Conference (NSAC), April 2026
  Paper: "Democratizing Intelligence: Neural Pruning, Local AI Deployment, and
  Open-Source Tools as Pathways to Equitable Access in the Global South"

─── AVAILABILITY ────────────────────────────────────────────
- Open to full-time AI/ML Engineering roles
- Open to freelance/contract work
- Available remotely or on-site in Delhi NCR
"""

SYSTEM_PROMPT = f"""You are the AI assistant on Abhey Tiwari's portfolio website.
Represent Abhey professionally. Answer questions about his skills, projects,
and experience accurately using only the information below.

{ABHEY_RESUME}

RULES:
1. Be concise — under 120 words unless a technical question needs more.
2. Be warm and professional — like a sharp executive assistant.
3. Never invent skills, projects, or credentials not listed above.
4. If someone expresses interest in hiring, collaborating, or contacting Abhey:
   - Acknowledge their interest warmly
   - Ask for their name and email if not provided
   - Tell them Abhey will be notified immediately
   - End your reply with this exact marker on its own line: [CONTACT_INTENT]
5. For anything not in the resume, say you don't have that detail but offer
   to pass the question to Abhey directly.
"""

# ── FASTAPI APP ───────────────────────────────────────────────
app = FastAPI(title="Abhey Tiwari Portfolio", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

conversation_history: list[types.Content] = []


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    contact_intent_detected: bool = False


# ── EMAIL ─────────────────────────────────────────────────────
def send_notification(user_message: str, ai_reply: str):
    html_body = f"""
    <html><body style="font-family:monospace;background:#0a0a0a;color:#f0ede8;padding:2rem;">
    <h2 style="border-bottom:1px solid #333;padding-bottom:1rem;">
        Someone wants to connect via your portfolio AI ✦
    </h2>
    <p style="color:#888">{datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
    <h3 style="color:#aaa;margin-top:1.5rem;">Their message:</h3>
    <div style="background:#1a1a1a;padding:1rem;border-left:3px solid #00ffc8;margin:.5rem 0">
        {user_message}
    </div>
    <h3 style="color:#aaa;margin-top:1.5rem;">AI replied:</h3>
    <div style="background:#1a1a1a;padding:1rem;border-left:3px solid #b06cff;margin:.5rem 0">
        {ai_reply}
    </div>
    <p style="color:#555;margin-top:2rem;font-size:.8rem">— Abhey Tiwari Portfolio AI</p>
    </body></html>
    """
    subject = f"🔔 Portfolio Contact — {datetime.now().strftime('%d %b %Y %H:%M')}"

    # Try Resend first (works on Render free tier)
    if RESEND_API_KEY:
        try:
            resend.Emails.send({
                "from": "portfolio@resend.dev",
                "to": NOTIFY_EMAIL,
                "subject": subject,
                "html": html_body,
            })
            print(f"✅ Resend notification sent to {NOTIFY_EMAIL}")
            return
        except Exception as e:
            print(f"❌ Resend error: {e}")

    # Fallback: SMTP (may fail on Render free tier due to port blocking)
    if SMTP_EMAIL and SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = SMTP_EMAIL
            msg["To"]      = NOTIFY_EMAIL
            msg.attach(MIMEText(html_body, "html"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.sendmail(SMTP_EMAIL, NOTIFY_EMAIL, msg.as_string())
            print(f"✅ SMTP notification sent to {NOTIFY_EMAIL}")
        except Exception as e:
            print(f"❌ SMTP error: {e}")
    else:
        print("⚠️  No email provider configured — add RESEND_API_KEY to Render env vars")


# ── API ROUTES — must be defined BEFORE static mount ──────────

@app.get("/health")
def health():
    return {
        "status": "online",
        "ai": "ready" if client else "missing GEMINI_API_KEY",
        "email": "ready" if SMTP_EMAIL else "not configured"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global conversation_history

    if not client:
        return ChatResponse(
            reply="AI assistant isn't configured on this deployment. Contact Abhey at abheytiwarikvs@gmail.com",
            contact_intent_detected=False
        )

    conversation_history.append(
        types.Content(role="user", parts=[types.Part(text=req.message)])
    )
    recent = conversation_history[-20:]

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=recent,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=512,
                temperature=0.7,
            ),
        )
        reply_text = response.text

    except Exception as e:
        print(f"Gemini error: {e}")
        conversation_history.pop()
        return ChatResponse(
            reply="Connection issue right now. Reach Abhey at abheytiwarikvs@gmail.com or +91 9810440326.",
            contact_intent_detected=False
        )

    contact_intent = "[CONTACT_INTENT]" in reply_text
    clean_reply    = reply_text.replace("[CONTACT_INTENT]", "").strip()

    conversation_history.append(
        types.Content(role="model", parts=[types.Part(text=clean_reply)])
    )

    if contact_intent:
        send_notification(req.message, clean_reply)

    return ChatResponse(reply=clean_reply, contact_intent_detected=contact_intent)


@app.delete("/chat/reset")
def reset():
    global conversation_history
    conversation_history = []
    return {"status": "conversation reset"}


# ── STATIC FILES ──────────────────────────────────────────────
# FastAPI serves index.html, CSS, JS, and all images from the same folder.
# This is what makes the single-repo Render deploy work.
STATIC_DIR = Path(__file__).parent

# Explicit routes for SEO files (must come before the catch-all mount)
@app.get("/robots.txt", include_in_schema=False)
def robots():
    f = STATIC_DIR / "robots.txt"
    return FileResponse(str(f)) if f.exists() else JSONResponse({}, status_code=404)

@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    f = STATIC_DIR / "sitemap.xml"
    return FileResponse(str(f), media_type="application/xml") if f.exists() else JSONResponse({}, status_code=404)

# Catch-all static mount — serves index.html at "/" and all assets
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# ── ENTRY ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print(f"\n🚀  http://localhost:{PORT}")
    print(f"    AI:    {'✅' if GEMINI_API_KEY else '⚠️  set GEMINI_API_KEY'}")
    print(f"    Email: {'✅' if SMTP_EMAIL else '⚠️  set SMTP_EMAIL + SMTP_PASSWORD'}\n")

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)