"""
The one place the system talks to Claude.

- real mode: calls the Anthropic API with Peggy's key (ANTHROPIC_API_KEY).
- mock mode: returns correctly-shaped canned JSON per step, so the whole pipeline
  runs and produces a PDF with no key and no network.

Every agent step calls `ask_json(step_name, system_prompt, user_content, tier)`.
"""
import json, os, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import settings
from compass import mockdata


def _extract_json(text: str):
    """Pull the first JSON object out of a model reply, tolerating stray prose/fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text).rstrip("`").strip()
    # find the outermost {...}
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start:end + 1])


def ask_json(step: str, system_prompt: str, user_content: str, tier: str = "top") -> dict:
    if settings.LLM_MODE == "mock":
        return mockdata.for_step(step)

    # --- real Anthropic call ---
    import anthropic
    key = os.environ.get(settings.ANTHROPIC_API_KEY_ENV)
    if not key:
        raise RuntimeError(
            f"LLM_MODE=real but {settings.ANTHROPIC_API_KEY_ENV} is not set. "
            "Export Peggy's Anthropic API key, or run in mock mode."
        )
    client = anthropic.Anthropic(api_key=key)
    model = settings.MODEL_TOP if tier == "top" else settings.MODEL_MID
    last_err = None
    for attempt in range(settings.MAX_JSON_RETRIES + 1):
        msg = client.messages.create(
            model=model,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content
                       + ("\n\nReturn ONLY valid JSON." if attempt else "")}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        try:
            return _extract_json(text)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"[{step}] model did not return valid JSON: {last_err}")


# ===========================================================================
# LIVE RESEARCH  [feedback log #22]
# The catalog cannot cover everything — an unknown-interest gap, a new program,
# a changed price or deadline. PLAN_RECS used to be TOLD to "web-search and
# verify", but ask_json is a single-shot call with no tools, so that instruction
# could never execute. A model told to verify with no means of verifying
# produces something that merely reads as verified. This makes it real.
# ===========================================================================

RESEARCH_SYSTEM = """You are researching real, currently-available programs for ONE student task.

You have web search. Use it, then VERIFY before recommending anything:
- the organisation exists and the page resolves;
- the age or grade band actually includes this student — state the band and the fit explicitly;
- cost, dates and registration deadlines as published, or say plainly they are not posted;
- the location or format fits the stated constraints.

Recommend ONLY what you verified. If you cannot verify a candidate, do not include it.
If nothing verifiable is found, return escalate:true with what you tried — a placeholder or a
plausible-sounding invention is a failure, an honest escalation is not.
Never invent a phone number, price, date or URL. Every recommendation carries its source URL.

Return ONLY JSON:
{"recommendations":[{"name","org","what_it_is","ages","age_fit_ok","format","location",
"price","price_note","deadline","contact","url","verified":true,"choose_this_if"}],
"escalate":false,"notes":""}"""


def research_json(task_description, constraints, tier="mid", max_searches=5):
    """Live web research with mandatory verification. Falls back to an honest
    escalation when the session has no web access (e.g. mock mode)."""
    user = (f"TASK: {task_description}\n"
            f"CONSTRAINTS (hard): {json.dumps(constraints, indent=2)}\n"
            "Find and verify real options that fit these constraints.")

    if settings.LLM_MODE != "real":
        return {"recommendations": [], "escalate": True,
                "notes": "mock mode: no web access. Set LLM_MODE=real with an API key to research live."}

    try:
        import anthropic
        key = os.environ.get(settings.ANTHROPIC_API_KEY_ENV) or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return {"recommendations": [], "escalate": True,
                    "notes": "no ANTHROPIC_API_KEY set; cannot research live."}
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model=settings.MODELS.get(tier, settings.MODELS["mid"]),
            max_tokens=4000,
            system=RESEARCH_SYSTEM,
            tools=[{"type": "web_search_20250305", "name": "web_search",
                    "max_uses": max_searches}],
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return _extract_json(text)
    except Exception as e:                       # never let research break a run
        return {"recommendations": [], "escalate": True,
                "notes": f"research unavailable: {type(e).__name__}: {e}"}


FACT_SYSTEM = """You look up ONE specific fact that is not in our data, using web search, and you
verify it before returning it.

RULES
- Prefer the primary source: the institution's own admissions/newsroom page or its Common Data
  Set. A consolidator is acceptable only when it cites the class year.
- Always capture WHICH YEAR the figure refers to. A number without its year is unusable.
- If sources disagree, return the primary one and note the disagreement.
- If you cannot verify it, return found:false. An honest miss is correct; a guess is a failure
  that reaches a real family.

Return ONLY JSON:
{"found":true|false,"value":<number or string>,"unit":"","year":<int|null>,
 "source_url":"","source_name":"","confidence":"high|medium|low","notes":""}"""


def research_fact(question, tier="mid", max_searches=4):
    """Look up any single missing datum on the web, verified. Used when the corpus
    or a reference table has no entry — see feedback log #24/#25."""
    if settings.LLM_MODE != "real":
        return {"found": False, "notes": "mock mode: no web access."}
    try:
        import anthropic
        key = os.environ.get(settings.ANTHROPIC_API_KEY_ENV) or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return {"found": False, "notes": "no API key; cannot look up live."}
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model=settings.MODELS.get(tier, settings.MODELS["mid"]),
            max_tokens=1500, system=FACT_SYSTEM,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": max_searches}],
            messages=[{"role": "user", "content": question}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return _extract_json(text)
    except Exception as e:
        return {"found": False, "notes": f"lookup unavailable: {type(e).__name__}: {e}"}
