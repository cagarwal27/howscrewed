# Backend API Contract

**Base URL:** `{{BACKEND_URL}}` (Railway deployment URL, e.g. `https://howscrewed-backend.up.railway.app`)

Replace `{{BACKEND_URL}}` in webhook tool schemas with the actual deployed URL.

---

## Endpoints

### GET /api/health

Health check. Use to verify backend is running.

**Response:**
```json
{
  "status": "ok",
  "service": "howscrewed-backend",
  "timestamp": "2026-03-19T19:17:11.762703"
}
```

---

### POST /api/firecrawl-extract

Extract structured data from web pages using Firecrawl's AI-powered extraction.

**When to use:** When the agent needs clean, structured data (phone numbers, prices, addresses) from specific URLs found during search.

**Request:**
```json
{
  "urls": ["https://www.joesauto.com/services/brakes"],
  "schema_definition": {
    "type": "object",
    "properties": {
      "business_name": { "type": "string" },
      "phone_number": { "type": "string" },
      "address": { "type": "string" },
      "price_range": { "type": "string" }
    }
  },
  "prompt": "Extract the business name, phone number, address, and brake repair price range."
}
```

**Response (success):**
```json
{
  "success": true,
  "data": {
    "business_name": "Joe's Auto",
    "phone_number": "+19165551234",
    "address": "123 Main St, Sacramento CA",
    "price_range": "$580-$750"
  }
}
```

**Response (error):**
```json
{
  "detail": "Firecrawl extract failed: <error message>"
}
```

**Common schemas:**

Auto shop:
```json
{
  "type": "object",
  "properties": {
    "business_name": { "type": "string" },
    "phone_number": { "type": "string" },
    "address": { "type": "string" },
    "rating": { "type": "number" },
    "price_range": { "type": "string" }
  }
}
```

Legal statute:
```json
{
  "type": "object",
  "properties": {
    "statute_number": { "type": "string" },
    "deadline_days": { "type": "integer" },
    "penalty_description": { "type": "string" },
    "penalty_multiplier": { "type": "number" }
  }
}
```

Job listing:
```json
{
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "company": { "type": "string" },
    "salary_min": { "type": "number" },
    "salary_max": { "type": "number" },
    "location": { "type": "string" }
  }
}
```

---

### POST /api/firecrawl-multi-search

Run multiple Firecrawl searches in parallel. Returns combined results.

**When to use:** When the agent needs to research multiple aspects of a situation simultaneously (fair prices + laws + competitors).

**Request:**
```json
{
  "queries": [
    "2019 Toyota Camry brake pads rotors replacement cost",
    "auto repair shops near Sacramento reviews ratings",
    "2019 Toyota Camry brake recall NHTSA"
  ],
  "location": "Sacramento, California",
  "limit": 3
}
```

**Response (success):**
```json
{
  "success": true,
  "searches": [
    {
      "query": "2019 Toyota Camry brake pads rotors replacement cost",
      "success": true,
      "results": [
        {
          "url": "https://repairpal.com/...",
          "title": "Toyota Camry Brake Pad Replacement Cost",
          "description": "...",
          "markdown": "## Brake Pad Replacement Cost\nThe average cost..."
        }
      ]
    },
    {
      "query": "auto repair shops near Sacramento reviews ratings",
      "success": true,
      "results": [...]
    },
    {
      "query": "2019 Toyota Camry brake recall NHTSA",
      "success": true,
      "results": [...]
    }
  ],
  "total_queries": 3
}
```

**Recommended query patterns per scenario:**

Mechanic:
```json
{
  "queries": [
    "[year] [make] [model] [repair] cost",
    "auto repair shops near [city] reviews",
    "[year] [make] [model] [repair] recall NHTSA",
    "[repair] fair price [city]"
  ],
  "location": "[city], [state]"
}
```

Landlord:
```json
{
  "queries": [
    "[state] security deposit return deadline law",
    "[state] security deposit penalty landlord violation",
    "[state] civil code security deposit exact text",
    "how to get security deposit back [state]"
  ]
}
```

Salary:
```json
{
  "queries": [
    "[title] salary [city] site:glassdoor.com",
    "[title] salary [state] [experience] site:levels.fyi",
    "[title] [city] job openings salary",
    "Bureau of Labor Statistics [title] [state]"
  ]
}
```

---

### POST /api/trigger-outbound-call

Trigger an outbound phone call via ElevenLabs Conversational AI.

**When to use:** When the user confirms they want Czara to make a call on their behalf.

**Request:**
```json
{
  "target_phone": "+19165551234",
  "research_context": "Fair price for 2019 Toyota Camry brake pads and rotors in Sacramento is $580-$750 according to RepairPal. The user is being quoted $1,800 which is approximately $1,100 over fair market price.",
  "objective": "Get a quote for front and rear brake pads and rotors replacement on a 2019 Toyota Camry. Note the price, parts/labor breakdown, and earliest availability.",
  "scenario_type": "mechanic"
}
```

**Response (success):**
```json
{
  "success": true,
  "conversation_id": "conv_abc123",
  "call_sid": "CA1234567890",
  "status": "calling"
}
```

**scenario_type values:** `mechanic`, `landlord`, `salary`, `medical`, `general`

Each type adjusts the outbound agent's tone:
- `mechanic` — friendly, straightforward (getting a quote)
- `landlord` — professional, calm, firm (citing statutes)
- `salary` — professional, informative (discussing market data)
- `medical` — patient, persistent (asking about assistance programs)
- `general` — professional, clear (default)

---

### POST /api/call-complete

Webhook for outbound call completion. Called by the outbound agent system when a call ends.

**Request:**
```json
{
  "conversation_id": "conv_abc123",
  "result": "Joe's Auto quoted $640 for front and rear brake pads and rotors, including labor. Parts: $380, Labor: $260. Earliest availability: Thursday.",
  "transcript": "Agent: Hi, I'm calling to get a quote... Shop: Sure, for a Camry..."
}
```

**Response:**
```json
{
  "status": "received",
  "conversation_id": "conv_abc123"
}
```

---

### GET /api/call-result/{conversation_id}

Retrieve the result of a completed outbound call.

**Response:**
```json
{
  "success": true,
  "data": {
    "result": "Joe's Auto quoted $640...",
    "transcript": "...",
    "completed_at": "2026-03-19T19:30:00"
  }
}
```

---

## Environment Variables

The backend requires these in `.env`:

```
FIRECRAWL_API_KEY=fc-xxx          # Required for search + extract
ELEVENLABS_API_KEY=xi-xxx         # Required for outbound calls
OUTBOUND_AGENT_ID=agent_xxx       # From ElevenLabs dashboard (Person A creates)
AGENT_PHONE_NUMBER_ID=pn_xxx      # From ElevenLabs dashboard (Person A imports)
```

## Notes for Person A

- Replace `{{BACKEND_URL}}` in webhook tool schemas with the actual Railway URL
- The `firecrawl_extract` tool name in ElevenLabs should match the function name exactly
- Set webhook `response_timeout_secs` to 30 for all tools (Firecrawl can be slow)
- The `trigger_outbound_call` endpoint handles prompt construction — just pass raw research data
