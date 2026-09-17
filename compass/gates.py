"""
RUNTIME ACCEPTANCE GATES — one per step boundary.  [feedback log #30]

The rubrics in evals/ grade a run AFTER it finishes. These run DURING it.

The question a gate asks is not "is this good?" but **"is this good enough for the NEXT
step to be meaningful?"** — fitness for purpose. A profile with no constraints doesn't
just score badly; it makes every downstream recommendation unbounded. Retrieval that
returns nothing doesn't just weaken the gap map; it makes the gap map fiction. Without
gates, one bad step quietly poisons everything after it and the failure surfaces at the
end, in the PDF, looking like a writing problem.

Gates are DETERMINISTIC and cheap, so they run on every step of every run for free.
Each returns one of four verdicts:

  PASS      continue
  RETRY     re-run this step once, handing it the failure as feedback
  DEGRADE   continue, but mark the state so downstream knows what is thin
            (never silently — a degraded run must be visible in the output)
  ESCALATE  stop. A human decides. Used where continuing would produce something a
            family might act on and be harmed by.
"""

PASS, RETRY, DEGRADE, ESCALATE = "PASS", "RETRY", "DEGRADE", "ESCALATE"


class GateResult:
    def __init__(self, step, verdict, failures=None, notes=""):
        self.step, self.verdict = step, verdict
        self.failures = failures or []
        self.notes = notes

    @property
    def ok(self):
        return self.verdict in (PASS, DEGRADE)

    def __repr__(self):
        f = f" · {'; '.join(self.failures)}" if self.failures else ""
        return f"[{self.verdict}] {self.step}{f}"


def _txt(o):
    if isinstance(o, str): return o
    if isinstance(o, dict): return " ".join(_txt(v) for v in o.values())
    if isinstance(o, list): return " ".join(_txt(v) for v in o)
    return str(o)


# --------------------------------------------------------------------------
def gate_intake(intake):
    """Before anything runs. Missing basics -> the whole plan is guesswork."""
    f = []
    pa = intake.get("parent_answers") or intake
    if not _txt(pa).strip():                       f.append("intake empty")
    if not intake.get("student"):                  f.append("no student block")
    if not (pa.get("constraints") or intake.get("constraints")):
        f.append("no constraints — every recommendation would be unbounded")
    if not (pa.get("intended_direction") or pa.get("intended")):
        f.append("no intended direction — retrieval has no target")
    return GateResult("intake", ESCALATE if f else PASS, f,
                      "ask the parent before running" if f else "")


def gate_profile(profile):
    """R1 feeds everything. Two failures make the rest meaningless."""
    f = []
    if not profile.get("spine") and "spine" not in _txt(profile.get("flags_to_confirm", "")).lower():
        f.append("no spine and no honest 'no clear spine' flag")
    if not profile.get("constraints"):
        f.append("constraints not carried — downstream cannot respect budget/location")
    import re
    nums = re.findall(r"\b\d{1,3}\s?%|\btier\b|\bodds\b", _txt(profile), re.I)
    if nums:
        f.append(f"numbers in the profile object (must be none): {nums[:3]}")
    return GateResult("profile", RETRY if f else PASS, f)


def gate_retrieval(cards, min_admits=5):
    """THE most important gate. Fictional or empty retrieval makes the entire
    downstream plan fiction — and it looks completely normal in the PDF."""
    f = []
    rows = (cards or {}).get("cards") or []
    if not rows:
        return GateResult("retrieval", ESCALATE, ["retrieval returned NO admits"],
                          "without real comparison students the plan is fiction")
    if (cards or {}).get("mock"):
        return GateResult("retrieval", ESCALATE, ["retrieval fell back to MOCK cards"],
                          "mock cards must never reach a real family's plan")
    if len(rows) < min_admits:
        f.append(f"only {len(rows)} admits (min {min_admits})")
    return GateResult("retrieval", DEGRADE if f else PASS, f,
                      "mark thin schools in the output" if f else "")


def gate_gap(gap):
    f = []
    gaps = gap.get("gaps") or []
    if not gaps:
        f.append("no gaps produced")
    VALID = {"at-or-above", "missing", "lower-level", "unknown-interest"}
    bad = [g.get("category") for g in gaps if isinstance(g, dict)
           and str(g.get("category", "")).lower() not in VALID]
    if bad:
        f.append(f"invalid categories: {bad[:3]}")
    nofreq = [g for g in gaps if isinstance(g, dict) and not g.get("frequency")]
    if nofreq:
        f.append(f"{len(nofreq)} gaps cite no tally frequency (invented counts)")
    import re
    if re.search(r"\bshould (join|enter|start)\b|can't get in|out of reach", _txt(gap), re.I):
        f.append("prescriptive language — the Gap Analyst diagnoses only")
    return GateResult("gap", RETRY if f else PASS, f)


def gate_strategy(strategy, gap, constraints):
    """A strategy that selects nothing, or selects everything, has not decided."""
    f = []
    moves = strategy.get("selected_moves") or []
    gaps = gap.get("gaps") or []
    if not moves:
        f.append("no moves selected — nothing was decided")
    if gaps and len(moves) >= len(gaps) and len(gaps) > 2:
        f.append(f"selected {len(moves)} of {len(gaps)} gaps — a pass-through, not a choice")
    if len(moves) > 6:
        f.append(f"{len(moves)} moves — no spike; effort is spread")
    if (strategy.get("dropped_moves") or []) and not (strategy.get("tensions") or []):
        f.append("moves dropped but no tensions recorded — the reasoning is invisible")
    return GateResult("strategy", RETRY if f else PASS, f)


