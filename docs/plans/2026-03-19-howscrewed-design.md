# How Screwed Am I? — Design Document

**Date:** 2026-03-19
**Hackathon:** ElevenHacks — Hack #1: Firecrawl
**Deadline:** 2026-03-26 17:00 UTC
**Team:** TBD

---

## 1. Product Overview

### One-Liner
An AI voice agent named Czara that you call to find out how screwed you are — then fixes it by making real phone calls on your behalf.

### What It Does
You call a phone number (or use a web widget), describe any situation where you're getting screwed — mechanic overcharging, landlord withholding deposit, underpaid salary, medical bill — and Czara:

1. **Assesses** your situation through natural conversation
2. **Researches** live web data in real-time (laws, fair prices, salary benchmarks, competitor quotes)
3. **Delivers a verdict** — exactly how screwed you are, with specific numbers and statute citations
4. **Takes action** — makes outbound phone calls on your behalf to mechanics, landlords, businesses, using research data as leverage

### Why This Wins
- Both sponsor tools are **load-bearing**: remove Firecrawl and Czara has no information; remove ElevenAgents and Czara can't call anyone
- The video IS the demo — real people, real savings, real phone calls
- It's not a toy — it saves real money ($1,160 at the mechanic, $2,400 from the landlord, $21K+ salary gap identified)
- The phone number is the CTA — "Call Czara. Tell her how screwed you are."

### Branding
- **Product name:** How Screwed Am I?
- **Agent name:** Czara
- **Domain:** howscrewed.ai (or best available alternative)
- **Tagline:** "Call Czara. Tell her how screwed you are."

---

## 2. Architecture Overview

### High-Level Flow

```
User calls Twilio number / uses web widget
        ↓
ElevenLabs Agent Workflow (5-phase flow)
        ↓
Phase 1: INTAKE — Czara gathers situation details
        ↓
Phase 2: RESEARCH — Firecrawl Search + Extract (3-4 calls per scenario)
        ↓
Phase 3: VERDICT — "Here's how screwed you are" + exact numbers/statutes
        ↓
Phase 4: ACTION — Czara triggers outbound call via backend API
        ↓
Phase 5: REPORT — Czara tells user the outcome
```

### Component Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│  ┌──────────────────┐  ┌─────────────────────────────────────┐  │
│  │  Twilio Phone #   │  │  Landing Page (howscrewed.ai)       │  │
│  │  (inbound calls)  │  │  - ElevenLabs <convai> widget      │  │
│  └────────┬─────────┘  │  - Phone number CTA                 │  │
│           │             │  - Scenario examples                │  │
│           │             └──────────────┬──────────────────────┘  │
└───────────┼────────────────────────────┼────────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ELEVENLABS AGENTS PLATFORM                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  CZARA — Inbound Agent (Agent Workflow)                    │  │
│  │                                                            │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐              │  │
│  │  │ Intake   │──▶│ Research │──▶│ Verdict  │              │  │
│  │  │ Subagent │   │ Subagent │   │ Subagent │              │  │
│  │  └──────────┘   └────┬─────┘   └────┬─────┘              │  │
│  │                      │              │                      │  │
│  │              ┌───────▼───────┐      │                      │  │
│  │              │ Dispatch Tools│      ▼                      │  │
│  │              │ - FC Search   │  ┌──────────┐              │  │
│  │              │ - FC Extract  │  │ Action   │              │  │
│  │              └───────────────┘  │ Subagent │              │  │
│  │                                 └────┬─────┘              │  │
│  │                                      │ transfer_to_agent  │  │
│  └──────────────────────────────────────┼────────────────────┘  │
│                                         ▼                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  OUTBOUND CALLER — Separate Agent                          │  │
│  │  - Voice: Professional, firm                               │  │
│  │  - Prompt: Injected research data + objective              │  │
│  │  - Makes real outbound calls via Twilio                    │  │
│  │  - Cites statutes, prices, data as leverage                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Tools connected:                                                │
│  - Firecrawl MCP Server (native)                                │
│  - Webhook: Backend /api/trigger-outbound-call                  │
│  - Webhook: Backend /api/firecrawl-extract                      │
│  - System: transfer_to_agent                                    │
│  - System: end_call                                             │
│  - ElevenLabs Sound Effects (cha-ching, dramatic sting)         │
└─────────────────────────────────────────────────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python/FastAPI)                    │
│                                                                  │
│  POST /api/trigger-outbound-call                                │
│    → Receives: target_phone, research_context, objective        │
│    → Calls ElevenLabs Outbound API with config override         │
│    → Returns: conversation_id, callSid                          │
│                                                                  │
│  POST /api/call-complete (webhook)                              │
│    → Receives: outbound call result                             │
│    → Stores result, available for inbound agent to query        │
│                                                                  │
│  POST /api/firecrawl-extract                                    │
│    → Receives: url(s), schema, prompt                           │
│    → Calls Firecrawl Extract API                                │
│    → Returns: structured JSON (phone, price, address)           │
│                                                                  │
│  POST /api/firecrawl-multi-search (optional)                    │
│    → Receives: array of queries                                 │
│    → Runs multiple Firecrawl searches in parallel               │
│    → Returns: synthesized results                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
            │                            │
            ▼                            ▼
