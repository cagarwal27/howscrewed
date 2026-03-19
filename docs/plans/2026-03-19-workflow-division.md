# How Screwed Am I? — Workflow Division

**Date:** 2026-03-19
**Companion to:** `2026-03-19-howscrewed-design.md`
**Team:** 2 developers (Person A + Person B)
**Deadline:** 2026-03-26 17:00 UTC

---

## Prerequisites

Before starting any phase, both developers need:

- [ ] Git repo cloned locally
- [ ] Claude Code installed and authenticated
- [ ] Agent Teams enabled: add `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to `settings.json` under `env`
- [ ] Read `docs/plans/2026-03-19-howscrewed-design.md` fully

---

## Phase Map

```
Phase 0: Account Setup        ░░  30 min   Together    Day 1
Phase 1: Parallel Build       ████ 2-4 hrs  Split       Day 1-2
Phase 2: Integration & Wiring ██  1-2 hrs  Together    Day 2
Phase 3: Prompt Eng & Polish  ███ 2-3 hrs  Together    Day 2-3
Phase 4: Video Production     █████ 4-6 hrs  Together    Day 3-5
Phase 5: Social & Submission  █  1 hr     Together    Day 5-6
```

---

## Phase 0: Account Setup (Together, ~30 min)

Both developers sit together. Goal: all credentials ready, no blockers for Phase 1.

### Person A

| Step | Action | Output |
|------|--------|--------|
| 1 | Create ElevenLabs account at elevenlabs.io | Account active |
| 2 | Claim hackathon ElevenLabs Creator code (from ElevenHacks page) | 1 month Creator plan |
| 3 | Create Twilio account at twilio.com | Account active |
| 4 | Buy a US phone number in Twilio (~$1.15/mo) | Phone number noted |
| 5 | Note Twilio Account SID + Auth Token from console | Credentials noted |

### Person B

| Step | Action | Output |
|------|--------|--------|
| 1 | Create Firecrawl account at firecrawl.dev | Account active |
| 2 | Claim hackathon Firecrawl credits (10K, from ElevenHacks page) | Credits applied |
| 3 | Create Railway account at railway.app | Account active |
| 4 | Create Vercel account at vercel.com | Account active |
| 5 | Check domain availability (howscrewed.ai, howscrewed.com, etc.) | Domain decision |

### Together

| Step | Action | Output |
|------|--------|--------|
| 1 | Create `.env.example` in repo with all key names | Committed to repo |
| 2 | Each create local `.env` with real values (never committed) | Local files only |
| 3 | Verify `.gitignore` includes `.env` | Confirmed |

**`.env.example` contents:**
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

## Phase 1: Parallel Build (Split, 2-4 hours)

**This is the core build phase.** Person A and Person B work independently on non-overlapping areas. Each runs their own Claude Code session(s).

### Person A: Agent Architect

**Focus:** ElevenLabs dashboard configuration + system prompt authoring
**Tools:** Browser (ElevenLabs dashboard) + 1 Claude Code terminal

#### Terminal 1: Claude Code Session (Prompt Drafting)

Use Claude Code to draft, iterate, and refine all system prompts and tool schemas. These get copy-pasted into the ElevenLabs dashboard.

```
Prompt Claude Code with:
"I'm building the How Screwed Am I project. Reference
docs/plans/2026-03-19-howscrewed-design.md section 3.1.
Help me write production-quality system prompts for each
subagent phase and the outbound caller agent. Also generate
the webhook tool API schemas in ElevenLabs format."
```

**Deliverables from this terminal:**
- Czara Intake subagent prompt
- Czara Research subagent prompt
- Czara Verdict subagent prompt
- Czara Action subagent prompt
- Czara Report Back subagent prompt
- Outbound Caller agent prompt
- Webhook tool schemas (JSON) for: `firecrawl_extract`, `firecrawl_multi_search`, `trigger_outbound_call`
- Dynamic variable definitions

#### Browser: ElevenLabs Dashboard (Agent Configuration)

Work through this checklist in order. Paste prompts from Terminal 1 as you go.

**Step 1: Create Czara Agent**
- [ ] Go to Agents → Create New Agent
- [ ] Name: "Czara"
- [ ] Select LLM: Claude Sonnet 4 (or GPT-4o)
- [ ] Select Voice: Browse voices, pick warm/feminine/practical tone
- [ ] Test voice with sample lines: "Hey, I'm Czara. So... how screwed are you?" and "Under Civil Code Section 1950.5, you may be entitled to up to twice the deposit amount."
- [ ] Set first message: "Hey, I'm Czara. So... how screwed are you?"
- [ ] Paste system prompt from Terminal 1 (start with Intake prompt for initial testing)

**Step 2: Connect Firecrawl MCP Server**
- [ ] Go to Agent → Tools → MCP Servers
- [ ] Add Custom MCP Server
- [ ] Name: "Firecrawl Search"
- [ ] Description: "Search the web and get structured content for any query"
- [ ] Server URL: `https://mcp.firecrawl.dev/{YOUR_FIRECRAWL_API_KEY}/v2/mcp`
- [ ] Click Add Integration
- [ ] Verify search tools appear in the tool list
- [ ] Test: Ask Czara something that requires a web search

