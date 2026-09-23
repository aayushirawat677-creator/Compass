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

        def _survives(name, haystack):
            if name.startswith("$"):
                return name.lower() in haystack
            toks = [t for t in _re.findall(r"[A-Za-z]{3,}", name)
                    if t.lower() not in _COMMON]
            if not toks:
                return name.lower() in haystack
            return all(t.lower() in haystack for t in toks)

        # Survives into the DOCUMENT, not only into the roadmap. When this check was
        # written the roadmap was the only place a fact could live; #57 then split the
        # job between the roadmap and this_year — what happens and when, versus which
        # programme and what it costs — so a price correctly LEAVES the roadmap for the
        # card. Checking only the roadmap made rule #56 fail work that rule #57 required.
        # Eighth gate bug, and the second where two of our own rules pulled against each
        # other. A fact must reach the reader; it need not reach a particular page. [#62]
        whole_doc = " ".join([rendered,
                              _txt(draft.get("this_year", {})).lower(),
                              _txt(draft.get("parent_actions", {})).lower()])
        lost = sorted(x for x in plan_facts if not _survives(x, whole_doc))
        if lost:
            f.append(f"{len(lost)} fact(s) the plan put in a task never reach the "
                     f"roadmap: {lost[:4]}")

    # The term repeated down a single goal is the term stated four times, with the
    # grouping left to the reader. Every grade is now term-organised, so the defect
    # takes two forms: a grade that kept the old goal-major shape, and a goal listed
    # twice inside one term block. [#57]
    for gr in (draft.get("roadmap", {}).get("grades") or []):
        if not gr.get("terms"):
            if gr.get("rows") or gr.get("goals"):
                f.append(f"grade {gr.get('grade')} is not organised by term — every "
                         f"grade uses the same semester shape")
            continue
        for tm in gr["terms"]:
            names = [str((go or {}).get("goal") or (go or {}).get("title") or "").strip().lower()
                     for go in (tm.get("goals") or [])]
            dupes = {n for n in names if n and names.count(n) > 1}
            if dupes:
                f.append(f"grade {gr.get('grade')}, {tm.get('term')}: "
                         f"{len(dupes)} goal(s) listed twice in one term — merge them")

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


def gate_appraisal(appraisals, activities):
    """ACTIVITY APPRAISAL. [#59]

    The appraiser is the first step allowed to say an activity is not worth five years, so
    it is also the first step that can do real damage by being wrong about a child nobody
    here has met. This gate checks the three ways that happens.
    """
    import json
    f = []
    appraisals = list(appraisals or [])
    activities = list(activities or [])

    # 1. Every activity gets appraised. A silently skipped one is carried by default, which
    #    is exactly the failure this step exists to remove.
    done = {str((a or {}).get("activity", "")).strip().lower() for a in appraisals}
    missed = [str(a.get("name") or a.get("activity") or a)[:40] for a in activities
              if str(a.get("name") or a.get("activity") or a).strip().lower() not in done]
    if missed:
        f.append(f"{len(missed)} activity(ies) never appraised: {missed[:3]}")

    VERDICTS = {"carry", "convert", "keep_as_interest", "retire"}
    for a in appraisals:
        name = str(a.get("activity", "?"))[:34]
        ap = a.get("appraisal") or {}
        v = str(ap.get("verdict", "")).strip().lower()

        if v not in VERDICTS:
            f.append(f"{name}: verdict {v!r} is not one of {sorted(VERDICTS)}")

        # 2. A ceiling with no reason cannot be reviewed, argued with, or corrected — and a
        #    judgment nobody can argue with is the one most likely to stand while wrong.
        if not str(ap.get("why") or "").strip():
            f.append(f"{name}: verdict with no stated reason")
        if v == "convert":
            c = ap.get("conversion") or {}
            if not c.get("becomes") or not c.get("uses_history_how"):
                f.append(f"{name}: convert without a route that uses the student's history "
                         f"— that is a replacement, not a conversion")

        # 3. The family decides the hard ones. A convert or retire on the student's longest
        #    or heaviest thread must reach them as a question. [#59]
        src = next((x for x in activities
                    if str(x.get("name") or x.get("activity") or "").strip().lower()
                    == str(a.get("activity", "")).strip().lower()), {}) or {}
        sig = (src.get("signals") or {})
        # Intake values arrive as ranges and prose — "4-6", "about 5", "<1 yr". Take the
        # TOP of a range, because the question is whether this is one of the student's
        # heavier threads and the ceiling is what decides that. The same range bug bit
        # the budget ledger; parse it here rather than crashing on it. [#54]
        def _hi(v):
            import re as _r
            nums = _r.findall(r"\d+(?:\.\d+)?", str(v or ""))
            return max((float(n) for n in nums), default=0.0)

        anchor = (_hi(sig.get("hours_per_week")) >= 4
                  or _hi(sig.get("years") or sig.get("years_involved")) >= 2)
        if v in ("convert", "retire") and anchor and not a.get("needs_family_input"):
            f.append(f"{name}: {v} on a long-running or high-hours thread without "
                     f"needs_family_input — the family never gets to correct it")
        if a.get("needs_family_input") and not str(a.get("family_question") or "").strip():
            f.append(f"{name}: needs_family_input with no question written")

        # Layer separation. A cached type entry that names a child poisons every future
        # family that gets the cache hit.
        tk = json.dumps(a.get("type_knowledge") or {}).lower()
        if any(k in tk for k in ("grade 8", "grade 9", "grade 10", "grade 11", "grade 12")):
            f.append(f"{name}: child-specific detail in type_knowledge — it would be cached")

    low = [str(a.get("activity", "?"))[:24] for a in appraisals
           if str(a.get("confidence", "")).lower() == "low"]
    note = ""
    if low and not f:
        note = f"low confidence on {low[:3]} — carry these gently"
    return GateResult("appraisal", RETRY if f else PASS, f,
                      note or ("an activity carried by default is the failure this "
                               "step removes" if f else ""))


