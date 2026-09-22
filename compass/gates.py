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
    # Q8: "Has [child] mentioned any schools they like — even casually?" The form asks
    # it; a record that does not carry it cannot be retrieved against, and the run
    # will stop at step 3 rather than at step 0 where it is cheap to fix. [#46]
    q8 = pa.get("schools_child_mentioned")
    if q8 is None:
        f.append("Q8 (schools the child has mentioned) missing from the record — "
                 "map it from the intake form")
    elif isinstance(q8, dict) and not q8.get("answer"):
        f.append("Q8 was not answered — ask the parent which schools have come up, "
                 "even casually. A parent's own alma mater is not an answer.")
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
    # Accept either spelling of the closed set. The prompt names these with
    # underscores and the gate was written with hyphens, so a correctly
    # categorised gap map failed the gate on punctuation. [#54]
    VALID = {"at_or_above", "missing", "lower_level", "unknown_interest"}
    bad = [g.get("category") for g in gaps if isinstance(g, dict)
           and str(g.get("category", "")).lower().replace("-", "_") not in VALID]
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
    # A spike is ONE thread at core intensity, not a short list. Counting moves
    # measured the wrong thing: a plan with seven moves and one core is a spike
    # with support; a plan with four moves all marked core is not. The prompt was
    # changed to say exactly that (#39) and the gate was still counting. [#54]
    core = [m for m in moves if str(m.get("intensity", "")).lower() == "core"]
    if moves and not core:
        f.append("nothing marked core — no spike; the plan has no centre")
    if len(core) > 1:
        f.append(f"{len(core)} moves at core intensity — a spike is exactly one")
    if len(moves) > 9:
        f.append(f"{len(moves)} moves — more threads than a week can hold")
    if (strategy.get("dropped_moves") or []) and not (strategy.get("tensions") or []):
        f.append("moves dropped but no tensions recorded — the reasoning is invisible")
    return GateResult("strategy", RETRY if f else PASS, f)


def gate_plan(plan_goals, strategy):
    """R6 now returns `grades[]` covering every year to 12, with `is_current_year`
    on one of them. The old gate only knew about `current_year` and failed a
    correct five-year plan for not having the one-year shape. [#54]"""
    f = []
    grades = plan_goals.get("grades") or []
    cur = ([g for g in grades if g.get("is_current_year")]
           or grades[:1] or plan_goals.get("current_year") or [])
    if not cur:
        f.append("no current-year plan — the parent has nothing to act on")
    if grades and len(grades) < 2:
        f.append("only one grade planned — this is a multi-year plan, not a year plan")
    thin = [g.get("grade") for g in grades if len(g.get("goals") or []) < 2]
    if thin:
        f.append(f"grade(s) with fewer than two goals: {thin}")
    moves = strategy.get("selected_moves") or []
    if moves and not (plan_goals.get("multi_year_arc") or grades):
        f.append("no multi-year arc")
    # Walk the plan whatever depth it nests to. R6 legitimately returns either
    # current_year -> goals -> tasks, or current_year -> TERMS -> goals -> tasks.
    # The old version only looked one level down, so a correctly dated plan in the
    # deeper shape was rejected for "carrying no dates" — a false failure that cost
    # a retry on every run. Shape is the schema's job; the gate checks substance.
    def _tasks(node):
        if isinstance(node, dict):
            for k in ("tasks", "goals", "terms", "rows"):
                for child in (node.get(k) or []):
                    yield from _tasks(child)
            if node.get("term") or node.get("by_when") or node.get("date"):
                yield node
        elif isinstance(node, list):
            for child in node:
                yield from _tasks(child)

    dated = list(_tasks(cur))
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
    # Accept every shape R7 actually returns. The old check looked only for a
    # `recommendations` key, so a rec returning primary/alternates passed unread —
    # including one whose own escalate flag was true. A gate that passes bad work
    # is worse than one that fails good work.
    def _payload(r):
        for k in ("recommendations", "primary", "alternates", "name", "options"):
            if r.get(k):
                return True
        return False

    unver = [r for r in (recs or []) if isinstance(r, dict)
             and not r.get("escalate") and not r.get("verified") and _payload(r)]
    if unver:
        f.append(f"{len(unver)} recommendation(s) neither verified nor escalated")
    flagged = [r for r in (recs or []) if isinstance(r, dict) and r.get("escalate")]
    if flagged:
        f.append(f"{len(flagged)} recommendation(s) raised their own escalate flag")
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
    # Match the WHOLE number, decimals and all. The old pattern allowed one decimal
    # place, so "15.64%" matched as "64" and was reported as a number nobody handed
    # over — a false failure on a correctly cited rate.
    txt = _txt(draft)
    pcts = {float(x) for x in re.findall(r"(\d{1,3}(?:\.\d+)?)\s?%", txt)}
    allowed = set()
    for a in allowed_numbers:
        try:
            v = float(a)
        except (TypeError, ValueError):
            continue
        allowed |= {round(v, 2), round(v, 1), float(round(v))}
    stray = sorted(v for v in pcts
                   if not any(abs(v - a) < 0.051 for a in allowed))
    if stray:
        f.append(f"percentages not handed to the writer: {stray[:6]}")
    # "not his odds" is the rule being OBEYED, not broken. Only flag the phrase when
    # it is asserting odds, i.e. when it is not negated right before.
    if re.search(r"(?<!not )(?<!never )\b(his|her|their) (chance|odds|probability)\b",
                 txt, re.I):
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