┌──────────────────────┐  ┌──────────────────────────────────────┐
│  FIRECRAWL API       │  │  TWILIO                              │
│  - /search           │  │  - Inbound phone number              │
│  - /extract          │  │  - Outbound calling                  │
│  - MCP server        │  │  - Call recording                    │
└──────────────────────┘  └──────────────────────────────────────┘
```

---

## 3. Component Details

### 3.1 Czara — Inbound Agent (ElevenLabs Agent Workflow)

**Platform:** ElevenLabs Conversational AI — Agent Workflows
**Voice:** Feminine, warm, practical. Smart friend energy. Calm but competent.
**LLM:** Claude Sonnet 4 or GPT-4o (best for tool calling reliability)
**Language:** English (primary)

#### Workflow Phases

**Phase 1: Intake Subagent**

Purpose: Greet the user, understand their situation, gather key details.

```
System prompt direction:
- You are Czara, the "How Screwed Am I?" agent
- Personality: warm, direct, slight dry humor, never condescending
- Greet casually: "Hey, I'm Czara. So... how screwed are you?"
- Ask clarifying questions to understand the situation
- Gather: what happened, where (city/state), when, dollar amounts, names of businesses/people
- Don't research yet — just listen and understand
- Once you have enough details, say something like "Alright, let me look into this"
```

Tools: None
Routing: Intent-based edges to Phase 2 (when enough details gathered)

**Phase 2: Research Subagent**

Purpose: Use Firecrawl to research the user's exact situation with live web data.

```
System prompt direction:
- You now have the user's situation from Phase 1
- Your job: research thoroughly before making any claims
- Make MULTIPLE searches — at minimum 3 per scenario
- Search for: fair prices/market rates, applicable laws/statutes, penalties/deadlines, alternatives/competitors
- Use Firecrawl Extract to get structured data (phone numbers, prices) from relevant pages
- Think out loud briefly: "Let me check the law on this..." or "Looking up fair prices in your area..."
- Do NOT guess or make up data — only cite what Firecrawl returns
- When research is complete, transition naturally to delivering findings
```

Tools:
- `firecrawl_search` (via MCP server) — web search with markdown content
- `firecrawl_extract` (via webhook to backend) — structured data extraction
- Sound effect: subtle "research" audio cue (optional)

Routing: Automatic transition to Phase 3 when research is complete

**Phase 3: Verdict Subagent**

Purpose: Deliver the "how screwed are you" assessment with specific data.

```
System prompt direction:
- Synthesize all research into a clear, specific verdict
- Lead with the headline: "Okay, here's the deal..." or "So... you're getting screwed."
- Be SPECIFIC: cite exact dollar amounts, statute numbers, deadlines, penalty amounts
- Give the "screwed score" — how bad is it on a scale
- For overcharges: state the fair price range vs what they're being charged
- For legal violations: cite the exact statute, deadline, and penalty
- For salary: state the market range and how far below they are
- After delivering the verdict, pause. Let it sink in.
- Then offer to take action: "Want me to call them?" or "I can reach out to some other shops for quotes"
- If user declines, give them a summary of what to do themselves and end gracefully
```

Tools:
- `play_sound_effect` (webhook to backend or pre-generated) — "cha-ching" for money saved, dramatic sting for bad news

Routing:
- User says yes → Phase 4 (Action)
- User says no → End node (graceful goodbye with summary)

**Phase 4: Action Subagent**

Purpose: Initiate outbound call on behalf of the user.

```
System prompt direction:
- User has agreed to let you take action
- Confirm: "Alright, I'm going to call [business/person] right now"
- Trigger the outbound call tool with: phone number, research context, objective
- Tell user: "I'm on the phone with them now. I'll let you know how it goes."
- While waiting: provide encouragement or additional context
- When result comes back, transition to Phase 5
```

Tools:
- `trigger_outbound_call` (webhook to backend `/api/trigger-outbound-call`)
- `transfer_to_agent` (system tool — transfers to outbound caller agent if using agent transfer instead of API)

Routing: To Phase 5 when outbound call completes (or to outbound agent via transfer)

**Phase 5: Report Back Subagent**

Purpose: Deliver the outcome of the outbound call.

```
System prompt direction:
- Report what happened on the outbound call
- Be specific: "Joe's Auto quoted $640 including labor. Mike's Brakes said $710."
- For landlord: "I spoke with your landlord's office. I cited Section 1950.5 and the penalty exposure. They said they'll process the refund within 5 business days."
- Offer next steps: "Want me to book with Joe's?" or "Want me to send you the job listings?"
- End warmly: "Glad I could help. Call me anytime you're getting screwed."
```

Tools:
- `play_sound_effect` — victory cha-ching
- `end_call` (system tool)

Routing: End node

#### Dynamic Variables

```json
{
  "user_name": "string (if provided)",
  "user_city": "string",
  "user_state": "string",
  "situation_type": "string (mechanic|landlord|salary|medical|parking|other)",
  "situation_details": "string (summary of their problem)",
  "research_results": "string (JSON of all Firecrawl findings)",
  "target_phone": "string (phone number to call)",
  "outbound_result": "string (what happened on the outbound call)"
}
```

### 3.2 Outbound Caller Agent (Separate ElevenLabs Agent)

**Platform:** ElevenLabs Conversational AI
**Voice:** Professional, confident, firm but not aggressive. Should sound like a real person calling — not a robot, not an AI assistant.
**LLM:** Same as Czara (Claude Sonnet 4 or GPT-4o)
**Triggered via:** ElevenLabs Outbound Call API (`POST /v1/convai/twilio/outbound-call`)

```
System prompt direction:
- You are calling on behalf of a client
- You have specific research data and an objective (injected via conversation_config_override)
- Scenario-specific behavior:

  FOR MECHANIC/PRICE QUOTES:
  - Be friendly and straightforward
  - "Hi, I'm calling to get a quote for [specific repair] on a [year make model]"
  - Get the price, parts and labor breakdown, availability
  - Thank them and end politely

  FOR LANDLORD/LEGAL:
  - Be professional, calm, and firm
  - "I'm calling regarding the security deposit for [address]"
  - Cite the exact statute number, deadline, and penalty exposure
  - Request resolution: "We'd like to resolve this before pursuing further action"
  - Document their response

  FOR GENERAL INQUIRIES:
  - Professional and clear
  - State what you need, get the information, end politely