def _plan_goal_rows(plan_goals):
    """(grade, goal_text, goal_dict) for every goal in the plan, at any depth. [#60]"""
    out = []
    for gr in (plan_goals.get("grades") or plan_goals.get("current_year") or []):
        g = gr.get("grade")
        buckets = list(gr.get("goals") or gr.get("rows") or [])
        for tm in (gr.get("terms") or []):
            buckets += list(tm.get("goals") or [])
        for go in buckets:
            t = str(go.get("goal") or go.get("title") or "")
            if t:
                out.append((g, t, go))
    return out


def gate_honours_appraisal(plan_goals, appraisals):
    """DOES THE PLAN ACTUALLY DO WHAT THE APPRAISAL SAID? [#60]

    Correct step order is necessary and not sufficient. The appraiser runs before strategy
    and the plan, and both are TOLD to honour its verdicts — and telling a model something
    has never been a guarantee here. That is the whole lesson of #50 and #56: when the
    writer quietly cut the plan's goals, the ordering was fine; what was missing was a
    check reconciling the two.

    We reconcile writer-against-plan. This reconciles plan-against-appraisal, which was the
    one direction nothing looked at.
    """
    import re
    f = []
    rows = _plan_goal_rows(plan_goals)
    if not rows or not appraisals:
        return GateResult("honours_appraisal", PASS, [], "nothing to reconcile")

    def _gnum(x):
        m = re.search(r"\d+", str(x))
        return int(m.group(0)) if m else None

    def _mentions(text, name):
        """Does this goal concern that activity? Match on distinctive words, not the
        literal string — the plan says 'the card business', the intake says 'Pokemon card
        business'. Comparing spelling where the rule is about substance is the mistake
        five gates have already made. [#54]"""
        stop = {"the", "and", "his", "her", "for", "with", "business", "club", "team"}
        toks = [w for w in re.findall(r"[a-z]{4,}", str(name).lower()) if w not in stop]
        return any(t in str(text).lower() for t in toks) if toks else False

    for a in appraisals:
        name = str(a.get("activity", ""))
        ap = a.get("appraisal") or {}
        verdict = str(ap.get("verdict", "")).lower()
        hits = [(g, t, go) for g, t, go in rows if _mentions(t, name)]

        if verdict == "convert":
            conv = ap.get("conversion") or {}
            by = _gnum(conv.get("grade"))
            # A conversion means the activity moves INSIDE something that vouches — a club,
            # a job, a team, a judged competition. Match on that substance, not on the
            # words of `becomes`: that field names DECA and FBLA, and #63 forbids the plan
            # from printing those, so keyword-matching it failed the plan for obeying the
            # newer rule. Ninth gate bug, and the third time a new rule has invalidated an
            # older gate's assumption. [#65]
            INSIDE = (r"\b(club|team|chapter|organisation|organization|society|league|"
                      r"job|work|shift|role|officer|intern\w*|employ\w*|shop|store|"
                      r"compet\w*|contest|tournament|fair|judged|judges|entry|enter)\b")
            landed = [g for g, t, go in hits
                      if re.search(INSIDE, t + " " + _txt(go.get("tasks") or []), re.I)]

            # An open family question suspends the CONVERSION, not the activity. This gate
            # and gate_open_questions were pulling opposite ways: one demanded the
            # conversion appear, the other forbade enacting it before the family answers.
            # Eleventh gate bug of the session and the fourth of this class. The resolution
            # is what the plan should do anyway — carry the activity as it stands, and
            # schedule the step that PRODUCES the decision. What it may never do is drop
            # the thread on the floor while a question about it is printed to the family.
            # [#65]
            if a.get("needs_family_input"):
                if not hits:
                    f.append(f"{name[:30]}: a question about this is going to the family, "
                             f"and the plan carries no goal for it at all — pending is not "
                             f"the same as gone")
            elif not landed:
                f.append(f"{name[:30]}: appraised CONVERT but no goal in any grade carries "
                         f"the conversion — the verdict reached the document and not the plan")
            elif by is not None:
                early = [g for g in landed if _gnum(g) is not None and _gnum(g) <= by]
                if not early:
                    f.append(f"{name[:30]}: conversion lands at grade {sorted(landed)} but "
                             f"the appraisal placed it by grade {by}")

        if verdict == "retire":
            live = [g for g, t, go in hits
                    if str((go or {}).get("track", "target")).lower() != "dropped"]
            if live:
                f.append(f"{name[:30]}: appraised RETIRE but still carries goals in "
                         f"grade(s) {sorted({g for g in live})}")

        if verdict == "keep_as_interest":
            # It is protected and asked nothing of. A performance target attached to it is
            # the plan quietly promoting it back into a credential.
            #
            # But a goal that REMOVES performance pressure names the same words. The first
            # version of this check failed "Free up hours by taking chess, cooking and
            # theater off the competition calendar" — the plan doing precisely the right
            # thing — because "competition" appeared in it. Sixth gate bug of this family:
            # matching a word where the rule is about direction. Check the verb. [#60]
            PERF = r"\b(qualify|place|win|rank|compet\w*|championship|state|national|" \
                   r"regional|award|title|varsity)\b"
            REMOVES = r"\b(off|out of|drop\w*|stop\w*|free up|remove\w*|no longer|" \
                      r"without|leave\w*|keep\w* (?:it|them|both|all)? ?as)\b"
            pushed = [t for _, t, _ in hits
                      if re.search(PERF, t, re.I) and not re.search(REMOVES, t, re.I)]
            if pushed:
                f.append(f"{name[:30]}: appraised KEEP_AS_INTEREST but the plan attaches a "
                         f"performance target: {pushed[0][:52]!r}")

    return GateResult("honours_appraisal", RETRY if f else PASS, f,
                      "correct order does not make the plan obey" if f else "")