def gate_document(draft, plan_goals):
    """PLAN -> DOCUMENT RECONCILIATION. [#50]

    We already reconcile the Outcome Card against the plan in both directions (#17).
    The equivalent check for the roadmap never existed, so when the writer was told to
    cut, it cut R6's goals and nothing noticed. A goal that exists in the plan and not
    in the document is the plan quietly shrinking between two steps.
    """
    f = []
    planned = []
    for gr in (plan_goals.get("grades") or plan_goals.get("current_year") or []):
        for go in (gr.get("goals") or []):
            t = go.get("goal") or go.get("title")
            if t:
                planned.append((gr.get("grade"), t))
    if not planned:
        return GateResult("document", PASS, [], "no goals to reconcile")

    rendered = _txt(draft.get("roadmap", {})).lower()
    missing = [f"grade {g}: {t[:48]}" for g, t in planned
               if not _overlap(t.lower(), rendered)]
    if missing:
        f.append(f"{len(missing)} plan goal(s) never reach the document: {missing[:3]}")

    # Normalise before comparing: the plan says 8, the document says "Grade 8".
    # This is the fourth gate to fail correct work on a representation difference
    # rather than a substance one — compare meaning, never spelling. [#54]
    def _num(x):
        import re
        m = re.search(r"\d+", str(x))
        return m.group(0) if m else str(x).strip().lower()

    grades_planned = {g for g, _ in planned if g}
    grades_rendered = {_num(x.get("grade")) for x in (draft.get("roadmap", {}).get("grades") or [])}
    gone = [g for g in grades_planned if _num(g) not in grades_rendered]
    if gone:
        f.append(f"grade(s) in the plan but not in the roadmap: {sorted(gone)}")

    # TASK FIDELITY. [#56] Rendering every goal is not enough — the last run rendered
    # all 20 and still lost the plan, because each task row was compressed from ~19
    # words to ~11 and the names, fees and deadlines went out with the connective
    # tissue. Presence was checked; substance was not. Check substance.
    import re as _re

    def _goals_of(container):
        """Yield (grade, goal_dict). The current year nests goals under terms[]; the
        later grades keep them under rows[]/goals[]. [#57]"""
        for gr in (container.get("grades") or container.get("current_year") or []):
            for tm in (gr.get("terms") or []):
                for go in (tm.get("goals") or []):
                    yield gr.get("grade"), go
            for go in (gr.get("goals") or gr.get("rows") or []):
                yield gr.get("grade"), go

    def _tasks_of(container, key_tasks="tasks"):
        out = []
        for _, go in _goals_of(container):
            for t in (go.get(key_tasks) or []):
                txt = t.get("text") if isinstance(t, dict) else t
                if txt:
                    out.append(str(txt))
        return out

    plan_tasks = _tasks_of(plan_goals)
    doc_tasks = _tasks_of(draft.get("roadmap", {}))

    if plan_tasks and doc_tasks:
        stubs = [t for t in doc_tasks if len(t.split()) < 12]
        if len(stubs) > len(doc_tasks) * 0.15:
            f.append(f"{len(stubs)} of {len(doc_tasks)} task rows are under 12 words "
                     f"(e.g. {stubs[0][:60]!r}) — rows were compressed, not the prose")

        # A fact R6 put in a task must survive somewhere in the rendered roadmap.
        # Capitalised multi-word names, prices and deadlines are the ones that vanish.
        def _facts(s):
            return set(_re.findall(r"\$[\d,]+|\b[A-Z][a-z]{2,}(?: [A-Z][a-z]{2,})+\b", s))

        plan_facts = set().union(*[_facts(t) for t in plan_tasks]) if plan_tasks else set()

        # Match on the distinctive token, not the exact string. The plan says "Acton
        # Children's Business Fair" and the document says "the Children's Business Fair,
        # run by Acton" — the organisation is named, shorter. Demanding the bigram fails
        # correct work on spelling, which is the #54 mistake a fifth time. A name has
        # survived when its rarest word has. [#57]
        _COMMON = {"business", "fair", "children", "school", "high", "middle", "county",
                   "city", "the", "of", "and", "grade", "summer", "fall", "spring"}

        def _survives(name):
            if name.startswith("$"):
                return name.lower() in rendered
            toks = [t for t in _re.findall(r"[A-Za-z]{3,}", name)
                    if t.lower() not in _COMMON]
            if not toks:
                return name.lower() in rendered
            return all(t.lower() in rendered for t in toks)

        lost = sorted(x for x in plan_facts if not _survives(x))
        if lost:
            f.append(f"{len(lost)} fact(s) the plan put in a task never reach the "
                     f"roadmap: {lost[:4]}")

    # A goal in a later grade may carry at most one row per term. The term repeated
    # down a single goal is the term stated four times, with the grouping left to the
    # reader. The current year does not hit this: its container IS the term. [#57]
    for gr in (draft.get("roadmap", {}).get("grades") or []):
        for go in (gr.get("rows") or gr.get("goals") or []):
            terms = [str((t or {}).get("term", "")).strip().lower()
                     for t in (go.get("tasks") or []) if isinstance(t, dict)]
            dupes = {t for t in terms if t and terms.count(t) > 1}
            if dupes:
                f.append(f"grade {gr.get('grade')}, goal "
                         f"{str(go.get('goal') or go.get('title'))[:40]!r}: "
                         f"{sorted(dupes)} appears more than once — one row per term")

    return GateResult("document", RETRY if f else PASS, f,
                      "the writer cut the plan, not the prose" if f else "")


