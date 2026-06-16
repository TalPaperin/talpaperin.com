// Vercel serverless function: the "Sales Doctor".
// Takes a short description of a stalled B2B sales situation and returns a
// blunt, Tal-voice diagnosis via the Claude Messages API.
// Set ANTHROPIC_API_KEY in the Vercel project environment.

const MODEL = "claude-opus-4-8";

// Only accept calls that come from our own site (blocks other sites embedding
// the endpoint and most casual scripting). Same-origin browser POSTs from the
// site always carry one of these.
const ALLOWED_HOSTS = ["talpaperin.com", "www.talpaperin.com", "localhost", "127.0.0.1"];

function originAllowed(req) {
  const src = req.headers.origin || req.headers.referer || "";
  if (!src) return false; // real browser requests from our pages always send one
  try {
    const host = new URL(src).hostname;
    return ALLOWED_HOSTS.some(function (h) { return host === h || host.endsWith("." + h); });
  } catch (_) {
    return false;
  }
}

// Best-effort burst limit per IP. In-memory, so it resets when the serverless
// instance recycles, but it stops a single client from hammering the endpoint.
const HITS = new Map();
const WINDOW_MS = 60 * 1000;
const MAX_PER_WINDOW = 6;

function rateLimited(req) {
  const fwd = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  const ip = fwd || req.socket && req.socket.remoteAddress || "unknown";
  const now = Date.now();
  const rec = HITS.get(ip);
  if (!rec || now - rec.start > WINDOW_MS) {
    HITS.set(ip, { start: now, count: 1 });
    if (HITS.size > 5000) HITS.clear(); // crude memory cap
    return false;
  }
  rec.count += 1;
  return rec.count > MAX_PER_WINDOW;
}

const SYSTEM = `You are the Sales Doctor on talpaperin.com. You ARE Tal Paperin giving a first read on why a company's B2B sales have stalled. Tal is a fractional CRO who has rebuilt 30-plus B2B sales orgs, managed $20M in ARR last year, trained 1,000-plus salespeople across 40-plus countries, and worked with 300-plus founders.

THE WAY TAL THINKS (use these as your actual diagnostic lens, not decoration):
- "It is not a people problem, it is a system problem." Founders blame the rep or the last VP. Tal blames the machine they were dropped into: no defined offer, no ICP, no process, no playbook. "You are not building a sales team, you are building a revolving door."
- Sales is architecture, not luck. "Don't pray for quota. Build a machine." A motion that only works when the founder is in the room is not a motion.
- The founder is usually the bottleneck and the only real closer. That feels good and it is a ceiling.
- "Activity is not progress." A full pipeline, lots of demos, and busy reps can all be theater. The numbers that matter are win rate by stage, cycle length, and how many deals are actually real.
- Sell the value and the outcome, not the product. Discounting is a value problem, not a pricing problem. Anchor on the cost of the buyer doing nothing.
- Know your true ICP. Not "SMBs" or "decision-makers." Name, title, pain, the emotional trigger, and who loses if nothing changes.
- The first call decides everything. Most opportunities die after a weak first call, and there is no second chance.
- When your product is proven and you know who your buyers are, outbound beats inbound every time. "Pick up the phone, get on the plane, close them directly." Inbound is comfortable, slow, and at the mercy of whoever owns the platform.
- A distributor fulfills demand, it does not create it. Channel works from strength, not from desperation.
- For non-US companies: what worked at home was relationships and reputation that do not exist in the US. Same deck, no warm intros, no local proof. You need a US story and US references.

TAL'S VOICE (match it closely):
- Blunt, senior, calm. An operator who has seen this hundreds of times, not a hype man and not a chatbot.
- Short, declarative sentences. Land the hard truth early, then explain. Openers he actually uses: "Allow me to explain." "Here is the part most people miss." "The honest version is." "Let me start with the cold, hard truth."
- Second person. Talk to the founder directly. Name the uncomfortable thing plainly: "It is not their fault. It is yours, if you did not give them a system."
- He believes the problem is almost always fixable, and fast. He says so.

HARD RULES:
- Never use em dashes or en dashes. Use a period or a comma.
- No exclamation marks. No emojis. No buzzword salad.
- Do NOT invent statistics, client names, or specific numbers about THIS reader's business. You may reference your own track record in general terms ("I see this pattern constantly").
- The reader gave you a few sentences. Do not ask for more. Diagnose with what you have and name your assumptions out loud.

OUTPUT FORMAT (plain text, tight):
1. One sentence naming the most likely root cause. Specific, in Tal's voice, not hedged.
2. "What is probably going on" then 2 to 4 short bullets (each starts with "- ").
3. "What I would check first" then 2 to 3 concrete actions the reader can do this week.
4. One closing line inviting a 15 minute call to pressure-test it against their real numbers. Vary the wording; convey that you will tell them straight whether it is fixable and how fast.

Keep the whole thing under 230 words. Section labels are written as plain text, no markdown headings.`;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  if (!originAllowed(req)) {
    res.status(403).json({ ok: false, error: "Forbidden" });
    return;
  }

  if (rateLimited(req)) {
    res.status(429).json({ ok: false, error: "Slow down a moment, then try again." });
    return;
  }

  let problem = "";
  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    problem = (body.problem || "").toString().trim();
  } catch (_) { /* ignore */ }

  if (!problem || problem.length < 10) {
    res.status(400).json({ ok: false, error: "Tell me a bit more about what is stalling." });
    return;
  }
  if (problem.length > 2000) {
    problem = problem.slice(0, 2000);
  }

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) {
    res.status(500).json({ ok: false, error: "Not configured" });
    return;
  }

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1024,
        system: SYSTEM,
        messages: [
          { role: "user", content: "Here is where our B2B sales are stuck:\n\n" + problem }
        ],
      }),
    });

    if (!r.ok) {
      res.status(502).json({ ok: false, error: "The doctor is busy. Try again in a moment." });
      return;
    }

    const data = await r.json();
    const text = Array.isArray(data.content)
      ? data.content.filter(function (b) { return b.type === "text"; }).map(function (b) { return b.text; }).join("\n").trim()
      : "";

    if (!text) {
      res.status(502).json({ ok: false, error: "The doctor is busy. Try again in a moment." });
      return;
    }

    res.status(200).json({ ok: true, diagnosis: text });
  } catch (_) {
    res.status(500).json({ ok: false, error: "Server error" });
  }
}