def gate_plan(plan_goals, strategy):
    f = []
    cur = plan_goals.get("current_year") or []
    if not cur:
        f.append("no current-year plan — the parent has nothing to act on")
    moves = strategy.get("selected_moves") or []
    if moves and not plan_goals.get("multi_year_arc"):
        f.append("no multi-year arc")
    dated = [t for g in cur for t in (g.get("tasks") or []) if isinstance(t, dict) and t.get("term")]
    if cur and not dated:
        f.append("no current-year task carries a term/date")
    return GateResult("plan_goals", RETRY if f else PASS, f)


def gate_recs(recs):
    """No retry here. A fabricated program is the one defect a family acts on —
    it goes straight to a human."""
    f = []
    t = _txt(recs)
    if "[CATALOG]" in t or "a local program" in t.lower():
        f.append("placeholder shipped")
    unver = [r for r in (recs or []) if isinstance(r, dict)
             and not r.get("escalate") and not r.get("verified")
             and (r.get("recommendations") or r.get("name"))]
    if unver:
        f.append(f"{len(unver)} recommendation(s) neither verified nor escalated")
    return GateResult("plan_recs", ESCALATE if f else PASS, f,
                      "a parent will phone this number" if f else "")


def gate_draft(draft, allowed_numbers):
    """Last structural gate before the PDF."""
    import re
    f = []
    REQUIRED = ("cover", "profile", "target", "roadmap", "this_year", "parent_actions")
    missing = [k for k in REQUIRED if not draft.get(k)]
    if missing:
        f.append(f"missing sections: {missing}")
    pcts = set(re.findall(r"(\d{1,3}(?:\.\d)?)\s?%", _txt(draft)))
    allowed = {str(a) for a in allowed_numbers} | {str(int(float(a))) for a in allowed_numbers}
    stray = sorted(pcts - allowed)
    if stray:
        f.append(f"percentages not handed to the writer: {stray[:6]}")
    if re.search(r"\b(his|her|their) (chance|odds|probability)\b", _txt(draft), re.I):
        f.append("personal-odds phrasing")
    return GateResult("writer", RETRY if f else PASS, f)


def summarise(results):
    """The quality trail — what degraded, and where."""
    worst = PASS
    order = {PASS: 0, DEGRADE: 1, RETRY: 2, ESCALATE: 3}
    for r in results:
        if order[r.verdict] > order[worst]:
            worst = r.verdict
    return {"overall": worst,
            "trail": [{"step": r.step, "verdict": r.verdict, "failures": r.failures}
                      for r in results],
            "blocked": worst == ESCALATE}


def gate_two_paths(tp, strategy=None):
    """R5. Two failures make the Outcome Cards meaningless: asserted fit, and a
    stretch path that is a different student.  [#29]"""
    f = []
    tgt = tp.get("target_variant") or {}
    st = tp.get("stretch_variant") or {}
    if not tgt or not st:
        return GateResult("two_paths", RETRY, ["missing target or stretch variant"])

    # fit must be computed, with n — this is the gate within the gate
    fits = tp.get("fit_assessment") or []
    if not fits:
        f.append("no fit assessment — the cards would have nothing behind them")
    no_n = [x.get("school") for x in fits if isinstance(x, dict) and not x.get("n")]
    if no_n:
        f.append(f"fit claimed with no n for: {no_n[:3]}")

    # both stretch mechanisms present, and each credential says which produced it
    prof = st.get("achievement_profile") or []
    no_via = [a for a in prof if isinstance(a, dict) and a.get("via") not in ("intensified", "added")]
    if prof and no_via:
        f.append(f"{len(no_via)} stretch credential(s) don't say how they were produced (via)")
    if prof and not any(a.get("via") == "intensified" for a in prof if isinstance(a, dict)):
        f.append("stretch built only by adding — that reads as a different student")

    # same spine
    if tgt.get("spine") and st.get("spine") and tgt["spine"] != st["spine"]:
        f.append("stretch has a different spine — not a version of this plan")

    # added credentials must come from strategy's stretch-tagged moves
    if strategy:
        tagged = {str(m.get("which_gap") or m.get("move") or "").lower()
                  for m in (strategy.get("selected_moves") or [])
                  if str(m.get("intensity", "")).lower() == "stretch"}
        added = [a for a in prof if isinstance(a, dict) and a.get("via") == "added"]
        if added and tagged and not any(
                any(t and t in _txt(a).lower() for t in tagged) for a in added):
            f.append("added stretch credentials trace to no stretch-tagged move")

    # the delta must be priced
    d = tp.get("delta") or {}
    if not (d.get("extra_hours_per_week") or d.get("extra_cost")):
        f.append("delta not priced — the stretch path looks free")

    import re
    if re.search(r"moves? (up|from) .{0,20}(reach|target|likely)", _txt(tp), re.I):
        f.append("implies a SCHOOL changed band — fit moves, selectivity does not")
    return GateResult("two_paths", RETRY if f else PASS, f)