- NEVER claim to be a lawyer or legal representative
- ALWAYS say you're "calling on behalf of" the client
- Keep calls focused and efficient — get what you need and end
- Report the full result back
```

**Context injection via outbound call API:**

```json
{
  "agent_id": "outbound_agent_id",
  "agent_phone_number_id": "twilio_number_id",
  "to_number": "+15551234567",
  "conversation_initiation_client_data": {
    "conversation_config_override": {
      "agent": {
        "prompt": {
          "prompt": "You are calling Joe's Auto at +15551234567 on behalf of a client. Get a quote for front and rear brake pads and rotors replacement on a 2019 Toyota Camry. Research shows fair price is $580-$750. Get their price, parts/labor breakdown, and earliest availability."
        },
        "first_message": "Hi, I'm calling to get a quote for a brake job on a 2019 Toyota Camry — front and rear pads and rotors. Could you help me with pricing?"
      }
    },
    "dynamic_variables": {
      "repair_type": "Front and rear brake pads and rotors",
      "vehicle": "2019 Toyota Camry",
      "fair_price_range": "$580-$750",
      "client_location": "Sacramento, CA"
    }
  }
}
```

### 3.3 Backend Server (Python/FastAPI)

**Framework:** FastAPI with async support
**Deployment:** Railway
**Purpose:** Thin orchestration layer for outbound calls and enhanced Firecrawl operations

#### Endpoints

**`POST /api/trigger-outbound-call`**

Called by Czara's webhook tool when user agrees to take action.

```python
from fastapi import FastAPI
from elevenlabs import ElevenLabs

app = FastAPI()
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

