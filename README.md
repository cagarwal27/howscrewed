# How Screwed Am I?

An AI voice agent named **Czara** that you call to find out how screwed you are — then fixes it by making real phone calls on your behalf.

**Built with [ElevenLabs](https://elevenlabs.io) Conversational AI + [Firecrawl](https://firecrawl.dev) Search for [#ElevenHacks](https://hacks.elevenlabs.io)**

---

## What It Does

1. **Call Czara** — describe your situation (mechanic overcharging, landlord withholding deposit, underpaid salary)
2. **She researches** — searches live web data for fair prices, applicable laws, salary benchmarks
3. **She delivers a verdict** — exactly how screwed you are, with specific numbers and statute citations
4. **She fixes it** — makes outbound phone calls on your behalf using research data as leverage

## Architecture

```
User calls Twilio number / uses web widget
        |
ElevenLabs Agent Workflow (Czara)
        |
  [Intake] --> [Research] --> [Verdict] --> [Action] --> [Report]
                   |                          |
           Firecrawl Search            Outbound Call
           Firecrawl Extract           (ElevenLabs API)
           (via MCP + backend)
```

### Components

| Component | Technology |
|-----------|-----------|
| Inbound Agent | ElevenLabs Conversational AI + Agent Workflows |
| Outbound Agent | ElevenLabs Conversational AI (separate agent) |
| Phone Number | Twilio → ElevenLabs native integration |
| Web Research | Firecrawl Search API (native MCP) |
| Data Extraction | Firecrawl Extract API (via backend) |
| Sound Effects | ElevenLabs Sound Effects API |
| Backend | Python / FastAPI |
| Landing Page | HTML + Tailwind CSS |

### ElevenLabs Features Used

- Conversational AI with Agent Workflows (5-phase flow)
- Agent Transfer (Czara → Outbound Caller)
- Dual Voices (warm Czara + professional outbound)
- Outbound Calling API with context injection
- Sound Effects API (cha-ching on savings)
- Web Widget (`<elevenlabs-convai>`)
- Dynamic Variables + Config Override
- Native Twilio Integration

### Firecrawl Features Used

- Search API via native MCP server connection
- Extract API for structured data (phone numbers, prices)
- Multi-search for parallel queries (3-4 per scenario)
- Site operators, location targeting, time filtering

## Setup

### Prerequisites

- Python 3.11+
- ElevenLabs account + API key
- Firecrawl account + API key
- Twilio account + phone number

### Backend

```bash
cd server
pip install -r requirements.txt
cp ../.env.example .env  # Fill in your keys
python main.py
```

API docs at `http://localhost:8000/docs`

### Landing Page

```bash
cd landing
# Open index.html in browser, or deploy to Vercel:
vercel --prod
```

### Sound Effects (optional)

```bash
cd server
python generate_sounds.py
```

## Demo Results

| Scenario | Outcome |
|----------|---------|
| Mechanic overcharge ($1,800 brakes) | Fair price: $580-$750. **Saved $1,160** |
| Security deposit ($2,400, 35 days late) | Cited Civil Code 1950.5. **Recovered $2,400** |
| Salary underpayment ($71K) | Market rate: $92K-$112K. **$21,000+ gap identified** |
| **Total** | **$24,560** |

## License

MIT
