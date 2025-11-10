from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os, time
from typing import Dict, List
from ai.prompt import SYSTEM_PROMPT
from ai.provider import GeminiProvider
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_PATH_index = Path(__file__).parent / "templates" / "index.html"
HTML_DOC_index = HTML_PATH_index.read_text(encoding="utf-8")
HTML_PATH_project = Path(__file__).parent / "templates" / "project.html"
HTML_DOC_project = HTML_PATH_project.read_text(encoding="utf-8")
HTML_PATH_skill = Path(__file__).parent / "templates" / "skill.html"
HTML_DOC_skill = HTML_PATH_skill.read_text(encoding="utf-8")
HTML_PATH_experience = Path(__file__).parent / "templates" / "experience.html"
HTML_DOC_experience = HTML_PATH_experience.read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(HTML_DOC_index)

@app.get("/#projects", response_class=HTMLResponse)
async def projects():
    return HTMLResponse(HTML_DOC_project)

@app.get("/#skills", response_class=HTMLResponse)
async def skills():
    return HTMLResponse(HTML_DOC_skill)

@app.get("/#experience", response_class=HTMLResponse)
async def experience():
    return HTMLResponse(HTML_DOC_experience)