@app.post("/api/trigger-outbound-call")
async def trigger_outbound_call(
    target_phone: str,
    research_context: str,
    objective: str,
    scenario_type: str
):
    # Build the outbound agent's prompt with research data
    prompt = build_outbound_prompt(scenario_type, research_context, objective)
    first_message = build_first_message(scenario_type, research_context)

    # Trigger outbound call via ElevenLabs API
    result = client.conversational_ai.twilio.outbound_call(
        agent_id=OUTBOUND_AGENT_ID,
        agent_phone_number_id=TWILIO_PHONE_NUMBER_ID,
        to_number=target_phone,
        conversation_initiation_client_data={
            "conversation_config_override": {
                "agent": {
                    "prompt": {"prompt": prompt},
                    "first_message": first_message
                }
            },
            "dynamic_variables": {
                "research_data": research_context,
                "objective": objective
            }
        }
    )

    return {"conversation_id": result.conversation_id, "status": "calling"}
```

**`POST /api/call-complete`**

Webhook endpoint called when outbound call finishes.

```python
@app.post("/api/call-complete")
async def call_complete(conversation_id: str, result: str, transcript: str):
    # Store result for Czara to query
    call_results[conversation_id] = {
        "result": result,
        "transcript": transcript,
        "completed_at": datetime.now()
    }
    return {"status": "received"}
```

**`POST /api/firecrawl-extract`**

Wraps Firecrawl Extract for structured data extraction.

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)

@app.post("/api/firecrawl-extract")
async def extract_data(urls: list[str], schema: dict, prompt: str):
    result = firecrawl.extract(
        urls=urls,
        prompt=prompt,
        schema=schema
    )
    return result
```

**`POST /api/firecrawl-multi-search`** (optional)

Runs multiple Firecrawl searches in parallel for comprehensive research.

```python
import asyncio

@app.post("/api/firecrawl-multi-search")
async def multi_search(queries: list[str], location: str = None):
    tasks = [
        firecrawl.search(
            query=q,
            limit=3,
            scrape_options={"formats": ["markdown"]},
            location=location
        )
        for q in queries
    ]
    results = await asyncio.gather(*tasks)
    return {"searches": results}
```

**`POST /api/generate-sound-effect`** (optional)

Generates or returns pre-cached sound effects.

```python
@app.post("/api/generate-sound-effect")
async def generate_sound(effect_type: str):
    # Pre-generated effects for common scenarios
    effects = {
        "money_saved": "cash_register_ching.mp3",
        "bad_news": "dramatic_sting.mp3",
        "victory": "triumphant_fanfare.mp3",
        "researching": "typing_clicks.mp3"
    }

    if effect_type in effects:
        return {"audio_url": f"/static/sounds/{effects[effect_type]}"}

    # Generate dynamically via ElevenLabs Sound Effects API
    result = client.text_to_sound_effects.convert(
        text=effect_type,
        duration_seconds=3
    )
    return {"audio": result}
```

### 3.4 Firecrawl Integration (Showing Depth)

The agent uses Firecrawl in **three distinct ways** — this shows judges maximum integration depth:

#### Way 1: Firecrawl Search via MCP (Native)

Connected directly to ElevenAgents as an MCP server.
- URL: `https://mcp.firecrawl.dev/{api-key}/v2/mcp`
- The agent calls this naturally during conversation for real-time web searches
- Supports site: operators, location targeting, time filtering

#### Way 2: Firecrawl Extract via Backend Webhook

For structured data extraction when the agent needs clean JSON (phone numbers, prices).

```
Agent calls webhook tool → Backend /api/firecrawl-extract → Firecrawl Extract API
                                                          → Returns structured JSON
```

Schema examples:

```json
// Auto shop extraction
{
  "type": "object",
  "properties": {
    "business_name": {"type": "string"},
    "phone_number": {"type": "string"},
    "address": {"type": "string"},
    "rating": {"type": "number"},
    "price_range": {"type": "string"}
  }
}

// Legal statute extraction
{
  "type": "object",
  "properties": {
    "statute_number": {"type": "string"},
    "deadline_days": {"type": "integer"},
    "penalty_description": {"type": "string"},
    "penalty_multiplier": {"type": "number"}
  }
}
```

#### Way 3: Firecrawl Multi-Search via Backend Webhook

For running parallel searches to build a complete picture quickly.

```
Agent calls webhook tool → Backend /api/firecrawl-multi-search
  → Parallel: Search fair prices
  → Parallel: Search applicable law
  → Parallel: Search penalty amounts
  → Parallel: Search competitor businesses
  → Returns synthesized results
```

### 3.5 ElevenLabs Feature Usage (Showing Depth)