**Step 3: Import Twilio Phone Number**
- [ ] Go to Phone Numbers tab
- [ ] Click Import → Twilio
- [ ] Enter: Label ("How Screwed"), Phone Number, Twilio SID, Twilio Auth Token
- [ ] Assign Czara agent to the phone number
- [ ] Test: Call the phone number from your real phone
- [ ] Verify Czara answers and you can have a conversation
- [ ] Note the `agent_phone_number_id` for the .env file

**Step 4: Build Agent Workflow**
- [ ] Go to Agent → Workflows
- [ ] Create workflow with 5 subagent nodes + edges:
  ```
  [Start] → [Intake] → [Research] → [Verdict] → [Action] → [Report Back] → [End]
                                        ↓
                                    [End: user declines]
  ```
- [ ] Configure each subagent node with its prompt from Terminal 1
- [ ] Add dispatch tool nodes for Firecrawl Search between Intake → Research
- [ ] Configure routing: intent-based edges from Intake to Research (when enough details gathered)
- [ ] Configure routing: conditional edge from Verdict (user says "yes" → Action, "no" → End)

**Step 5: Create Outbound Caller Agent**
- [ ] Create new agent: "Outbound Caller"
- [ ] Select LLM: Same as Czara
- [ ] Select Voice: Professional, firm, confident (noticeably different from Czara)
- [ ] Paste outbound system prompt from Terminal 1
- [ ] Note the `OUTBOUND_AGENT_ID`

**Step 6: Configure Agent Transfer**
- [ ] On Czara agent → Tools → System Tools
- [ ] Enable `transfer_to_agent`
- [ ] Add transfer rule:
  - Target: Outbound Caller agent
  - Condition: "When the user confirms they want you to make a call on their behalf"
  - Transfer message: "Alright, I'm connecting you now..."
  - Enable transferred agent first message: Yes

**Step 7: Add Webhook Tools** (after Person B deploys backend)
- [ ] Add webhook tool: `firecrawl_extract`
  - URL: `{BACKEND_URL}/api/firecrawl-extract`
  - Method: POST
  - Request body schema from Terminal 1
- [ ] Add webhook tool: `firecrawl_multi_search`
  - URL: `{BACKEND_URL}/api/firecrawl-multi-search`
  - Method: POST
  - Request body schema from Terminal 1
- [ ] Add webhook tool: `trigger_outbound_call`
  - URL: `{BACKEND_URL}/api/trigger-outbound-call`
  - Method: POST
  - Request body schema from Terminal 1

**Step 7 is blocked on Person B's backend deployment URL.** Do steps 1-6 first, step 7 when URL is available.

---

### Person B: Code Builder

**Focus:** Backend server + landing page + deployment
**Tools:** Claude Code with Agent Teams (2 teammates in worktrees)

#### Terminal 1: Claude Code Team Lead

Launch an Agent Team to build backend and landing page in parallel.

