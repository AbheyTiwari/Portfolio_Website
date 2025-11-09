# app.py
#importing necessary modules
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

HTML_PATH = Path(__file__).parent / "templates" / "index.html"
HTML_DOC = HTML_PATH.read_text(encoding="utf-8")

@app.get("/")
async def read_root():
    return HTMLResponse(content=HTML_DOC, status_code=200)