| Feature | How We Use It | Why It Impresses |
|---------|--------------|-----------------|
| **Conversational AI** | Core product — Czara voice agent | Foundation |
| **Agent Workflows** | 5-phase conversation flow with subagent nodes | Shows sophisticated flow design |
| **Agent Transfer** | Native handoff from Czara to outbound caller | Built-in feature most teams won't use |
| **Outbound Calling API** | Programmatic outbound calls with context injection | The differentiator — AI acts, not just talks |
| **Dual Voices** | Czara (warm) vs Outbound (professional) | Shows voice selection intentionality |
| **Sound Effects API** | "Cha-ching" on money saved, dramatic stings | Fun polish, uses another ElevenLabs product |
| **Web Widget** | `<elevenlabs-convai>` on landing page | Full platform usage |
| **Dynamic Variables** | Personalized prompts per conversation | Shows API depth |
| **Conversation Config Override** | Inject research into outbound agent | Advanced API usage |
| **Twilio Native Integration** | Phone number connected via dashboard | Proper telephony setup |

### 3.6 Landing Page

**Tech:** Single `index.html` + Tailwind CSS (CDN) + ElevenLabs widget
**Deployment:** Vercel (or GitHub Pages)
**Domain:** howscrewed.ai (or best available)

#### Page Structure

```
┌─────────────────────────────────────────────┐
│  HERO SECTION                               │
│  "How Screwed Am I?"                        │
│  "Call Czara. She'll find out — then fix it."│
│  [📞 Call: (XXX) XXX-XXXX]  [🎙️ Try Now]   │
│  (Try Now opens ElevenLabs widget)          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  HOW IT WORKS (3 steps)                     │
│  1. Call Czara → 2. She researches →        │
│  3. She calls them for you                  │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  SCENARIO CARDS                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Mechanic │ │ Landlord │ │ Salary   │    │
│  │ Saved    │ │ Recovered│ │ Found    │    │
│  │ $1,160   │ │ $2,400   │ │ $21,000+ │    │
│  └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  FOOTER                                      │
│  Built with ElevenLabs + Firecrawl           │
│  for #ElevenHacks                            │
│  [GitHub] [Twitter]                          │
└─────────────────────────────────────────────┘

<!-- ElevenLabs Widget (floating) -->
<elevenlabs-convai agent-id="AGENT_ID"></elevenlabs-convai>
```

---

## 4. Scenario Playbooks

### 4.1 Mechanic Overcharge

**Trigger phrase:** "They're quoting me $X for [repair] on my [car]"

**Firecrawl searches:**
1. `"[year] [make] [model] [repair] cost"` → fair price range
2. `"auto repair shops near [city] reviews"` → alternatives
3. `"[year] [make] [model] [repair] recall NHTSA"` → check recalls
4. Extract from shop pages: `{name, phone, address, rating}`

**Czara's verdict:**
> "For a 2019 Toyota Camry, brake pads and rotors in Sacramento should cost $580 to $750. You're being quoted $1,800 — that's about $1,100 over fair market. Want me to call some other shops for quotes?"

**Outbound action:** Call 2-3 shops, get quotes for the exact repair.

**Result:**
> "Joe's Auto quoted $640 including labor. Mike's Brakes said $710. Want me to book with Joe's?"

### 4.2 Security Deposit Not Returned

**Trigger phrase:** "My landlord hasn't returned my deposit" / "Moved out X weeks ago"

**Firecrawl searches:**
1. `"[state] security deposit return deadline law"` → statute
2. `"[state] security deposit penalty landlord violation"` → penalties
3. `"[state] civil code security deposit text"` → exact statute text
4. Extract from legal page: `{statute_number, deadline_days, penalty_multiplier}`

**Czara's verdict:**
> "In California, landlords must return your deposit within 21 days with an itemized statement. It's been 35 days. Under Civil Code Section 1950.5, you may be entitled to up to twice the deposit — that's $4,800 in penalties. Want me to call your landlord?"

**Outbound action:** Call landlord, cite statute, state penalty exposure, request immediate return.

**Result:**
> "I spoke with your landlord's office. Cited Section 1950.5 and the $4,800 penalty exposure. They said they'll process the refund within 5 business days."

### 4.3 Salary Underpayment

**Trigger phrase:** "I think I'm underpaid" / "What should I be making?"

**Firecrawl searches:**
1. `"[title] salary [city] site:glassdoor.com"` → Glassdoor data
2. `"[title] salary [state] [experience] site:levels.fyi"` → Levels data
3. `"[title] [city] job openings salary"` → current postings
4. `"Bureau of Labor Statistics [title] [state]"` → BLS data

