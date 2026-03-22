# Landing Page Redesign — Design Document

**Date:** 2026-03-22
**Approach:** "Call Czara" (Character-driven) + Money Counter from "The Money Shot"
**Tech:** HTML + Tailwind CSS (CDN) + vanilla JS + CSS animations. Zero external dependencies.
**Deploy:** Vercel static site

---

## Design Principles

1. **Czara's voice IS the page** — all copy written as if Czara is talking to you
2. **Widget is king** — judges will try it, so it must be prominent and immediate
3. **Results sell** — the $24,560 animated counter is the scroll-stopping moment
4. **Bold, not gimmicky** — big type, strong personality, clean layout
5. **Screenshot-worthy** — every section should look good as a screenshot on X/LinkedIn

---

## Page Structure

### Section 1: Hero (100vh)

- Small pill badge: "Built for #ElevenHacks" (brand red border, subtle)
- **"How Screwed Am I?"** — 80-100px desktop, 48-56px mobile. Font-black (900). "How Screwed" white, "Am I?" red gradient.
- Subtext in Czara's voice: "Call me. I'll research your situation, tell you exactly how screwed you are, then make calls on your behalf to fix it. — Czara"
- Two CTAs:
  - Primary (red, pulsing ring): "Talk to Czara" → scrolls to widget
  - Secondary (dark card, outlined): "Call Instead: (XXX) XXX-XXXX" → tel: link
- Muted line below: "No app. No signup. Just talk."
- Subtle red radial gradient glow behind title for depth
- Fade-in + slide-up animation on load

### Section 2: How It Works (3 steps)

- Section title: "Here's what happens when you call"
- 3 columns, each with:
  - Step number in red circle
  - Bold title
  - One-line description in Czara's voice
- Steps:
  1. "You tell me what happened" — "Mechanic rip-off, landlord screwing you, underpaid — whatever it is."
  2. "I research it live" — "Fair prices, laws, salary data, competitor quotes. Real-time, specific to your situation."
  3. "I call them for you" — "I'll call the mechanic, the landlord, whoever — using what I found as leverage."
- Scroll-triggered fade-in animation (IntersectionObserver)

### Section 3: Results / Money Counter

- Section title: "What happened last time someone called"
- Three scenario cards — styled as conversational stories, not feature cards:
  - **Mechanic:** "Some guy's mechanic wanted $1,800 for brakes on his Camry. Fair price? $640. I called three other shops and got him quotes. Saved $1,160."
  - **Landlord:** "Her landlord ghosted on a $2,400 security deposit for 35 days. I called and cited Civil Code 1950.5. They're mailing the check. Recovered $2,400."
  - **Salary:** "He was making $71K as a marketing manager. Market rate? $92K-$112K. I pulled Glassdoor, Levels.fyi, and 4 open roles paying more. Gap identified: $21,000+."
- Each card: dark card bg, left red accent border, emoji icon, story text, big green money number at bottom
- Below cards: knockout stat banner
  - **"$24,560"** — animated counter that ticks up when scrolled into view
  - Subtitle: "saved across 3 phone calls"
  - Subtle green glow behind the number

### Section 4: Try It Now (Widget)

- id="widget-section" for scroll target
- Section title: "Talk to Czara right now"
- Subtitle: "Click the button below. No download, no signup."
- ElevenLabs widget: `<elevenlabs-convai agent-id="AGENT_ID_PLACEHOLDER">`
- Below widget: "Or call directly: (XXX) XXX-XXXX"
- This section gets a slightly different background — very subtle gradient or a faint border-top glow to set it apart as the "destination"

### Section 5: Footer

- "Built with ElevenLabs Conversational AI + Firecrawl Search API"
- Tech feature tags (subtle): Agent Workflows · Dual Voices · Outbound Calling · MCP Integration · Structured Data Extraction
- Links: GitHub · #ElevenHacks
- Keep minimal

---

## Technical Details

### Animations (all vanilla)

1. **Hero entrance:** CSS @keyframes fade-in + translateY. Title, subtitle, CTAs staggered by 0.15s each.
2. **Scroll reveals:** IntersectionObserver triggers `.visible` class on sections. CSS transition: opacity 0→1, translateY 20px→0, over 0.5s.
3. **Money counter:** IntersectionObserver triggers JS counter that increments from $0 to $24,560 over ~2 seconds. Uses requestAnimationFrame for smoothness. Easing function for deceleration at end.
4. **Card hover:** translateY(-4px) + subtle red box-shadow. CSS transition only.
5. **Pulse ring on CTA:** CSS @keyframes, already exists in current code.

### Typography

- Font: Inter (already loaded via Google Fonts)
- Hero title: 900 weight, 5rem (80px) desktop, 3rem (48px) mobile
- Section titles: 700 weight, 2rem
- Body: 400 weight, 1rem
- Scenario stories: 400 weight, 0.9375rem, gray-400

### Colors (unchanged from current)

- Background: #0A0A0A
- Card: #141414
- Border: #2A2A2A
- Brand red: #FF3B30, dark variant #CC2F26
- Money green: #34C759
- Text: white, gray-400, gray-600

### File Structure

```
landing/
├── index.html      ← Main page (HTML + inline Tailwind classes)
├── styles.css       ← Custom CSS (animations, gradients, counter styles)
├── main.js          ← Vanilla JS (IntersectionObserver, counter, scroll)
└── vercel.json      ← Deploy config (unchanged)
```

### Responsive Breakpoints

- Mobile-first: single column, smaller title (3rem), stacked CTAs
- sm (640px): side-by-side CTAs, 3-col grids
- lg (1024px): max title size, wider content area

---

## Copy (Final)

All copy written in Czara's voice — direct, warm, slightly cocky, never corporate.

### Hero
- Badge: "Built for #ElevenHacks"
- Title: "How Screwed Am I?"
- Sub: "Call me. I'll research your situation, tell you exactly how screwed you are, then make calls on your behalf to fix it. — Czara"
- CTA1: "Talk to Czara"
- CTA2: "Call Instead"
- Micro: "No app. No signup. Just talk."

### How It Works
- Title: "Here's what happens when you call"
- Step 1: "You tell me what happened" / "Mechanic rip-off, landlord screwing you, underpaid — whatever it is."
- Step 2: "I research it live" / "Fair prices, laws, salary data, competitor quotes. Real-time, specific to your situation."
- Step 3: "I call them for you" / "I'll call the mechanic, the landlord, whoever — using what I found as leverage."

### Results
- Title: "What happened last time someone called"
- Cards: conversational stories (see Section 3 above)
- Counter: "$24,560" / "saved across 3 phone calls"

### Widget
- Title: "Talk to Czara right now"
- Sub: "Click the button below. No download, no signup."
- Fallback: "Or call directly: (XXX) XXX-XXXX"

### Footer
- "Built with ElevenLabs Conversational AI + Firecrawl Search API"
