from .models import Client
# --- Client Profiles API ---
@app.get("/api/clients")
def get_clients():
    """Return all client profiles for search/listing."""
    with Session(engine) as session:
        clients = session.query(Client).all()
        return [client.dict() for client in clients]
import base64
EVENTS: List[Dict[str, Any]] = []

@app.post("/webhook")
async def webhook(request: Request):
    ct = (request.headers.get("content-type") or "").lower()

    # 1) If it's JSON, treat it as transcript/event data
    if "application/json" in ct:
        data: Dict[str, Any] = await request.json()
        EVENTS.append({"type": "json", "data": data})
        return {"ok": True, "received": "json"}

    # 2) Otherwise treat it as raw audio bytes (octet-stream / audio/*)
    raw = await request.body()

    # Store only metadata (recommended) to avoid massive memory usage
    EVENTS.append({
        "type": "audio",
        "content_type": ct,
        "bytes": len(raw),
    })

    # If you REALLY want to store the bytes for debugging, uncomment this (careful: memory!)
    # EVENTS.append({
    #     "type": "audio",
    #     "content_type": ct,
    #     "bytes": len(raw),
    #     "b64": base64.b64encode(raw[:2000]).decode("ascii")  # only first 2KB
    # })

    return {"ok": True, "received": "audio", "bytes": len(raw), "content_type": ct}


import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict, List


app = FastAPI()

# Pydantic model for transcript
class TranscriptIn(BaseModel):
    text: str
    session_id: Optional[str] = None
    source: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"service": "omi-bridge", "version": os.getenv("GIT_SHA", "dev")}

@app.post("/forward-to-ai-studio")
async def forward_to_ai_studio(request: Request):
    """
    Forwards whatever JSON body we receive to your AI Studio endpoint.
    Set AI_STUDIO_URL in Railway variables, e.g. https://your-ai-studio-endpoint/whatever
    """
    ai_url = os.getenv("AI_STUDIO_URL")
    if not ai_url:
        raise HTTPException(status_code=500, detail="Missing AI_STUDIO_URL env var")

    payload = await request.json()

    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(ai_url, json=payload)
        # Bubble up downstream errors with context
        if r.status_code >= 400:
            raise HTTPException(status_code=502, detail={"downstream_status": r.status_code, "downstream_body": r.text})

    # If downstream returns JSON, pass it through; otherwise pass text
    try:
        return r.json()
    except Exception:
        return {"ok": True, "downstream_text": r.text}
    deviceType: str = "Unknown"
    session_id: str = "frontend"
    speaker: str = "agent"

@app.post("/api/transcripts")
def save_transcript(data: TranscriptIn):
    # Save transcript as a Message in the DB
    with Session(engine) as session:
        msg = Message(
            session_id=data.session_id,
            speaker=data.speaker,
            text=data.transcript
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)
    # Optionally, extract insights (simple keyword demo)
    insights = []
    if "budget" in data.transcript.lower():
        insights.append("💰 Budget discussed")
    if "kitchen" in data.transcript.lower():
        insights.append("🍳 Kitchen preference noted")
    return {"ok": True, "message_id": msg.id, "insights": insights}

EVENTS: List[Dict[str, Any]] = []
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "banana").lower()
# If DBSession is defined elsewhere, import it here.
# Example:
# from .db import DBSession

app = FastAPI()
from fastapi import FastAPI
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4
import os

# If your file already has app = FastAPI(), keep yours and DO NOT duplicate it.
# Just make sure there's an 'app' variable that is the FastAPI instance.

EVENTS: List[Dict[str, Any]] = []
TRIGGER_WORD = os.getenv("TRIGGER_WORD", "banana").lower()

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

@app.get("/version")
def version():
    return {
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "service": os.getenv("RAILWAY_SERVICE_NAME", "unknown"),
        "env": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
    }

@app.post("/webhook")
def webhook(payload: Dict[str, Any]):
    text = str(payload.get("text", "")).strip()
    matched = TRIGGER_WORD in text.lower() if text else False

    event = {
        "id": str(uuid4()),
        "received_at": datetime.utcnow().isoformat(),
        "text": text,
        "matched": matched,
        "trigger_word": TRIGGER_WORD,
        "raw": payload,
    }

    EVENTS.insert(0, event)   # newest first
    del EVENTS[200:]          # keep last 200

    return {"ok": True, "event": event}

@app.get("/events")
def list_events(limit: int = 50):
    limit = max(1, min(limit, 200))
    return {"count": min(len(EVENTS), limit), "events": EVENTS[:limit]}

@app.get("/events/{event_id}")
def get_event(event_id: str):
    for e in EVENTS:
        if e["id"] == event_id:
            return e
    return {"detail": "Not Found"}


def make_session_id() -> str:
    # Good session IDs should be unguessable
    return secrets.token_urlsafe(24)


def upsert_client(db, client_name: Optional[str], phone: Optional[str], email: Optional[str]) -> Optional[int]:
    """
    TODO: implement DB upsert.
    Return client_id (int) or None.
    """
    # Placeholder so the server boots
    return None


def require_secret(req: Request):
    expected = os.getenv("WEBHOOK_SECRET")
    if not expected:
        raise HTTPException(status_code=500, detail="WEBHOOK_SECRET not set")

    provided = req.headers.get("X-Webhook-Secret")
    if provided != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/session/activate")
async def session_activate(request: Request):
    require_secret(request)
    return {"ok": True}