def gate_open_questions(plan_goals, appraisals, draft=None):
    """A QUESTION ASKED MUST STAY OPEN UNTIL IT IS ANSWERED. [#60]

    The appraiser sets `needs_family_input` on the calls we decided not to make alone —
    a convert or retire on the student's longest-running or heaviest thread. The document
    then prints that question to the parent.

    The failure this catches is the one the first appraiser PDF actually committed: page 2
    asks the family for their view on the card business, and the roadmap four pages later
    has already chosen. Printing a question and then acting as though it were answered is
    worse than never asking, because it tells the family their answer mattered when it did
    not.
    """
    import re
    f = []
    open_ones = [a for a in (appraisals or []) if a.get("needs_family_input")]
    if not open_ones:
        return GateResult("open_questions", PASS, [], "nothing was asked")

    rows = _plan_goal_rows(plan_goals)
    for a in open_ones:
        name = str(a.get("activity", ""))
        if not str(a.get("family_question") or "").strip():
            f.append(f"{name[:30]}: flagged for the family with no question written")

        # The plan may CARRY the activity as it stands — that is what it is told to do
        # while waiting. What it may not do is enact the branch we asked about.
        verdict = str((a.get("appraisal") or {}).get("verdict", "")).lower()
        conv = (a.get("appraisal") or {}).get("conversion") or {}
        becomes = str(conv.get("becomes") or "")
        key = [w for w in re.findall(r"[a-z]{6,}", becomes.lower())][:5]
        if verdict in ("convert", "retire") and key:
            enacted = [t for _, t, _ in rows
                       if sum(k in t.lower() for k in key) >= 2]
            if enacted and not _asks_in_document(draft, name):
                f.append(f"{name[:30]}: the plan enacts the branch we said we would ask "
                         f"about ({enacted[0][:44]!r}) and the document never puts the "
                         f"question to the family")
    return GateResult("open_questions", RETRY if f else PASS, f,
                      "a question printed and then overruled is worse than no question"
                      if f else "")


