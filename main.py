"""
Abhey Tiwari — AI Portfolio Assistant
FastAPI + Gemini API (new google.genai SDK — no deprecation warnings)

SETUP:
1. pip install fastapi uvicorn google-genai python-dotenv
2. Copy .env.example to .env and fill in your keys
3. Run: uvicorn main:app --reload --port 8000

GEMINI KEY:     https://aistudio.google.com/app/apikey
GMAIL APP PASS: https://myaccount.google.com/apppasswords
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ── CONFIG ───────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NOTIFY_EMAIL   = os.getenv("NOTIFY_EMAIL", "abheytiwarikvs@gmail.com")
SMTP_EMAIL     = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD", "")

client = genai.Client(api_key=GEMINI_API_KEY)

# ── KNOWLEDGE BASE ───────────────────────────────────────────
ABHEY_RESUME = """
NAME: Abhey Tiwari
ROLE: AI Engineer & Full-Stack Developer
LOCATION: Noida, Uttar Pradesh, India (Delhi NCR)
EMAIL: abheytiwarikvs@gmail.com
PHONE: +91 9810440326
GITHUB: https://github.com/AbheyTiwari
LINKEDIN: https://www.linkedin.com/in/abheytiwari/
STATUS: Open to Work — remote or NCR-based roles

─── SUMMARY ────────────────────────────────────────────────
AI Engineer specializing in RAG pipelines, local ML deployment, and full-stack
development. Designs intelligent systems that respect privacy while delivering
real-world impact. Passionate about privacy-first AI with zero cloud dependency.

─── SKILLS ─────────────────────────────────────────────────
AI/ML:      LLMs, RAG Pipelines, LangChain, LlamaIndex, Ollama (local inference),
            CNNs, NLP, Transfer Learning, DeepFace, FAISS, ChromaDB,
            Vector Search, Embeddings, Semantic Retrieval

Languages:  Python (primary), C++, JavaScript

Frameworks: FastAPI, Flask, Django, Streamlit, React

Infra:      Linux, Git/GitHub, Docker, REST APIs, WebSockets, WebRTC

AI APIs:    Gemini API, OpenAI GPT, Ollama

─── PROJECTS ───────────────────────────────────────────────

1. MAITRI AI (Privacy-First Mental Health Companion)
   - Real-time emotionally-aware psychological companion
   - DeepFace for emotion detection from webcam
   - Ollama (Llama3/Mistral) for 100% local dialogue — zero cloud
   - Stack: FastAPI, DeepFace, Ollama, WebSockets
   - GitHub: https://github.com/AbheyTiwari/Maitri.git

2. INDICA v1.0 (Voice-Controlled AI Assistant)
   - Voice assistant with RAG, short-term memory, plugin architecture
   - Voice-to-action latency under 2 seconds
   - Stack: Python, Gemini API, RAG, SpeechRecognition, TTS
   - GitHub: https://github.com/AbheyTiwari/INDICA

3. BUGFINER AI (Automated Bug Reproduction)
   - Natural language bug reports → executable Playwright browser tests
   - Video recording and live logging. 70% less manual QA time.
   - Stack: Flask, Playwright, GPT, Asyncio
   - GitHub: https://github.com/AbheyTiwari/AI_bug_finder..git

4. QUIZARD (RAG PDF Assistant)
   - Intelligent document Q&A with semantic search
   - 90%+ answer accuracy on document queries
   - Stack: FastAPI, Streamlit, Gemini API, RAG, ChromaDB
   - GitHub: https://github.com/AbheyTiwari/Quizard

5. CANCER DETECTION AI (Medical AI)
   - CNN + XGBoost hybrid for MRI and skin lesion analysis
   - Deployable on standard laptops without GPU
   - Stack: TensorFlow, PyTorch, XGBoost
   - GitHub: https://github.com/AbheyTiwari/MRI-SkinCancer-AI

6. FILESHARE (Privacy-First LAN File Sharing)
   - Zero cloud dependency local network file sharing
   - Stack: FastAPI, Flask, Django
   - GitHub: https://github.com/AbheyTiwari/FileShare

─── EXPERIENCE ─────────────────────────────────────────────

1. Tech, Research & Innovation Intern — Draupadi Dream Trust (Jul–Aug 2025)
   - Research on Yamuna River (religious, cultural, environmental)
   - Analyzed Delhi water crisis with DJB data
   - Scripts reducing manual entry by ~40%

2. Frontend Developer — BeyondRiffs, Remote (Sep–Dec 2024)
   - Rebuilt large React platform sections overnight before launch
   - Improved load time by ~25%
   - FastAPI micro-services cutting feature turnaround by ~30%

3. Website Developer — Mangalam Valley Resort (Jul–Nov 2023)
   - Full booking site with payment gateway, hosting, SSL

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
app = FastAPI(title="Abhey Tiwari — Portfolio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_history: list[types.Content] = []


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    contact_intent_detected: bool = False


# ── EMAIL NOTIFICATION ────────────────────────────────────────
def send_notification(user_message: str, ai_reply: str):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("⚠️  SMTP not configured — skipping email")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔔 Portfolio Contact — {datetime.now().strftime('%d %b %Y %H:%M')}"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = NOTIFY_EMAIL

        html = f"""
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
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, NOTIFY_EMAIL, msg.as_string())

        print(f"✅ Notification sent to {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"❌ Email error: {e}")


# ── ROUTES ────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "online", "assistant": "Abhey Tiwari Portfolio AI"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global conversation_history

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
        reply_text = (
            "I'm having a connection issue right now. "
            "Please reach Abhey directly at abheytiwarikvs@gmail.com "
            "or call +91 9810440326."
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)