```
Prompt:
"Create an agent team to build the 'How Screwed Am I?' project.
Read docs/plans/2026-03-19-howscrewed-design.md for full specs.

Spawn 2 teammates:

TEAMMATE 1 — Backend:
Build a Python/FastAPI backend in server/ directory.
See design doc section 3.3 for all endpoint specs.
Endpoints needed:
  POST /api/firecrawl-extract — wraps Firecrawl Extract API
  POST /api/firecrawl-multi-search — runs parallel Firecrawl searches
  POST /api/trigger-outbound-call — calls ElevenLabs outbound API
  POST /api/call-complete — webhook for outbound call results
  GET /api/health — health check
Include: requirements.txt, .env loading via python-dotenv,
CORS middleware (allow all origins for hackathon), Procfile for Railway.
Use async endpoints with httpx for external API calls.

TEAMMATE 2 — Landing Page:
Build a landing page in landing/ directory.
See design doc section 3.6 for layout specs.
Single index.html using Tailwind CSS via CDN.
Include:
  - Hero: 'How Screwed Am I?' title, tagline, phone number CTA, 'Try Now' button
  - ElevenLabs widget: <elevenlabs-convai agent-id='AGENT_ID_PLACEHOLDER'>
  - 'How it works' 3-step section
  - 3 scenario cards (mechanic $1,160, landlord $2,400, salary $21K+)
  - Footer with ElevenLabs + Firecrawl credits, #ElevenHacks
  - Responsive, mobile-first
  - vercel.json for deployment
  - Keep agent-id as placeholder — Person A provides the real ID later
"
```

**Monitor the team:**
- Use `Shift+Down` to cycle between teammates
- Use `Ctrl+T` to view the shared task list
- Review code as teammates complete tasks
- Merge both teammate branches when complete

#### Terminal 2: Deployment (after Team Lead reports done)

```bash
# Deploy backend to Railway
cd server/
railway login
railway init
railway up
# Note the deployed URL: https://xxx.up.railway.app

# Deploy landing page to Vercel
cd ../landing/
vercel --prod
# Note the deployed URL

# Share both URLs with Person A immediately
```

#### Terminal 3 (optional): Pre-generate Sound Effects

```
Prompt Claude Code:
"Write a Python script that uses the ElevenLabs Sound Effects API
to generate and save these audio files to server/static/sounds/:
1. 'cash register cha-ching sound' → money_saved.mp3
2. 'dramatic orchestral sting bad news reveal' → bad_news.mp3
3. 'short triumphant victory fanfare' → victory.mp3
4. 'subtle keyboard typing research sounds' → researching.mp3
Use the ElevenLabs SDK text_to_sound_effects.convert() method."
```

---

### Phase 1 Sync Points

These are moments where Person A and Person B must exchange information:

| When | From | To | What |
|------|------|----|------|
| Backend deployed | B | A | Backend URL for webhook tools (Step 7) |
| Czara agent created | A | B | `CZARA_AGENT_ID` for .env |
| Outbound agent created | A | B | `OUTBOUND_AGENT_ID` for .env |
| Phone number imported | A | B | `AGENT_PHONE_NUMBER_ID` for .env |
| Landing page deployed | B | A | Landing URL to verify widget works |
| Agent ID for widget | A | B | Real agent ID to replace placeholder in landing page |

**Communication method:** Slack/Discord DM, or just shout across the room. Update `.env` on both machines as values become available.

---

## Phase 2: Integration & Wiring (Together, 1-2 hours)

Both developers work side-by-side, each in their own Claude Code terminal, on the main branch.

### Goal
Everything connected end-to-end. A phone call to the Twilio number triggers the full flow: Czara answers → researches via Firecrawl → delivers verdict → offers to call → triggers outbound call → reports back.

### Person A: Test Caller + Agent Tuner

```
Actions:
1. Call Twilio number from real phone
2. Test mechanic scenario end-to-end
3. Test landlord scenario end-to-end
4. Test salary scenario end-to-end
5. Note every issue: wrong routing, bad search queries,
   awkward phrasing, failed tool calls, transfer issues
6. Fix issues in ElevenLabs dashboard in real-time
   (adjust prompts, workflow edges, tool configs)
7. Test web widget on landing page
```

### Person B: Backend Monitor + Code Fixer

```
Terminal 1 (Claude Code):
- Watch Railway logs: railway logs --follow
- Fix any backend errors (500s, timeouts, malformed requests)
- Adjust Firecrawl search query construction if results are poor
- Fix CORS issues if widget can't connect
- Ensure outbound call trigger works

Terminal 2 (Claude Code):
- Update landing page with real agent ID
- Fix any styling issues
- Re-deploy as needed: vercel --prod
```

### Integration Checklist