def _asks_in_document(draft, activity_name):
    """Is the question actually in front of the parent? Absent a draft we cannot tell, and
    we do not fail a step for something we cannot see."""
    if draft is None:
        return True
    import re
    qs = ((draft.get("profile") or {}).get("family_questions") or [])
    stop = {"the", "and", "his", "her", "business"}
    toks = [w for w in re.findall(r"[a-z]{4,}", activity_name.lower()) if w not in stop]
    blob = _txt(qs).lower()
    return any(t in blob for t in toks) if toks else bool(qs)


# Bodies that run youth competition ladders. Naming one in a grade the student has not
# reached assumes a chapter at a school they have not started. [#62]
# NOT in this list: the FORMATS of an activity. Model UN, Public Forum, Lincoln-Douglas,
# Congress and mock trial are kinds of debate, not organisations with chapters — and #63
# requires the Explore years to name them, because sampling the formats is the point of
# those years. The first version treated "Model UN" as a programme and failed a plan for
# obeying the newer rule. Tenth gate bug, same class as the eighth. [#65]
_NAMED_BODIES = (r"\b(DECA|FBLA|FCCLA|ProStart|NSDA|CHSSA|NFTE|Diamond Challenge|"
                 r"Conrad Challenge|Blue Ocean|USACO|USAMO|Science Olympiad|Acton|"
                 r"National Leadership Conference|Invitational|Thespian)\b")


def gate_horizon(plan_goals, current_grade, appraisals=None):
    """DEPTH BY HORIZON — and the roadmap is general in EVERY grade. [#63]

    Earlier this gate demanded that the CURRENT year's roadmap rows carry a name, price or
    contact. That was wrong twice over: it duplicated the `this_year` section, whose whole
    job is that layer, and it made the roadmap page unscannable when being scannable is
    what the roadmap is for. One fact, one place (#32).

    So the rule is now simple in one direction: NO roadmap row, in any grade, names a
    programme, a price or a date. The specificity lives in `this_year`, and `gate_document`
    already checks that every fact reaches the reader somewhere.
    """
    import re
    f = []
    for grade, text, go in _plan_goal_rows(plan_goals):
        body = text + " " + _txt(go.get("tasks") or [])
        named = sorted(set(m.group(0) for m in re.finditer(_NAMED_BODIES, body, re.I)))
        money = re.findall(r"\$\s?\d[\d,]*", body)
        dated = re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                           r"[a-z]*\.? ?\d{1,2}\b", body)
        if named or money or dated:
            bits = (named + money + dated)[:3]
            f.append(f"grade {grade}: roadmap row carries {bits} — programme names, "
                     f"prices and dates belong in this_year, not the roadmap")

        # The goal line is the line that gets read. Ours were failing on length and on
        # internal vocabulary a parent has no reason to know. [#63]
        JARGON = (r"\b(rung|credential|load[- ]bearing|outside body|vouch\w*|"
                  r"at_or_above|lower_level|differentiator|spike|signal\w*|"
                  r"modal|cohort|admit pattern)\b")
        j = sorted(set(m.group(0).lower() for m in re.finditer(JARGON, text, re.I)))
        if j:
            f.append(f"grade {grade}: goal uses our vocabulary, not the family's: {j[:3]}")
        if len(text.split()) > 16:
            f.append(f"grade {grade}: goal is {len(text.split())} words — one short "
                     f"sentence a parent reads once: {text[:46]!r}")

    return GateResult("horizon", RETRY if f else PASS, f,
                      "the roadmap shows the arc; this_year carries the detail"
                      if f else "")