**Czara's verdict:**
> "Based on Glassdoor, Levels.fyi, and current job postings, your role in Sacramento pays $92,000 to $112,000. You're at $71,000. That's $21,000 to $41,000 below market rate."
> *[pause for reaction]*
> "I found 4 open positions at your level paying $95K or more. Want me to send you the links? Having competing offers is the strongest leverage for a raise conversation."

**Outbound action:** No outbound call needed — compile job listings and provide talking points for raise negotiation.

### 4.4 Medical Bill (Bonus)

**Trigger:** "They charged me $X for [procedure]"

**Searches:** Fair price (Healthcare Bluebook), hospital financial assistance policy, No Surprises Act protections, negotiation strategies.

**Verdict:** Fair price comparison + financial assistance program if available.

**Action:** Walk through dispute process, optionally call billing department.

### 4.5 Parking Ticket (Bonus)

**Trigger:** "I got a ticket for [violation]"

**Searches:** Municipal signage requirements, contest process, precedent for dismissal.

**Verdict:** Odds of winning a contest + exact steps.

**Action:** Tell them how to contest with specific evidence to gather.

### 4.6 General Catch-All

Czara should handle ANY situation — subscriptions, warranties, insurance claims, contractor disputes, etc. The system prompt instructs her to:
1. Understand the situation through questions
2. Research using Firecrawl (appropriate searches for the domain)
3. Deliver a specific, data-backed verdict
4. Offer actionable next steps (outbound call if applicable)

---

## 5. Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Inbound Agent** | ElevenLabs Conversational AI + Agent Workflows | Czara, 5-phase workflow |
| **Outbound Agent** | ElevenLabs Conversational AI | Separate agent, triggered via API |
| **Phone Number** | Twilio → ElevenLabs native integration | Inbound + outbound capable |
| **Web Research** | Firecrawl Search API (via MCP) | Native MCP connection to agent |
| **Data Extraction** | Firecrawl Extract API (via backend webhook) | Structured phone/price/address data |
| **Sound Effects** | ElevenLabs Sound Effects API | Pre-generated library + dynamic |
| **Backend** | Python / FastAPI | Thin orchestration layer |
| **Landing Page** | HTML + Tailwind CSS (CDN) | Single file, ElevenLabs widget |
| **Backend Hosting** | Railway | Fast deploy, free tier |
| **Landing Hosting** | Vercel | Static, instant |
| **Domain** | howscrewed.ai (or alternative) | TBD availability |

### Dependencies

```
# Python backend
fastapi
uvicorn
elevenlabs
firecrawl-py
python-dotenv
httpx
```

### Environment Variables

```
ELEVENLABS_API_KEY=
FIRECRAWL_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
CZARA_AGENT_ID=
OUTBOUND_AGENT_ID=
AGENT_PHONE_NUMBER_ID=
```

---

## 6. Deployment Plan

### Pre-Build Setup (Before coding)
1. Create ElevenLabs account, claim free hackathon credits
2. Create Firecrawl account, claim free hackathon credits (10K)
3. Buy Twilio phone number (~$1/month)
4. Set up Railway account (backend deployment)
5. Set up Vercel account (landing page)
6. Register domain (howscrewed.ai or alternative)

### Infrastructure
- **Railway**: Auto-deploys from GitHub on push. FastAPI server with uvicorn.
- **Vercel**: Auto-deploys static HTML from GitHub on push.
- **Twilio**: Phone number imported into ElevenLabs via dashboard.
- **ElevenLabs**: Agents configured via dashboard + API. Workflows built in visual editor.
- **Firecrawl MCP**: Connected to ElevenLabs agent via dashboard MCP settings.

---

## 7. Video Production Plan

### Master Video: 90 seconds