- [ ] Inbound phone call → Czara answers with correct greeting
- [ ] Czara asks clarifying questions (Intake phase works)
- [ ] Czara triggers Firecrawl search (MCP tool works)
- [ ] Czara triggers Firecrawl extract (webhook tool works)
- [ ] Czara delivers specific verdict with real data
- [ ] Czara offers to take action
- [ ] User says yes → outbound call triggers
- [ ] Outbound agent calls target number with correct context
- [ ] Outbound agent has research data in its prompt
- [ ] Outbound agent voice is noticeably different from Czara
- [ ] Call recording works (if configured)
- [ ] Web widget on landing page works
- [ ] Widget uses Czara voice and correct agent
- [ ] Landing page loads fast, looks good on mobile

---

## Phase 3: Prompt Engineering & Polish (Together, 2-3 hours)

**This phase determines whether you win.** The tech stack is table stakes. What separates winners is how natural and impressive the conversation feels.

### Method: One Tests, One Tunes (Swap Every 30 min)

```
TESTER (calling Czara repeatedly):        TUNER (adjusting in dashboard + code):
────────────────────────────────────       ──────────────────────────────────────
Call with mechanic scenario                Refine Research subagent prompt
  - Does she ask the right questions?        - Better Firecrawl query construction
  - Are search results relevant?             - More specific search operators
  - Is the verdict specific enough?          - Add site: targeting
  - Does outbound call feel natural?

Call with landlord scenario                Refine Verdict subagent prompt
  - Does she cite exact statute?             - More specific number delivery
  - Is the tone right (firm but not scary)?  - Better pause timing
  - Does the landlord call sound real?       - Tone adjustment

Call with salary scenario                  Refine Intake subagent prompt
  - Does she ask the right details?          - Better question sequencing
  - Are salary sources accurate?             - Smoother transitions
  - Is the emotional pause right?

Call with random edge cases:               General polish:
  - "My gym won't let me cancel"             - Adjust workflow routing edges
  - "I got a parking ticket"                 - Add fallback responses
  - "My flight was cancelled"                - Tune voice speed/stability
  - "Is my landlord allowed to enter          - Test sound effect timing
     without notice?"
  - Gibberish / hostile input
  - Caller hangs up mid-conversation
```

### Quality Bar Checklist

Before moving to video, Czara must:
- [ ] Sound natural and conversational (not robotic or scripted)
- [ ] Ask 2-3 clarifying questions before researching (not just one)
- [ ] Make at least 3 distinct Firecrawl searches per scenario
- [ ] Cite specific numbers: statute codes, dollar amounts, deadlines
- [ ] Handle gracefully when Firecrawl returns poor results
- [ ] Transition smoothly between workflow phases (no awkward pauses)
- [ ] Outbound agent sounds professional and different from Czara
- [ ] Outbound agent uses research data as leverage in the call
- [ ] Handle "no thanks" gracefully with a helpful summary
- [ ] Handle unexpected scenarios with reasonable research + advice

---

## Phase 4: Video Production (Together, 4-6 hours)

Per hackathon guidelines: *"Spend at least half your time making it great."*

### Pre-Production (30 min)

```
Together:
- [ ] Finalize which 2-3 scenarios to film (recommend: mechanic, landlord, salary)
- [ ] Scout locations: auto shop parking lot, apartment, desk/office
- [ ] Assign roles: who is on camera for each scene?
- [ ] Prep phone: charge fully, clear notifications, enable Do Not Disturb
- [ ] Test call to Czara in each location (verify audio quality)
- [ ] Write loose script bullets (NOT a word-for-word script)
```

### Filming (2-3 hours)

Reference design doc section 7 for the second-by-second video script.

```
Person A (on camera):                     Person B (directing + filming):
─────────────────────                     ──────────────────────────────
SCENE 1 — MECHANIC (auto shop lot)        Film on iPhone 4K, handheld
- Hold repair estimate to camera          Capture: person, phone screen, reaction
- Call Czara on speakerphone              Film 2-3 takes, pick the best
- React naturally to the verdict          Get a closeup of phone showing call

SCENE 2 — LANDLORD (apartment)            Film in natural apartment lighting
- Look frustrated, mention deposit        Get the reaction shot when Czara
- Call Czara                                delivers the statute citation
- React to outbound call happening        Film phone showing outbound call
- Show Venmo notification (staged)        Closeup of Venmo notification

SCENE 3 — SALARY (desk)                   Film the silence after the number
- Sit at desk, explain situation          This is the emotional climax
- Call Czara                              Hold on the face, don't cut away
- The silence when underpayment revealed

BONUS — HBO JOKE (quick, anywhere)        Quick handheld, casual energy
- "Used my roommate's HBO for 3 years"
- Czara's funny response
```

