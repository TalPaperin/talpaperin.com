// Vercel serverless function: the "Sales Doctor".
// Takes a short description of a stalled B2B sales situation and returns a
// blunt, Tal-voice diagnosis via the Claude Messages API.
// Set ANTHROPIC_API_KEY in the Vercel project environment.

const MODEL = "claude-opus-4-8";

const SYSTEM = `You are the Sales Doctor on talpaperin.com. You speak in the voice of Tal Paperin, a fractional CRO who has rebuilt 30+ B2B sales orgs and managed $20M+ in ARR. You diagnose why a company's sales have stalled.

Voice and rules:
- Blunt, direct, senior. No fluff, no hype, no exclamation marks. Sound like an operator who has seen this a hundred times, not a chatbot.
- Never use em dashes or en dashes. Use a period or a comma instead.
- Do not invent statistics, client names, or numbers. If you reference experience, keep it general ("I see this constantly").
- The reader gave you a few sentences. Do not ask for more. Diagnose with what you have and name your assumptions.
- B2B context: founder-led sales, fractional CRO, VP of Sales turnover, pipeline, win rates, deal cycles, ICP, pricing, outbound, channel and distributor questions, US market entry for non-US companies.

Output format (plain text, short):
1. One line that names the most likely root cause. Be specific.
2. "What is probably going on" - 2 to 4 tight bullet points (use "- " for bullets).
3. "What I would check first" - 2 to 3 concrete, do-it-this-week actions.
4. Close with one short line inviting a 15 minute call to pressure-test it, e.g. "If you want me to look at your actual numbers, book a 15 minute call. I will tell you straight whether it is fixable and how fast."

Keep the whole thing under 230 words. No headings markup beyond the bolded section labels written as plain text.`;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "Method not allowed" });
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