```
[0-3s]   HOOK: Text "This AI just saved me $24,000" + Czara's voice mid-call
[3-5s]   Title: "How Screwed Am I?" + phone number
[5-25s]  SCENE 1: MECHANIC
         - Real auto shop parking lot
         - Person: "They want $1,800 for brakes"
         - Calls Czara, quick cuts of conversation
         - Czara: "$580-$750 is fair. You're being overcharged $1,100."
         - Czara calls other shops, gets $640 quote
         - Text overlay: SAVED $1,160
[25-45s] SCENE 2: LANDLORD
         - Someone's apartment, frustrated
         - Person: "$2,400 deposit, 5 weeks, nothing"
         - Czara cites Civil Code 1950.5, penalty exposure
         - Czara CALLS the landlord (outbound call audio)
         - Venmo notification: $2,400
         - Text overlay: RECOVERED $2,400
[45-65s] SCENE 3: SALARY
         - Person at desk
         - "I think I'm underpaid"
         - Natural back-and-forth with Czara
         - Czara: "$92K-$112K market rate. You're at $71K."
         - Person's face. Silence.
         - Text overlay: UNDERPAID BY $21,000+
[65-75s] BONUS: Quick funny one
         - "I've been using my roommate's HBO for 3 years"
         - Czara: "Technically a CFAA violation but... you're fine"
         - Quick laugh, shows personality
[75-85s] RUNNING TOTAL
         - $1,160 + $2,400 + $21,000 = $24,560
[85-90s] CTA
         - "Call Czara. Tell her how screwed you are."
         - Phone number + howscrewed.ai
         - "Built with ElevenLabs + Firecrawl | #ElevenHacks"
```

### Platform Cuts
- **TikTok/Reels (45-60s):** Hook + mechanic + landlord + total. Vertical 9:16. Bold captions.
- **X/Twitter (30-45s):** Landlord scene only — strongest standalone. Tweet: "I built an AI that calls your landlord and cites the exact law they're breaking."
- **LinkedIn (90s full):** Full video + story-format text post. Lead with salary scene framing.