### Post-Production (2-3 hours)

```
Person A — Master Edit:                   Person B — Platform Variants:
────────────────────────                  ─────────────────────────────
Open CapCut desktop                       Export footage to CapCut mobile
Import all footage + audio                Create TikTok cut (9:16, 45-60s)
                                          Create Instagram Reel (9:16, 45-60s)

Master video (90s, 16:9 or 9:16):
- [0-3s] Hook text + Czara voice
- [3-5s] Title card
- [5-25s] Mechanic scene
- [25-45s] Landlord scene
- [45-65s] Salary scene
- [65-75s] HBO bonus
- [75-85s] Running total animation
- [85-90s] CTA + credits

Both:
- Add auto-captions (CapCut → Text → Auto captions)
- Style: bold white, black background, large font
- Color dollar amounts: green for saved, red for lost
- Add subtle background music (CapCut royalty-free library, 15-20% volume)
- Add "cha-ching" sound on money saved reveals
- Add speaker labels: "Czara:", "Mechanic:", "Landlord:"

Export:
- Master: 1080p minimum, 90 seconds
- X/Twitter: Landlord scene standalone, 30-45s
- TikTok: Hook + mechanic + landlord + total, 45-60s vertical
- Instagram: Same as TikTok
- LinkedIn: Full 90s video (pair with text post)
```

---

## Phase 5: Social Posts & Submission (Together, 1 hour)

### Social Posts (+50 pts each = 200 pts possible)

**X/Twitter** (Person A posts):
```
Tweet text:
"I built an AI that calls your landlord and cites the exact law they're breaking.

It got someone's $2,400 deposit back.

Built with @elevenlabs + @firecrawl for #ElevenHacks

Call Czara: [phone number]"

Attach: 30-45s landlord clip (native upload, not a link)
```

**LinkedIn** (Person A posts):
```
Post text:
"This weekend I built something that saves people real money.

It's called 'How Screwed Am I?' — you call an AI named Czara,
tell her your situation, and she researches it in real-time
using live web data. Then she makes phone calls on your behalf.

The mechanic scene: saved $1,160.
The landlord scene: recovered $2,400.
The salary scene: identified $21K+ underpayment.

Built with @ElevenLabs conversational AI and @Firecrawl
for the #ElevenHacks hackathon.

Try it: [phone number] or [website URL]"

Attach: Full 90s video (native upload)
```

**TikTok** (Person B posts):
```
Caption: "POV: You let an AI call your landlord #ElevenHacks #AI #LifeHack #MoneySaving #Landlord #TenantRights"
Attach: 45-60s vertical cut
```

**Instagram** (Person B posts):
```
Caption: "This AI called my landlord and cited the exact statute they violated. Got $2,400 back. Link in bio. #ElevenHacks #AI #LifeHack #MoneySaving"
Attach: 45-60s vertical Reel
Cover image: Frame showing $2,400 RECOVERED text overlay
```

### Submission Form

```
Together, fill out on hacks.elevenlabs.io:

Description:
"How Screwed Am I? is an AI voice agent named Czara that you call
to assess any situation where you're being taken advantage of.
Czara researches your exact situation in real-time using Firecrawl
Search — fair prices, applicable laws, salary benchmarks — then
makes outbound phone calls on your behalf to fix it.

Built with ElevenLabs Conversational AI (Agent Workflows, dual
voices, outbound calling, sound effects, web widget) and Firecrawl
(Search API via native MCP, Extract API for structured data,
multi-search for comprehensive research).

In our demo: Czara saved $1,160 at a mechanic, recovered a $2,400
security deposit by calling a landlord and citing the exact statute,
and identified $21,000+ in salary underpayment."

Cover image: Best frame from video (dollar amount visible)
Repo URL: https://github.com/[your-org]/howscrewed
Demo URL: [landing page URL]
Social links: [paste all 4 post URLs]
```

### Final Verification

- [ ] Call Twilio number — Czara answers and works
- [ ] Visit landing page — widget works, looks good
- [ ] All 4 social posts are live and tagged correctly
- [ ] Submission form filled completely
- [ ] Video plays correctly in submission
- [ ] Repo has clean README with architecture overview