def _overlap(goal_text, haystack, need=0.5):
    """Did this goal survive into the document, in any wording?"""
    import re
    words = {w for w in re.findall(r"[a-z]{4,}", goal_text)
             if w not in {"with", "that", "this", "から", "keep", "from", "into", "year"}}
    if not words:
        return True
    hit = sum(1 for w in words if w in haystack)
    return hit / len(words) >= need


def gate_budget(ledger):
    """The year's recommendations must fit the family's stated ceiling. [#51]

    A plan a family cannot afford is not a plan; it is a sales document. This is a
    RETRY rather than an escalation because the fix is in our hands — drop or
    substitute the expensive item — not the parent's.
    """
    f = []
    if not ledger:
        return GateResult("budget", PASS, [])
    if not ledger.get("within_budget"):
        over = (ledger.get("over_by") or 0) + (ledger.get("summer_over_by") or 0)
        biggest = [i["name"] for i in (ledger.get("items") or [])[:2]]
        f.append(f"over the family's stated budget by ${over:.0f} — largest: {biggest}")
    if ledger.get("geographically_blocked"):
        f.append(f"{len(ledger['geographically_blocked'])} recommendation(s) outside the "
                 "family's stated region reached the plan")
    if ledger.get("above_session_ceiling"):
        f.append(f"{len(ledger['above_session_ceiling'])} above the per-session ceiling")
    return GateResult("budget", RETRY if f else PASS, f,
                      "a plan they cannot afford is not a plan" if f else "")
