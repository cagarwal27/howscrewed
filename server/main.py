import os
import asyncio
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OUTBOUND_AGENT_ID = os.getenv("OUTBOUND_AGENT_ID", "")
AGENT_PHONE_NUMBER_ID = os.getenv("AGENT_PHONE_NUMBER_ID", "")

app = FastAPI(title="How Screwed Am I? — Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory store for outbound call results (sufficient for hackathon)
call_results: dict[str, dict] = {}


# ─── Request/Response Models ───────────────────────────────────────────────────


class ExtractRequest(BaseModel):
    urls: list[str]
    schema_definition: dict
    prompt: str


class MultiSearchRequest(BaseModel):
    queries: list[str]
    location: Optional[str] = None
    limit: int = 3


class OutboundCallRequest(BaseModel):
    target_phone: str
    research_context: str
    objective: str
    scenario_type: str


class CallCompleteRequest(BaseModel):
    conversation_id: str
    result: str
    transcript: str = ""


# ─── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "howscrewed-backend",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/firecrawl-extract")
async def firecrawl_extract(req: ExtractRequest):
    """Extract structured data from URLs using Firecrawl Extract API."""
    if not FIRECRAWL_API_KEY:
        raise HTTPException(status_code=500, detail="FIRECRAWL_API_KEY not configured")

    from firecrawl import FirecrawlApp

    fc = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    try:
        result = fc.extract(
            urls=req.urls,
            params={
                "prompt": req.prompt,
                "schema": req.schema_definition,
            },
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Firecrawl extract failed: {e}")


@app.post("/api/firecrawl-multi-search")
async def firecrawl_multi_search(req: MultiSearchRequest):
    """Run multiple Firecrawl searches in parallel and return combined results."""
    if not FIRECRAWL_API_KEY:
        raise HTTPException(status_code=500, detail="FIRECRAWL_API_KEY not configured")

    from firecrawl import FirecrawlApp

    fc = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    async def search_one(query: str) -> dict:
        try:
            params = {
                "limit": req.limit,
                "scrapeOptions": {"formats": ["markdown"]},
            }
            if req.location:
                params["location"] = req.location
            result = fc.search(query=query, params=params)
            return {"query": query, "success": True, "results": result}
        except Exception as e:
            return {"query": query, "success": False, "error": str(e)}

    tasks = [search_one(q) for q in req.queries]
    searches = await asyncio.gather(*tasks)

    return {"success": True, "searches": searches, "total_queries": len(req.queries)}


@app.post("/api/trigger-outbound-call")
async def trigger_outbound_call(req: OutboundCallRequest):
    """Trigger an outbound call via ElevenLabs Conversational AI API."""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=500, detail="ELEVENLABS_API_KEY not configured"
        )
    if not OUTBOUND_AGENT_ID:
        raise HTTPException(
            status_code=500, detail="OUTBOUND_AGENT_ID not configured"
        )
    if not AGENT_PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=500, detail="AGENT_PHONE_NUMBER_ID not configured"
        )

    prompt = _build_outbound_prompt(
        req.scenario_type, req.research_context, req.objective
    )
    first_message = _build_first_message(req.scenario_type, req.research_context)

    import httpx

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.elevenlabs.io/v1/convai/twilio/outbound-call",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "agent_id": OUTBOUND_AGENT_ID,
                    "agent_phone_number_id": AGENT_PHONE_NUMBER_ID,
                    "to_number": req.target_phone,
                    "conversation_initiation_client_data": {
                        "conversation_config_override": {
                            "agent": {
                                "prompt": {"prompt": prompt},
                                "first_message": first_message,
                            }
                        },
                        "dynamic_variables": {
                            "research_data": req.research_context,
                            "objective": req.objective,
                        },
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "success": True,
                "conversation_id": data.get("conversation_id"),
                "call_sid": data.get("callSid"),
                "status": "calling",
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"ElevenLabs outbound call failed: {e.response.text}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=502, detail=f"Outbound call failed: {e}"
            )


@app.post("/api/call-complete")
async def call_complete(req: CallCompleteRequest):
    """Webhook endpoint for outbound call completion notifications."""
    call_results[req.conversation_id] = {
        "result": req.result,
        "transcript": req.transcript,
        "completed_at": datetime.now().isoformat(),
    }
    return {"status": "received", "conversation_id": req.conversation_id}


@app.get("/api/call-result/{conversation_id}")
async def get_call_result(conversation_id: str):
    """Retrieve the result of a completed outbound call."""
    if conversation_id not in call_results:
        raise HTTPException(status_code=404, detail="Call result not found")
    return {"success": True, "data": call_results[conversation_id]}


# ─── Helpers ───────────────────────────────────────────────────────────────────


def _build_outbound_prompt(scenario_type: str, research_context: str, objective: str) -> str:
    base = (
        "You are calling on behalf of a client. You have specific research data and a clear objective.\n\n"
        "IMPORTANT RULES:\n"
        "- NEVER claim to be a lawyer or legal representative\n"
        "- ALWAYS say you're 'calling on behalf of' the client\n"
        "- Keep calls focused and efficient\n"
        "- Be professional and polite\n"
        "- Report the full result back\n\n"
    )

    tone_guide = {
        "mechanic": (
            "TONE: Friendly and straightforward. You're getting a price quote.\n"
            "APPROACH: Ask for a quote for the specific repair. Get price, parts/labor breakdown, and availability.\n"
        ),
        "landlord": (
            "TONE: Professional, calm, and firm. You mean business.\n"
            "APPROACH: Cite the exact statute, deadline, and penalty exposure. "
            "Request immediate resolution. Don't threaten, but make the legal exposure clear.\n"
        ),
        "salary": (
            "TONE: Professional and informative.\n"
            "APPROACH: Present market data and open positions. Provide talking points.\n"
        ),
        "medical": (
            "TONE: Patient but persistent.\n"
            "APPROACH: Ask about financial assistance programs, itemized billing, and payment plans.\n"
        ),
    }

    prompt = base
    prompt += tone_guide.get(scenario_type, "TONE: Professional and clear.\n")
    prompt += f"\nRESEARCH DATA:\n{research_context}\n"
    prompt += f"\nOBJECTIVE:\n{objective}\n"
    return prompt


def _build_first_message(scenario_type: str, research_context: str) -> str:
    messages = {
        "mechanic": "Hi, I'm calling to get a quote for a repair. Could you help me with pricing?",
        "landlord": "Hello, I'm calling regarding a security deposit matter. Could I speak with someone about that?",
        "salary": "Hello, I'm reaching out about an open position I saw listed. Could I get some details?",
        "medical": "Hi, I'm calling about a bill. Could I speak with someone in the billing department?",
    }
    return messages.get(scenario_type, "Hello, I'm calling on behalf of a client. Could you help me with something?")


# ─── Entry Point ───────────────────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