def _is_protected(goal_text, appraisals):
    """Does this goal belong to an activity the appraisal told us to leave alone?

    `keep_as_interest` means the plan protects it and asks nothing of it — so it is
    supposed to carry no programme, price or contact, and the near-horizon specificity
    rule must not fire on it. [#62]
    """
    import re
    # A goal whose own verb is maintain-or-reduce asks nothing new of the student, so it
    # correctly carries no programme and no price. Chess is the case that exposed this:
    # the appraisal said `carry` and the strategy said MAINTAIN, so the verdict alone did
    # not exempt it and the gate demanded a contact for "keep chess running at the size it
    # is". The requirement is on goals that ask for something NEW. [#62]
    import re as _re
    if _re.search(r"\bkeep\w*\b.*\b(size|running|going|as (it|they) (is|are)|unchanged)\b"
                  r"|\bat the size\b|\bnothing (new|riding)\b|\bwithout growing\b"
                  r"|\b(hold|leave)\w* .*\b(steady|as it stands|alone)\b",
                  str(goal_text), _re.I):
        return True

    for a in (appraisals or []):
        if str((a.get("appraisal") or {}).get("verdict", "")).lower() not in (
                "keep_as_interest", "retire"):
            continue
        stop = {"the", "and", "his", "her", "for", "with", "business", "club", "team"}
        toks = [w for w in re.findall(r"[a-z]{4,}", str(a.get("activity", "")).lower())
                if w not in stop]
        if toks and any(t in str(goal_text).lower() for t in toks):
            return True
    return False


def gate_academics(plan_goals, admit_pattern=None, current_grade=None):
    """ACADEMICS IN EVERY GRADE. [#64]

    The first five-year plan carried nineteen goals and not one was academic. The gap step
    had measured an academics floor at all six target schools; strategy dropped every one
    and nothing noticed, because no gate had ever been asked to look for the category that
    was missing rather than at the quality of the categories present.

    That is the general shape of this bug: every other gate checks what IS there. An entire
    domain going absent is invisible to all of them.

    Measured, for the record: across the six schools in this worked example, 80.6% of the
    admits we hold sat in the 3.8+ band (n=899) — Georgetown 95%, Berkeley 90%, Michigan
    82%, Penn 77%, NYU 70%. The floor is real and it is not folklore.
    """
    import re
    f = []
    rows = _plan_goal_rows(plan_goals)
    if not rows:
        return GateResult("academics", PASS, [], "no plan to check")

    ACADEMIC = (r"\b(grade\w*|gpa|marks?|report card|transcript|tutor\w*|study|studies|"
                r"course\w*|class(es)?|subject\w*|math\w*|science|english|honors|honours|"
                r"\bap\b|advanced placement|exam\w*|test\w*|sat\b|act\b|psat|"
                r"counsel\w*|schedule|rigou?r|homework|academic\w*)\b")

    by_grade = {}
    for grade, text, go in rows:
        try:
            g = int(re.search(r"\d+", str(grade)).group(0))
        except (AttributeError, TypeError, ValueError):
            continue
        body = text + " " + _txt(go.get("tasks") or [])
        by_grade.setdefault(g, []).append(bool(re.search(ACADEMIC, body, re.I)))

    bare = sorted(g for g, hits in by_grade.items() if not any(hits))
    if bare:
        f.append(f"grade(s) {bare} carry no academic goal at all — grades are what gets a "
                 f"student read, and a GPA is cumulative, so a skipped year cannot be "
                 f"recovered later")

    # The chain has to start at the beginning, not at the year the number is reported.
    try:
        cur = int(re.search(r"\d+", str(current_grade)).group(0))
    except (AttributeError, TypeError, ValueError):
        cur = min(by_grade) if by_grade else None
    if cur is not None and cur in by_grade and not any(by_grade[cur]):
        f.append(f"the current year (grade {cur}) has no academic goal — raising a GPA "
                 f"takes a year or two, so this is the term the work starts in")

    # Testing has to appear before the year it is sat in.
    later = [g for g in by_grade if g >= 11]
    if later:
        # Accept the test by name OR by an unambiguous phrase. "Start test preparation,
        # taught first and practised after" is a testing goal; demanding the acronym
        # failed it. A test's NAME is durable and universal, unlike a school chapter, so
        # #63's ban on named programmes never applied to it — either form is correct here.
        # Twelfth gate bug this session. [#65]
        TESTING = (r"\b(sat|act|psat|nmsqt)\b|"
                   r"\b(college|admission\w*|standardi[sz]ed|entrance)\s+test\w*|"
                   r"\btest\s+(prep\w*|practice|preparation|sitting)|"
                   r"\b(sit|take|retake)\s+the\s+tests?\b")
        test_rows = [t for g, t, go in rows
                     if re.search(TESTING, t + " " + _txt(go.get("tasks") or []), re.I)]
        if not test_rows:
            f.append("no goal anywhere mentions the college tests, though the plan runs "
                     "through the years they are taken in")

    # If we have the band, the plan should be aiming at it rather than at a number we made up.
    if admit_pattern:
        band = _txt(admit_pattern)
        m = re.search(r"\b([34]\.\d)\+?", band)
        if m:
            said = re.search(r"\b([34]\.\d)\b", _txt(plan_goals))
            if said and said.group(1) != m.group(1):
                f.append(f"the plan names GPA {said.group(1)} where the admit pattern for "
                         f"these schools says {m.group(1)} — use the band, not a guess")

    return GateResult("academics", RETRY if f else PASS, f,
                      "a plan with no academic thread has left out what decides it"
                      if f else "")