### Filming Requirements
- Film on iPhone in 4K, handheld (documentary feel)
- Real locations: auto shop parking lot, apartment, desk/office
- Show real phone screen with call timer (proof it's real)
- Capture genuine reactions
- AI voice must be clear and audible (speakerphone or good audio capture)
- Auto-captions via CapCut (mandatory for muted viewing)
- Colored text overlays for dollar amounts (green = saved)

---

## 8. Submission Checklist

### Required
- [ ] Working phone number anyone can call (Twilio + ElevenLabs)
- [ ] Web widget on landing page (ElevenLabs `<convai>`)
- [ ] Landing page live at domain
- [ ] Main video: 90 seconds, hackathon submission
- [ ] GitHub repo with clean README
- [ ] Description written for submission form
- [ ] Cover image (screenshot of landing page or video frame)
- [ ] At least 1 social media post (X required)

### Social Posts (+50 pts each)
- [ ] X/Twitter post — landlord scene clip + hook tweet
- [ ] LinkedIn post — story format + full video
- [ ] Instagram Reel — vertical cut, 45-60s
- [ ] TikTok — vertical cut, 45-60s, "POV:" format

### Technical Quality
- [ ] Czara handles any situation thrown at her (not just the 3 demo scenarios)
- [ ] Firecrawl makes 3-4 distinct calls per scenario (shows depth)
- [ ] Outbound calling works end-to-end
- [ ] Sound effects play at key moments
- [ ] Agent Workflow has clear multi-phase flow
- [ ] Dual voices are noticeably different and appropriate

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Firecrawl returns no/bad results | Hardcode fallback data for demo scenarios. Agent gracefully says "let me try another search" |
| Outbound call fails | Build retry logic. For video, use controlled calls to teammate's phone |
| Twilio number not ready | Web widget is the backup — always works |
| Agent Workflow too complex | Start with single agent + tools, upgrade to workflows once working |
| ElevenLabs rate limits | Cache common searches. Pre-generate sound effects. |
| Voice quality issues on phone | Test extensively. Use high-quality Twilio number. Optimize TTS settings. |
| Legal concerns about "AI lawyer" claims | NEVER claim to be a lawyer. Say "calling on behalf of" not "representing." Cite DoNotPay FTC case as cautionary example. |

---

## 10. Design Decisions Log

### D1: Demo Realness Strategy
**Decision:** "Real where it matters, controlled where it's risky"
- Inbound call experience (phone + web widget) must be 100% real and functional — judges will test it
- Firecrawl integration must be live with multiple dynamic searches per conversation
- Outbound calling built as real working pipeline, but filmed with controlled calls (teammate plays mechanic/landlord)
- **Why:** Video is weighted heaviest in judging. Demo URL exists so judges will try inbound. Firecrawl founders will check search integration depth. Outbound is the video wow factor but unreliable with real businesses.

### D2: Tech Stack
**Decision:** Python/FastAPI for backend
- Best SDK support for both ElevenLabs and Firecrawl
- Async out of the box for external API calls
- Auto-generated docs at /docs for debugging
- Firecrawl connects to ElevenAgents via native MCP — backend is thinner than originally planned
- Backend mainly handles: outbound call orchestration + optional enhanced search chains

### D3: Voice Strategy — Dual Voice
**Decision:** Two distinct voices
- **Czara (inbound agent):** Feminine, warm, practical — smart friend who's seen it all. Casual enough for "how screwed am I?" energy, competent enough to cite statutes.
- **Outbound caller agent:** Professional, firm — "calling on behalf of my client" energy. Different voice to show ElevenLabs range.
- **Why:** Showcases ElevenLabs voice variety for judges. Makes narrative sense — talking to you vs. calling your landlord should feel different.

### D4: Agent Name
**Decision:** Agent is named "Czara"

### D5: Scenario Scope
**Decision:** Build all scenarios in the agent, film only 2-3 for video
- Czara can handle ANY situation (mechanic, landlord, salary, medical bills, parking tickets, subscriptions, etc.)
- Video focuses on the 2-3 most cinematic scenarios
- **Why:** Shows depth when judges test it. Keeps video production focused and high-quality.

### D6: Branding
**Decision:** "How Screwed Am I?" is the product name, Czara is the agent
- Domain: howscrewed.ai (or similar available domain)
- Tagline direction: "Call Czara. Tell her how screwed you are."
- **Why:** "How Screwed Am I?" is inherently viral (curiosity bait). Czara as the agent gives it personality. Combination is stronger than either alone.

### D7: Conversation Architecture
**Decision:** Full Agent Workflows with maximum tool integration
- Use ElevenLabs Agent Workflows visual builder for multi-step inbound flow
- Subagent nodes for each conversation phase (assess, research, verdict, action)
- Dispatch tool nodes for Firecrawl Search + Extract calls
- Native `transfer_to_agent` for inbound→outbound handoff
- Outbound agent also uses workflows for its call script
- **Why:** Judges (Firecrawl founders + ElevenLabs Growth lead) will specifically evaluate depth of tool integration. Using Agent Workflows shows deep ElevenLabs platform knowledge. Maximizes creative use of both sponsor tools.

### D8: Integration Depth — Maximum Tool Usage
**Decision:** Integrate as many ElevenLabs + Firecrawl features as possible
- **Firecrawl Search**: Real-time web research during calls (via MCP + webhook)
- **Firecrawl Extract**: Structured data extraction (phone numbers, prices, addresses)
- **Firecrawl Agent**: Background deep research for complex scenarios (not real-time)
- **ElevenLabs Agent Workflows**: Visual multi-step conversation flows
- **ElevenLabs Agent Transfer**: Native handoff between Czara and outbound agent
- **ElevenLabs Sound Effects**: "Cha-ching" on money saved, dramatic stings
- **ElevenLabs Web Widget**: Landing page integration
- **Twilio Call Recording + Transcription**: Record outbound calls, show transcripts
- **Why:** Hackathon scoring rewards creative, deep integration of sponsor tools. "Don't just use the APIs at their most basic level. Dig into the advanced features." Neither tool should be decorative — both must be load-bearing.

### D9: Voice Cloning
**Decision:** Skip for hackathon. Revisit post-hackathon.
- Two distinct voices (Czara warm/casual + outbound professional/firm) is already a strong ElevenLabs showcase
- Voice cloning adds complexity without improving the core call experience
- **Why:** Focus on making the call experience flawless. Don't let shiny features dilute core quality.

### D10: Auto-Generated Video Reports (Remotion)
**Decision:** Skip for hackathon. Revisit post-hackathon.
- The hackathon submission video IS the viral content
- Users don't need auto-generated clips for the demo to win
- **Why:** Same principle — core call experience first. This is a post-hackathon growth feature, not a hackathon-winning feature.

---

## 11. Key Reference Repos

| Repo | What to Use |
|------|------------|
| [elevenlabs/elevenlabs-examples](https://github.com/elevenlabs/elevenlabs-examples) | Official templates, Twilio + ConvAI examples |
| [nibodev/elevenlabs-twilio-i-o](https://github.com/nibodev/elevenlabs-twilio-i-o) | Inbound + outbound Twilio wiring |
| [twilio-labs/call-gpt](https://github.com/twilio-labs/call-gpt) | Function calling during live calls pattern |
| [firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) | MCP server setup for agent integration |
| [firecrawl/firecrawl-app-examples](https://github.com/firecrawl/firecrawl-app-examples) | Firecrawl usage patterns |
| [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | Alternative orchestration if needed |
| [vocodedev/vocode-core](https://github.com/vocodedev/vocode-core) | Outbound call architecture patterns |

---

*Built with Firecrawl Search + ElevenAgents for ElevenHacks.*