---

## Quick Reference: Who Owns What

| Area | Owner | Claude Code Mode |
|------|-------|-----------------|
| ElevenLabs dashboard config | Person A | Single session (prompt drafting) |
| Agent Workflows (visual builder) | Person A | N/A (browser work) |
| System prompts (authoring) | Person A | Single session |
| Voice selection & testing | Person A | N/A (browser + phone) |
| Twilio number setup | Person A | N/A (browser) |
| FastAPI backend code | Person B | Agent Teams (Teammate 1) |
| Landing page HTML | Person B | Agent Teams (Teammate 2) |
| Railway deployment | Person B | Terminal (railway CLI) |
| Vercel deployment | Person B | Terminal (vercel CLI) |
| Sound effect generation | Person B | Single session |
| Integration testing | Both | Parallel sessions (co-work style) |
| Prompt engineering | Both | Person A: phone tester, Person B: dashboard tuner |
| Video filming | Both | N/A (phones + locations) |
| Video editing | Split | Person A: master edit, Person B: platform variants |
| Social posts | Split | Person A: X + LinkedIn, Person B: TikTok + Instagram |
| Submission form | Both | N/A (browser) |

---

## Key Technical Simplification: Native Twilio

ElevenLabs' native Twilio integration handles all telephony through the dashboard:
- **No backend code** for inbound call routing
- **No webhook setup** for connecting calls to agents
- **No TwiML** or Twilio SDK needed
- **Outbound calls** can be triggered via ElevenLabs API directly (one HTTP POST)

The backend only exists for Firecrawl Extract/Multi-Search wrappers and as a webhook target for outbound call completion notifications. This is ~150-200 lines of Python.

---

## Critical Path & Dependencies

```
                    ┌─────────────┐
                    │ Phase 0:    │
                    │ All accounts│
                    │ + API keys  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐
    │ Person A:       │      │ Person B:        │
    │ Create agents   │      │ Build backend    │
    │ Build workflow   │      │ Build landing    │
    │ Connect MCP     │      │ Deploy both      │
    │ Import Twilio # │      │                  │
    └────────┬────────┘      └────────┬─────────┘
             │                        │
             │   ◄── exchange IDs ──► │
             │   ◄── exchange URLs ──►│
             │                        │
             ▼                        ▼
    ┌─────────────────┐      ┌─────────────────┐
    │ Person A:       │      │ Person B:        │
    │ Wire webhooks   │      │ Update .env      │
    │ to backend URLs │      │ with agent IDs   │
    └────────┬────────┘      └────────┬─────────┘
             │                        │
             └────────────┬───────────┘
                          ▼
                ┌─────────────────┐
                │ Phase 2:        │
                │ Integration     │
                │ test together   │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ Phase 3:        │
                │ Prompt eng      │
                │ + polish        │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ Phase 4:        │
                │ Film + edit     │
                │ video           │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │ Phase 5:        │
                │ Post + submit   │
                └─────────────────┘
```

**Blocking dependency:** Person A cannot wire webhook tools (Step 7) until Person B provides the backend URL. Person B cannot set the real agent ID in the landing page until Person A creates the agent. Plan to exchange these as soon as they're available — don't wait until both are "done."

---

## If Things Go Wrong

| Problem | Fallback |
|---------|----------|
| Agent Workflows too complex to set up | Use a single agent with all prompts + tools. Simpler but still works. |
| Firecrawl MCP won't connect to ElevenLabs | Use webhook tools pointing to backend `/api/firecrawl-multi-search` instead |
| Outbound calling doesn't work | Film the outbound call as a separate pre-recorded demo clip, edit it into the video |
| Railway deploy fails | Use Render.com (same git-push deploy, free tier) |
| Vercel deploy fails | Host `index.html` on GitHub Pages or Netlify |
| Twilio number issues | Demo using the web widget only (still works for judges) |
| Voice sounds wrong | ElevenLabs has 5,000+ voices — spend 15 min browsing and testing alternatives |
| Agent Teams fails / experimental issues | Fall back to manual worktrees: `git worktree add ../backend feature/backend` and `git worktree add ../landing feature/landing`, run separate Claude Code sessions in each |
| Czara gives bad answers | Hardcode fallback data for the 3 demo scenarios in the system prompt as examples |