def gate_card_plan(two_paths, plan_goals):
    """THE CARD AND THE PLAN MUST BE THE SAME STORY. [#67]

    The Outcome Card says what the student's profile looks like in the fall he applies.
    The plan says what he does to get there. They were siblings off the same moves, never
    reconciled, so the card could describe one student and the plan build another — and
    the family would read both on the same document.

    `gate_two_paths` checks the card against STRATEGY. `gate_document` checks the document
    against the PLAN. This was the missing edge: card against plan, both directions, which
    is the shape that worked for #50 and #56.

    Found by asking a plain question — does the card update when the goals do? It did not,
    and the delivered PDF had a card listing six credentials with no academics entry while
    every grade of the plan carried an academic goal.
    """
    import re
    f = []
    tgt = (two_paths or {}).get("target_variant") or {}
    prof = tgt.get("achievement_profile") or []
    rows = _plan_goal_rows(plan_goals)
    if not prof or not rows:
        return GateResult("card_plan", PASS, [], "nothing to reconcile")

    plan_text = " ".join(t + " " + _txt(go.get("tasks") or []) for _, t, go in rows).lower()

    # Domain vocabulary, so a credential named `service_nonprofit` can be recognised in a
    # goal that says "volunteer with one local group". Matching the slug itself would be
    # the spelling-not-substance mistake five earlier gates already made. [#54]
    DOMAIN_WORDS = {
        "venture": ["business", "sell", "selling", "trad", "shop", "market", "customer"],
        "work_internship": ["job", "work", "shift", "intern", "employ", "paid"],
        "debate": ["debate", "debating", "speech", "forum", "congress", "mock trial",
                   "model un"],
        "leadership_office": ["officer", "lead", "president", "captain", "role", "chair"],
        "service_nonprofit": ["volunteer", "service", "charity", "community", "group"],
        "athletics": ["sport", "tennis", "ping-pong", "team", "athletic", "racquet"],
        "arts_music": ["theat", "music", "drama", "stage", "musical", "perform"],
        "academics_floor": ["grade", "gpa", "course", "class", "subject", "test", "study",
                            "academic", "rigor", "rigour"],
        "olympiad_math": ["math", "olympiad", "competition math"],
        "research": ["research", "lab", "paper", "study"],
        "robotics_cs": ["robot", "coding", "program", "computer"],
    }

    def _in_plan(cred):
        """Is this credential built by something in the plan?

        `credential` arrives in two shapes: a domain slug ("service_nonprofit") from some
        runs, and a full descriptive sentence from others. The first version of this only
        handled the slug — it stripped spaces, turned a sentence into one giant token,
        matched nothing, and reported that the plan did not build credentials it plainly
        did. Both card_plan failures on the first real run were this. Thirteenth gate bug,
        and the schema is genuinely loose here, so handle both. [#67]
        """
        raw = str(cred or "").lower()
        slug = re.sub(r"[^a-z_]", "", raw)
        if slug in DOMAIN_WORDS:                      # a clean slug
            return any(w in plan_text for w in DOMAIN_WORDS[slug])
        words = [w for w in re.findall(r"[a-z]{4,}", raw)]
        if not words:
            return False
        # A sentence: match if it names a domain we know, or shares distinctive words with
        # the plan. Two hits, so one incidental word does not carry it.
        for dom, dw in DOMAIN_WORDS.items():
            # The SAME word must appear in both. Matching on "any word of this domain"
            # let a research-paper credential pass because the plan's academic tasks
            # contain the word "study" — a control that failed to fire the moment it was
            # written, which is exactly why every gate here gets a negative test. [#67]
            shared = [w for w in dw if w in raw and w in plan_text]
            if shared:
                return True
        STOP = {"with", "that", "this", "from", "into", "what", "when", "where", "which",
                "already", "through", "about", "their", "these", "those", "runs", "year",
                "school", "grade", "note", "short", "where", "does", "only", "just"}
        distinctive = [w for w in words if w not in STOP]
        return sum(w in plan_text for w in distinctive) >= 2

    # 1. CARD -> PLAN. A credential the card promises that no goal produces is the card
    #    describing a student this plan does not build.
    orphans = [str(a.get("credential") or a) for a in prof
               if isinstance(a, dict) and a.get("credential")
               and "capacity" not in str(a.get("credential")).lower()
               and not _in_plan(a.get("credential"))]
    if orphans:
        f.append(f"the card promises {orphans[:3]} and no goal in the plan produces "
                 f"{'it' if len(orphans) == 1 else 'them'}")

    # 2. PLAN -> CARD. A domain the plan works on for five years and the card never shows
    #    is the reverse failure, and it is the one that actually happened: the plan carried
    #    an academic goal in every grade and the card had no academics entry at all.
    card_text = _txt(two_paths).lower()
    worked_on = set()
    for _, t, go in rows:
        body = (t + " " + _txt(go.get("tasks") or [])).lower()
        for dom, words in DOMAIN_WORDS.items():
            if sum(w in body for w in words) >= 1:
                worked_on.add(dom)
    missing = sorted(d for d in worked_on
                     if not any(w in card_text for w in DOMAIN_WORDS[d])
                     and d not in card_text)
    if missing:
        f.append(f"the plan works on {missing[:3]} across the years and the card never "
                 f"shows {'it' if len(missing) == 1 else 'them'}")

    # 2b. THE CARD'S ACADEMIC BLOCK MUST BE THE PLAN'S ACADEMIC WORK. [#67]
    #     Academics does not live in `achievement_profile` — the card carries it in its own
    #     course-targets block — so the domain check above passes on a card whose academic
    #     statement is stale. That is precisely the failure that prompted this gate: the
    #     card said grade eight was for choosing courses well, while the plan had moved on
    #     to finding the weak subjects and fixing them. Absence is easy to spot; a stale
    #     sentence that still reads plausibly is not, and it is the more common defect.
    acad_goals = [t for _, t, go in rows
                  if re.search("|".join(DOMAIN_WORDS["academics_floor"]),
                               t + " " + _txt(go.get("tasks") or []), re.I)]
    card_acad = _txt(tgt.get("course_targets") or tgt.get("academics") or "").lower()
    if acad_goals and card_acad:
        # The card should echo what the plan's academic goals actually say. Compare on
        # distinctive words, not phrasing.
        STOP = {"grade", "school", "high", "year", "course", "courses", "class", "classes",
                "taken", "this", "that", "with", "from", "they", "them", "their", "than"}
        plan_words = {w for g in acad_goals
                      for w in re.findall(r"[a-z]{5,}", g.lower()) if w not in STOP}
        if plan_words and not (plan_words & set(re.findall(r"[a-z]{5,}", card_acad))):
            f.append("the card's academic block shares no substance with the plan's "
                     "academic goals — one of them has moved and the other has not")
    elif acad_goals and not card_acad:
        f.append("the plan carries academic goals and the card states no academic "
                 "position at all")

    # 3. A stretch card must still be the same student as the target card, measured
    #    against the plan rather than against itself.
    st = (two_paths or {}).get("stretch_variant") or {}
    added = [a for a in (st.get("achievement_profile") or [])
             if isinstance(a, dict) and a.get("via") == "added"]
    unplanned = [str(a.get("credential")) for a in added if not _in_plan(a.get("credential"))]
    if unplanned:
        f.append(f"the stretch card adds {unplanned[:2]}, which the plan never schedules "
                 f"— a stretch is a harder version of this plan, not a different one")

    return GateResult("card_plan", RETRY if f else PASS, f,
                      "the card and the plan are describing different students"
                      if f else "")
