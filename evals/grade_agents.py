"""
PER-AGENT rubric grader — implements R1_profile_rubric v2 and GapAnalyst_rubric v1
as written: it grades each agent's INTERNAL OBJECT, scores 0-3 per check, rolls up to
one Fitness grade (A-F), gates on dossier completeness, and attaches a FIX LEVER.

This is deliberately separate from evals/grade.py, which grades the RENDERED PLAN —
that is R9's writing plus the modules, not R1's or the Gap Analyst's object.
Grading the wrong artifact sends you to fix the wrong prompt.

    python evals/grade_agents.py out/<run>.state.json
"""
import json, re, sys, os

STRONG, OKAY, WEAK, MISSING = 3, 2, 1, 0
LEVELS = {3: "Strong", 2: "Okay", 1: "Weak", 0: "Missing/Broken"}
# remediation levers, per the rubric docs
FIX_PROMPT, ASK_PARENT, CHANGE_INTAKE, CHANGE_SCHEMA, BAD_INPUT = (
    "FIX_PROMPT", "ASK_PARENT", "CHANGE_INTAKE", "CHANGE_SCHEMA", "BAD_INPUT")

def chk(name, score, why, fix=None, gate=False):
    return {"check": name, "score": score, "level": LEVELS[score],
            "why": why, "fix": fix if score < 3 else None, "gate": gate}

def _t(o):
    if isinstance(o, str): return o
    if isinstance(o, dict): return " ".join(_t(v) for v in o.values())
    if isinstance(o, list): return " ".join(_t(v) for v in o)
    return ""

# ==========================================================================
# R1 — PROFILE  (rubric v2: four checks, check 1 is the gate)
# ==========================================================================
def grade_r1(profile, intake):
    out = []

    # --- 1. Dossier completeness (THE GATE) -- about the intake form, not R1 ---
    it = _t(intake).lower()
    need = {"grade/year": r"grade|year", "activities": r"activit|pokemon|debate|chess",
            "budget": r"budget|\$", "location": r"location|regional|san jos",
            "free hours": r"hours?[ _]per[ _]week|hours_per_week|weekly",
            "hard-nos": r"hard_nos|hard nos|no out-of-region",
            "stated worry": r"worry|concern", "academics": r"gpa|transcript|test"}
    miss = [k for k, p in need.items() if not re.search(p, it)]
    s = STRONG if not miss else (OKAY if len(miss) <= 2 else WEAK if len(miss) <= 4 else MISSING)
    out.append(chk("1. Dossier completeness (GATE)", s,
                   "all basics present" if not miss else f"missing from intake: {miss}",
                   ASK_PARENT if miss else None, gate=True))

    # --- 2. Profile completeness: must-haves + per-activity signals ---
    has_spine = bool(profile.get("spine"))
    has_temp = bool(profile.get("temperament"))
    has_guard = bool(profile.get("constraints"))
    acts = profile.get("activities") or []
    SIG = ("tenure", "duration", "role", "level", "scale", "result", "verified")
    withsig = [a for a in acts if isinstance(a, dict) and sum(k in _t(a).lower() or k in a for k in SIG) >= 2]
    parts = sum([has_spine, has_temp, has_guard])
    if parts == 3 and acts and len(withsig) == len(acts): s = STRONG
    elif parts >= 2 and acts:                             s = OKAY
    elif parts >= 1:                                      s = WEAK
    else:                                                 s = MISSING
    out.append(chk("2. Profile completeness", s,
                   f"spine={has_spine} temperament={has_temp} guardrails={has_guard} "
                   f"activities={len(acts)} with-signals={len(withsig)}",
                   FIX_PROMPT if s < STRONG else None))

    # --- 3. Accuracy & no overclaiming ---
    spine = profile.get("spine") or {}
    has_quote = bool(spine.get("evidence_quote")) or bool(profile.get("evidence"))
    flags = profile.get("flags_to_confirm")
    over = re.findall(r"\b(successful entrepreneur|highly accomplished|exceptional|proven leader)\b",
                      _t(profile), re.I)
    nums = re.findall(r"\b\d{1,3}\s?%|\btier\b|\bodds\b", _t(profile), re.I)
    if has_quote and flags and not over and not nums: s = STRONG
    elif has_quote and not over:                      s = OKAY
    elif not over:                                    s = WEAK
    else:                                             s = MISSING
    out.append(chk("3. Accuracy & no overclaiming", s,
                   f"evidence quotes={has_quote} flags_to_confirm={bool(flags)} "
                   f"overclaims={over} numbers-in-object={nums}",
                   FIX_PROMPT if s < STRONG else None))

    # --- 4. Reading correctness (the real thinking) ---
    conf = (spine.get("confidence") or "").lower()
    pacing = [t for t in (profile.get("temperament") or [])
              if isinstance(t, dict) and t.get("pacing_implication")]
    tensions = profile.get("constraint_tensions")
    selfdrv = profile.get("self_driven_read") or profile.get("preference_vs_behaviour")
    have = sum([bool(conf), bool(pacing), bool(tensions), bool(selfdrv)])
    s = [MISSING, WEAK, WEAK, OKAY, STRONG][have]
    missing_bits = [n for n, v in [("confidence", conf), ("pacing_implication", pacing),
                                   ("constraint_tensions", tensions),
                                   ("self_driven_read", selfdrv)] if not v]
    out.append(chk("4. Reading correctness", s,
                   f"present: {4-len(missing_bits)}/4 · missing: {missing_bits}",
                   CHANGE_SCHEMA if missing_bits else None))
    return out

# ==========================================================================
# GAP ANALYST  (rubric v1: six checks)
# ==========================================================================
def grade_gap(gap, cards, profile):
    out = []
    gaps = gap.get("gaps") or []
    t = _t(gap)

    domains = {str(g.get("domain", "")).lower() for g in gaps if isinstance(g, dict)}
    s = STRONG if len(domains) >= 4 else OKAY if len(domains) >= 2 else WEAK if domains else MISSING
    out.append(chk("1. Coverage", s, f"domains covered: {sorted(domains)}",
                   FIX_PROMPT if s < STRONG else None))

    freq = [g for g in gaps if isinstance(g, dict) and g.get("frequency")]
    meta = gap.get("meta")
    s = STRONG if gaps and len(freq) == len(gaps) and meta else OKAY if freq else WEAK if gaps else MISSING
    out.append(chk("2. Accurate & grounded", s,
                   f"{len(freq)}/{len(gaps)} gaps cite a tally frequency · meta block={bool(meta)}",
                   FIX_PROMPT if s < STRONG else None))

    VALID = {"at-or-above", "missing", "lower-level", "unknown-interest"}
    cats = [str(g.get("category", "")).lower() for g in gaps if isinstance(g, dict)]
    good = [c for c in cats if c in VALID]
    s = STRONG if cats and len(good) == len(cats) else OKAY if good else MISSING
    out.append(chk("3. Correct categorization", s,
                   f"valid categories {len(good)}/{len(cats)} · seen: {sorted(set(cats))}",
                   FIX_PROMPT if s < STRONG else None))

    strengths = gap.get("strengths") or [g for g in gaps if isinstance(g, dict)
                                         and g.get("category") == "at-or-above"]
    small = [g for g in gaps if isinstance(g, dict) and
             (g.get("within_range") is not None or g.get("magnitude") is not None)]
    s = STRONG if strengths and small else OKAY if strengths or small else WEAK
    out.append(chk("4. Complete — small gaps & strengths", s,
                   f"strengths listed={len(strengths)} · gaps carrying magnitude/within_range={len(small)}",
                   FIX_PROMPT if s < STRONG else None))

    FIELDS = ("domain", "category", "kid_state", "admit_reference", "grade_context")
    full = [g for g in gaps if isinstance(g, dict) and all(g.get(f) for f in FIELDS)]
    s = STRONG if gaps and len(full) == len(gaps) else OKAY if full else WEAK if gaps else MISSING
    out.append(chk("5. Structured for handoff", s,
                   f"{len(full)}/{len(gaps)} gaps have all of {FIELDS}",
                   CHANGE_SCHEMA if s < STRONG else None))

    lane = re.findall(r"\b(should join|should enter|he should|can't get in|out of reach|"
                      r"tier \d|recommend)\b", t, re.I)
    s = STRONG if not lane else WEAK
    out.append(chk("6. Stays in its lane", s,
                   "reports only" if not lane else f"prescriptive/tier language: {lane}",
                   FIX_PROMPT if lane else None))
    return out

# ==========================================================================
def fitness(checks):
    gate = next((c for c in checks if c.get("gate")), None)
    if gate and gate["score"] <= WEAK:
        return "F (gated)", "Dossier gate failed — stop and go back to the parent before grading the rest."
    avg = sum(c["score"] for c in checks) / len(checks)
    letter = ("A" if avg >= 2.75 else "B" if avg >= 2.25 else
              "C" if avg >= 1.75 else "D" if avg >= 1.0 else "F")
    meaning = {"A": "Ready. Hand it downstream.", "B": "Small fixes; usable.",
               "C": "Real gaps; fix before relying on it.",
               "D": "Not usable; rework.", "F": "Not usable; rework."}[letter]
    return f"{letter} ({avg:.2f}/3)", meaning

def report(title, checks):
    print(f"\n{title}\n" + "-"*74)
    for c in checks:
        tag = "  [GATE]" if c.get("gate") else ""
        print(f"  {c['score']}/3  {c['level']:14s} {c['check']}{tag}")
        print(f"        {c['why']}")
        if c["fix"]: print(f"        FIX -> {c['fix']}")
    g, m = fitness(checks)
    print(f"\n  FITNESS: {g}  — {m}")
    return g

def main(path):
    st = json.load(open(path))
    print("="*74); print(f"PER-AGENT RUBRIC REPORT · {os.path.basename(path)}"); print("="*74)
    report("R1 — PROFILE  (rubric v2, four checks)",
           grade_r1(st.get("profile") or {}, st.get("intake") or {}))
    report("GAP ANALYST  (rubric v1, six checks)",
           grade_gap(st.get("gap") or {}, st.get("cards") or {}, st.get("profile") or {}))
    print("\n" + "="*74)
    print("NOTE: each agent is graded on its OWN object, per the rubric docs.")
    print("The rendered PDF is graded separately by evals/grade.py — that is R9 + modules.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/t.state.json")
