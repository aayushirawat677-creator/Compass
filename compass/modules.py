"""
Deterministic steps — the ones that touch NUMBERS. Never call the LLM.
  - match_rank:   pull admit cards (intended + peers discovered from cards), rank, tally.
  - constraint_guardrail:  block anything outside the parents' constraints.
  - tiering:      seed the college list with tiers (published-rate aware where IPEDS is present).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import settings
from compass import data_access


# ---------------------------------------------------------------------------
# Step 3 — Match & Rank cards  (+ tally, + peer discovery, + thin-data escalation)
# ---------------------------------------------------------------------------
def match_rank(intended_colleges, major, projected_card):
    """Retrieve similar ADMITTED students.  [#30: this silently returned 0 for a while]

    Rewritten for the exploded application-level corpus (#23): the frame has literal
    `college` / `result` columns and `post_id` as the student key. The previous version
    referenced `student_id` and a `result` containing "accept" — neither existed after
    the explode, so it returned zero cards on a 30,414-row corpus, and the pipeline
    carried on with mock cards. The retrieval gate now catches that; this fixes it.
    """
    df = data_access.load_corpus()
    if df is None:
        out = _mock_cards()
        out["mock"] = True                      # so the gate can refuse it
        return out

    cols = settings.CORPUS_COLUMNS
    sid, majcol = cols["student_id"], cols["major"]
    admits = df[df["result"] == "admit"]

    # major bucket, mapped through the corpus' own labels
    want = {k for k, v in getattr(settings, "MAJOR_TRACKS", {}).items()
            if v and major and (v in str(major).lower() or str(major).lower() in v)}
    if want and majcol in admits.columns:
        admits = admits[admits[majcol].isin(want)] if len(admits[admits[majcol].isin(want)]) else admits

    intended = [c.lower().strip() for c in (intended_colleges or []) if c]
    if intended:
        primary = admits[admits["college"].astype(str).str.lower().apply(
            lambda c: any(i in c or c in i for i in intended))]
    else:
        primary = admits.head(0)

    # peer discovery: the other colleges those same admits also got into
    ids = set(primary[sid])
    also = admits[admits[sid].isin(ids)]
    peer_names = sorted(set(also["college"].astype(str)) - set(intended_colleges or []))
    peers = also[~also["college"].isin(intended_colleges or [])]

    cards = _concat(primary, peers)
    escalate = primary[sid].nunique() < settings.MIN_ADMITS_PER_SCHOOL
    return {"cards": cards.head(50).to_dict("records"),
            "tally": _tally(cards),
            "n_students": int(cards[sid].nunique()) if len(cards) else 0,
            "peers_discovered": peer_names[:15],
            "escalate_thin_data": bool(escalate)}


def _concat(a, b):
    import pandas as pd
    return pd.concat([a, b]).drop_duplicates()


def _tally(cards):
    """Deterministic counts over the retrieved admits. GPA/test are BANDS in this
    corpus (#23), so report the modal band and its share — never a fabricated mean."""
    import pandas as pd
    n = len(cards)
    if not n:
        return {"n_cards": 0, "n_students": 0}
    cols = settings.CORPUS_COLUMNS
    out = {"n_cards": int(n), "n_students": int(cards[cols["student_id"]].nunique())}
    for key in ("gpa", "test"):
        c = cols.get(key)
        if c and c in cards.columns:
            vc = cards.drop_duplicates(subset=[cols["student_id"]])[c]
            vc = vc[vc.astype(str).str.strip() != ""].value_counts()
            if len(vc):
                out[f"{key}_modal_band"] = str(vc.index[0])
                out[f"{key}_modal_share"] = round(float(vc.iloc[0] / vc.sum()), 2)
                out[f"{key}_n"] = int(vc.sum())
    if "college" in cards.columns:
        out["top_colleges"] = [str(k) for k in cards["college"].value_counts().head(5).index]
    return out


def _mock_cards():
    return {"cards": [
        {"college": "MIT", "result": "accepted", "major": "CS", "gpa": "3.95",
         "activities": "national robotics; research project", "awards": "national"},
        {"college": "MIT", "result": "accepted", "major": "CS", "gpa": "4.0",
         "activities": "research paper; robotics club lead", "awards": "state"},
        {"college": "Carnegie Mellon", "result": "accepted", "major": "CS", "gpa": "3.9",
         "activities": "robotics + independent build", "awards": "regional->national"},
    ],
        "tally": {"n_cards": 3, "gpa_range": [3.9, 4.0], "had_research": "7 of 10", "had_national_result": "6 of 10"},
        "peers_discovered": ["carnegie mellon", "caltech", "stanford"],
        "escalate_thin_data": False}


# ---------------------------------------------------------------------------
# Step 6c — Constraint Guardrail  (deterministic; nothing leaks past constraints)
# ---------------------------------------------------------------------------
def constraint_guardrail(recommendation, constraints):
    """Return (ok, violations[]). Blocks over-budget / out-of-area / hard-no items."""
    violations = []
    budget = _money(constraints.get("budget"))
    options = recommendation.get("options", [])
    if recommendation.get("single_action"):
        options = [recommendation["single_action"]]
    for opt in options:
        cost = opt.get("cost_usd")
        if budget is not None and isinstance(cost, (int, float)) and cost > budget:
            violations.append(f"'{opt.get('name')}' costs ${cost} > budget ${budget}")
        # Location: only flag when the option carries an explicit out-of-area location.
        loc = str(opt.get("location", "")).lower()
        in_state_only = "state" in str(constraints.get("location_radius", "")).lower() \
            or any("out of state" in h.lower() or "out-of-state" in h.lower()
                   for h in constraints.get("hard_nos", []))
        if loc and in_state_only and ("out of state" in loc or "abroad" in loc or "overseas" in loc):
            violations.append(f"'{opt.get('name')}' is out of the allowed area ({loc}) — needs human confirm")
    return (len(violations) == 0, violations)


def _money(s):
    if not s:
        return None
    import re
    m = re.search(r"([\d,]+)", str(s))
    return float(m.group(1).replace(",", "")) if m else None


# ---------------------------------------------------------------------------
# Step 6d — College tiering seed  (numbers come from here, not the writer)
# ---------------------------------------------------------------------------
def tiering(intended_colleges, college_seed):
    """Attach a published-rate hint to each seed college where IPEDS is available."""
    out = []
    for c in college_seed:
        name = c["college"] if isinstance(c, dict) else c
        rate = data_access.ipeds_published_rate(name)
        row = dict(c) if isinstance(c, dict) else {"college": name}
        if rate is not None:
            row["published_admit_rate"] = round(rate, 3)
        out.append(row)
    return out


try:
    import pandas as pd
except Exception:
    pd = None


# ===========================================================================
# APPLICATION-LEVEL OUTCOME RATES  [feedback log #18]
# ===========================================================================
# THE KEY IDEA: the unit of analysis is an APPLICATION, not a student.
# One student legitimately appears as an admit at some schools and a deny at
# others. That is not mixed-up data — it is what gives us a denominator.
#
#   "What does an admit look like?"        -> admits only   (credentials, stats)
#   "How often does someone like this      -> admits + denies (a real rate)
#    get in HERE?"
#
# Never answer the second question from admits-only rows, and never answer the
# first from the mixed pool.

ADMIT_RESULTS = {"accepted", "admitted", "accept", "admit", "enrolled", "likely"}
DENY_RESULTS  = {"rejected", "denied", "reject", "deny"}
OTHER_RESULTS = {"waitlisted", "deferred", "waitlist", "defer", "withdrew"}


def _bucket(result):
    r = str(result or "").strip().lower()
    if r in ADMIT_RESULTS: return "admit"
    if r in DENY_RESULTS:  return "deny"
    if r in OTHER_RESULTS: return "other"
    return "unknown"


def cohort_rates(corpus_df, cohort_student_ids, cols, min_decisions=20):
    """Real admit rates for a matched cohort, computed per college.

    corpus_df          : the full application-level corpus
    cohort_student_ids : student ids of the matched (similar) students
    cols               : settings.CORPUS_COLUMNS
    min_decisions      : suppress any college with fewer decisions than this

    Returns {college: {admits, denies, other, decisions, rate, band, sufficient}}
    'rate' is the rate WITHIN THIS COHORT IN OUR DATA — not the school's
    published rate, and not an individual's probability. Label it that way.
    """
    sid, col, res = cols["student_id"], "college", "result"
    df = corpus_df[corpus_df[sid].isin(set(cohort_student_ids))].copy()
    df = df.drop_duplicates(subset=[sid, col])
    df["_b"] = df[res].map(_bucket)

    out = {}
    for college, g in df.groupby(col):
        admits = int((g["_b"] == "admit").sum())
        denies = int((g["_b"] == "deny").sum())
        other  = int((g["_b"] == "other").sum())
        decisions = admits + denies          # 'other' is excluded from the rate
        row = {"admits": admits, "denies": denies, "other": other,
               "decisions": decisions, "rate": None, "band": None,
               "sufficient": decisions >= min_decisions}
        if row["sufficient"]:
            rate = admits / decisions
            row["rate"] = round(rate, 3)
            row["band"] = ("Likely"    if rate >= 0.60 else
                           "Target"    if rate >= 0.35 else
                           "Reach"     if rate >= 0.15 else
                           "Far Reach")
        out[str(college)] = row
    return out


def admit_pattern(corpus_df, cohort_student_ids, cols, college=None):
    """Credential frequencies and stat ranges among ADMITS only.

    This is the 'what does an admit look like' question, so denies are
    correctly excluded here. Always returns n so the card can cite it.
    """
    sid = cols["student_id"]
    df = corpus_df[corpus_df[sid].isin(set(cohort_student_ids))].copy()
    if college:
        df = df[df["college"].astype(str) == str(college)]
    df = df[df["result"].map(_bucket) == "admit"].drop_duplicates(subset=[sid])

    # GPA and test are BANDS in this corpus ("3.8+", "1500+/34+"), never numbers.
    # Report the distribution and the modal band; never invent a median.
    stats = {}
    for key in ("gpa", "test"):
        c = cols.get(key)
        if c and c in df.columns:
            vc = df[c].replace("", pd.NA).dropna().value_counts()
            if len(vc):
                stats[key] = {"modal_band": vc.index[0],
                              "distribution": {k: int(v) for k, v in vc.head(6).items()},
                              "n": int(vc.sum())}
    return {"n_admits": int(df[sid].nunique()), "stats": stats,
            "note": "GPA/test are bands as recorded in the corpus, not computed numbers."}


# ===========================================================================
# PER-SCHOOL ADMIT PATTERN  [#44]
# ===========================================================================
# Two Paths was handed one corpus-wide tally — 67 students across six schools —
# and asked to assess fit per school. It correctly refused, and every school came
# back "not assessed". That is a wiring failure, not a prompt failure: the step was
# never given the thing it needs. This computes, for each named school:
#   - how many admits we actually hold for it (the n that makes fit assertable)
#   - the GPA / test bands those admits sat in
#   - how often a given credential type appears among them, so a plan can be
#     calibrated against what admits really did rather than against a guess.
#
# It answers the calibration question directly: for THIS spike, at THIS school,
# what level did admits reach? Aim at the middle of that distribution, not the tail.

CREDENTIAL_PATTERNS = {
    "debate":            r"\bdebate|forensics|NSDA|policy debate|lincoln.?douglas|public forum",
    "research":          r"\bresearch|published|paper|lab\b|ISEF|Regeneron|science fair",
    "venture":           r"\bstartup|business|founded|company|entrepreneur|sold\b|revenue",
    "olympiad_math":     r"\bAMC|AIME|USAMO|olympiad|MATHCOUNTS",
    "robotics_cs":       r"\brobotics|FRC|FTC|USACO|hackathon|\bcoding\b",
    "service_nonprofit": r"\bnonprofit|volunteer|service|founded a club|charity",
    "arts_music":        r"\bmusic|orchestra|art\b|film|theater|theatre|dance",
    "athletics":         r"\bvarsity|captain|recruit|state champion|athlet",
    "leadership_office": r"\bpresident|captain|editor.in.chief|founder|led\b",
    "work_internship":   r"\binternship|intern\b|job\b|employed",
}

# The rungs a credential can reach, weakest first. Same vocabulary as the
# program registry's ladder, so a plan can say "aim one rung above where he is".
LEVEL_PATTERNS = [
    ("international", r"\bTOC\b|Tournament of Champions|world schools|international olympiad|IMO\b|ISEF"),
    ("national",      r"\bnationals?\b|national qualifier|national champion|USAMO|USACO platinum"),
    ("state",         r"\bstate (qualifier|champ|final|tournament|semi)|qualified for state|\bstates\b|all.state"),
    ("regional",      r"\bregional|district\b|county\b|sectional"),
    ("school",        r"\bcaptain\b|\bclub\b|school team|varsity"),
]


def admit_pattern_by_school(intended_colleges, major, min_admits=None):
    """Per-school credential and level distribution among admits.

    Returns one record per college, plus `sufficient` so the step downstream can
    tell the difference between "we looked and this is what admits showed" and
    "we do not hold enough admits for this school to say anything". An honest
    `sufficient: false` with its n beats a fabricated percentage.
    """
    import re as _re
    df = data_access.load_corpus()
    if df is None:
        return {"schools": [], "mock": True}
    raw = data_access.load_corpus(applications=False)
    cols = settings.CORPUS_COLUMNS
    sid = cols["student_id"]
    floor = min_admits or getattr(settings, "MIN_ADMITS_PER_SCHOOL", 5)
    admits = df[df["result"] == "admit"]

    # one text blob per student, so a credential is counted once per person
    text_by_id = {}
    if raw is not None:
        body = raw.get("post_body")
        title = raw.get("title")
        for pid, b, t in zip(raw[sid], body if body is not None else raw[sid],
                             title if title is not None else raw[sid]):
            text_by_id[pid] = f"{b} {t}".lower()

    out = []
    for college in (intended_colleges or []):
        hits = admits[admits["college"].astype(str).str.contains(
            _re.escape(str(college)), case=False, na=False)]
        ids = sorted(set(hits[sid]))
        n = len(ids)
        texts = [text_by_id.get(i, "") for i in ids]

        creds = {}
        for name, pat in CREDENTIAL_PATTERNS.items():
            who = [t for t in texts if _re.search(pat, t, _re.I)]
            if not who:
                continue
            # Read the level from the WINDOW AROUND the credential, not from the
            # whole post. Scanning the post finds "National Honor Society" and
            # "international student" and calls every credential national — which
            # is how a calibration number becomes confidently wrong. [#44]
            levels = {}
            for t in who:
                lvl = _level_near(t, pat)
                if lvl:
                    levels[lvl] = levels.get(lvl, 0) + 1
            creds[name] = {
                "n": len(who),
                "share_of_admits": round(len(who) / n, 3) if n else None,
                "levels": dict(sorted(levels.items(), key=lambda kv: -kv[1])),
                "modal_level": max(levels, key=levels.get) if levels else None,
            }

        out.append({
            "college": college,
            "n_admits_held": n,
            "sufficient": n >= floor,
            "gpa_band": _modal(hits, cols.get("gpa")),
            "test_band": _modal(hits, cols.get("test")),
            "credentials": dict(sorted(creds.items(), key=lambda kv: -kv[1]["n"])),
        })
    return {
        "schools": out,
        "floor": floor,
        "note": ("Counts are admits we hold, not admits that exist. A credential's "
                 "modal level is what admits who had it typically reached — aim there, "
                 "not at the tail. Shares describe admits only and are never an "
                 "admission rate."),
    }


_LEVEL_NOISE = _RE_NOISE = (
    r"national honor society|nhs\b|national merit|nationality|international student|"
    r"international baccalaureate|\bIB\b|internationally")


def _level_near(text, credential_pattern, window=140):
    """The rung a credential reached, read from the text around that credential."""
    import re as _re
    for m in _re.finditer(credential_pattern, text, _re.I):
        lo, hi = max(0, m.start() - window), min(len(text), m.end() + window)
        span = text[lo:hi]
        span = _re.sub(_LEVEL_NOISE, " ", span, flags=_re.I)
        for lvl, lpat in LEVEL_PATTERNS:
            if _re.search(lpat, span, _re.I):
                return lvl
    return None


def _modal(frame, col):
    if not col or col not in getattr(frame, "columns", []) or not len(frame):
        return None
    vals = frame[col].astype(str).str.strip()
    vals = vals[vals != ""]
    if not len(vals):
        return None
    top = vals.value_counts()
    return {"band": top.index[0], "share": round(float(top.iloc[0] / len(vals)), 3),
            "n": int(len(vals))}


# ===========================================================================
# CAPACITY BUDGET  [#47]
# ===========================================================================
# A plan that does not fit the week is not a plan. Goals are added against a
# real hour budget, computed from the day rather than guessed, and the budget
# shrinks every year as homework grows — which is why a plan that fits in
# grade 8 can quietly become impossible by grade 11.
#
# Per weekday, in hours. Sources are guidelines, not measurements, so they are
# stated here rather than buried: sleep is the recommended range for the age
# band; homework follows the standard ten-minutes-per-grade-per-night rule;
# school includes commute.
# Teens need 8-10 hours at every one of these ages, so sleep does NOT shrink to
# make room. Holding it flat is also what makes the budget tighten year on year:
# homework grows and nothing else gives. An earlier version tapered sleep, which
# cancelled the homework growth exactly and made the budget look flat - a claim
# the numbers did not support.
SLEEP_BY_GRADE = {7: 9.0, 8: 9.0, 9: 9.0, 10: 9.0, 11: 9.0, 12: 9.0}
SCHOOL_DAY = 7.5                      # instruction + commute
MEALS_AND_DOWNTIME = 3.0              # meals, family, unstructured rest
WEEKEND_ACTIVITY_HOURS = 6.0          # per weekend day, outside school terms' weekdays
SUMMER_WEEKLY_HOURS = 45.0            # no school, no homework: a different pool entirely


def _homework_hours(grade):
    """Ten minutes per grade per night, the standard guideline."""
    try:
        g = int(str(grade).strip()[:2].rstrip('th').rstrip('rd').rstrip('nd') or 8)
    except ValueError:
        g = 8
    return max(0.0, min(g, 12) * 10 / 60.0)


def capacity_budget(profile, grade, season="school_year"):
    """Hours a week actually available for activities, and what is already spent.

    `committed` is read from the profile's own activity hours, so subtracting a
    low-value activity returns its hours to the budget — a subtraction is a real
    planning move, not a cosmetic one. Returns `free_hours_per_week`, which is
    the ceiling any NEW goal has to fit inside.
    """
    try:
        g = int(str(grade).strip()[:2].rstrip('th').rstrip('rd').rstrip('nd') or 8)
    except ValueError:
        g = 8
    sleep = SLEEP_BY_GRADE.get(g, 9.0)
    hw = _homework_hours(g)

    if season == "summer":
        total = SUMMER_WEEKLY_HOURS
        basis = (f"summer: no school and no homework, about {SUMMER_WEEKLY_HOURS:.0f} h/week "
                 "of usable time. This is why the big commitments live here.")
    else:
        weekday = max(0.0, 24 - sleep - SCHOOL_DAY - hw - MEALS_AND_DOWNTIME)
        total = weekday * 5 + WEEKEND_ACTIVITY_HOURS * 2
        basis = (f"grade {g}: {sleep:.1f} h sleep, {SCHOOL_DAY:.1f} h school and commute, "
                 f"{hw:.1f} h homework, {MEALS_AND_DOWNTIME:.1f} h meals and downtime "
                 f"leaves {weekday:.1f} h on a weekday, plus {WEEKEND_ACTIVITY_HOURS:.0f} h "
                 f"a weekend day.")

    committed, unknown = 0.0, []
    for a in (profile.get("activities") or []):
        sig = a.get("signals") or a if isinstance(a, dict) else {}
        h = sig.get("hours_per_week") or (a.get("hours_per_week") if isinstance(a, dict) else None)
        lo = _hours_number(h)
        if lo is None:
            unknown.append(a.get("name") if isinstance(a, dict) else str(a))
        else:
            committed += lo

    free = round(total - committed, 1)
    return {
        "grade": g,
        "season": season,
        "total_hours_per_week": round(total, 1),
        "committed_hours_per_week": round(committed, 1),
        "free_hours_per_week": free,
        "activities_without_stated_hours": unknown,
        "basis": basis,
        "note": ("free_hours_per_week is the ceiling for anything NEW. Dropping an activity "
                 "returns its hours here. Homework grows about 10 minutes per grade per "
                 "night, so this budget tightens every year — a plan that fits now can stop "
                 "fitting by grade 11."),
    }


def _hours_number(h):
    """'4-6' -> 6 (plan against the top of a stated range, never the bottom)."""
    import re as _re
    if h is None:
        return None
    nums = [float(x) for x in _re.findall(r"\d+(?:\.\d+)?", str(h))]
    return max(nums) if nums else None


def stage_bands(current_grade):
    """The three stages, relative to where the student is now. [#48]

    Solidify is always grade 10 and Specialize is always 11-12; Explore is
    however many years remain before that. A grade 7 student explores for three
    years; a grade 9 student explores for one.
    """
    try:
        g = int(str(current_grade).strip()[:2].rstrip('th').rstrip('rd').rstrip('nd') or 8)
    except ValueError:
        g = 8
    bands = []
    if g <= 9:
        bands.append({"name": "Explore", "grades": list(range(g, 10)), "color": "g"})
    if g <= 10:
        bands.append({"name": "Solidify", "grades": [10], "color": "p"})
    bands.append({"name": "Specialize", "grades": [x for x in (11, 12) if x >= g], "color": ""})
    return [b for b in bands if b["grades"]]


# ===========================================================================
# BUDGET LEDGER  [#51]
# ===========================================================================
# constraint_guardrail checks ONE recommendation against the constraints. That is
# not enough: four options can each sit inside a $5,000 ceiling and total $8,000.
# Nobody was adding them up. This does, per year, and it enforces geography at the
# same time — an in-person programme outside the family's stated radius is not
# cheaper for being affordable.

_ONLINE = ("online", "virtual", "remote", "hybrid")


def budget_ledger(recommendations, constraints, season_field="term"):
    """Total the year's recommendations against the family's stated ceiling.

    Returns `within_budget` and, when it is false, the items to drop in priority
    order — cheapest-first is wrong here, so it surfaces the most expensive items
    and lets the planner decide. Also returns geographic rejections separately,
    because those are not a money problem and cannot be solved by dropping something
    else.
    """
    # A stated range is a ceiling at its TOP. "$2,000-$5,000" means they can go to
    # $5,000, not that $2,001 is a breach.
    ceiling = _ceiling(constraints.get("activities_budget")
                       or constraints.get("budget_activities_per_year"))
    summer_ceiling = _ceiling(constraints.get("summer_budget")
                              or constraints.get("summer_program_budget"))
    per_session_raw = (constraints.get("per_session_ceiling")
                       or constraints.get("per-session_cost_ceiling"))
    per_session = _ceiling(per_session_raw)
    state = str(constraints.get("location") or "").upper()
    allows_travel = not any(
        k in str(constraints.get("hard_nos") or constraints).lower()
        for k in ("travel-heavy", "out-of-region", "out of region", "travel heavy"))

    items, geo_blocked, session_blocked = [], [], []
    total = summer_total = 0.0
    for r in (recommendations or []):
        for opt in _rec_options(r):
            cost = _money(opt.get("cost") or opt.get("price") or opt.get("cost_usd"))
            name = opt.get("name") or r.get("task") or "recommendation"
            fmt = str(opt.get("format") or "").lower()
            loc = str(opt.get("state") or opt.get("location") or "").upper()
            is_online = any(w in fmt for w in _ONLINE)

            if loc and state and loc not in state and not is_online and not allows_travel:
                geo_blocked.append({"name": name, "location": loc,
                                    "why": "in person outside the family's stated region"})
                continue
            # A per-hour or per-session ceiling only compares against a per-hour or
            # per-session price. Measuring a $1,395 semester fee against a $100/hour
            # ceiling blocks a legitimate option for no reason.
            unit_priced = any(w in str(opt.get("cost") or opt.get("price") or "").lower()
                              for w in ("hour", "session", "class", "lesson", "/hr"))
            if (per_session is not None and cost is not None
                    and unit_priced and cost > per_session):
                session_blocked.append({"name": name, "cost": cost,
                                        "ceiling": per_session,
                                        "why": "above the per-session ceiling"})
                continue
            if cost:
                summer = "summer" in " ".join(
                    str(x) for x in (opt.get(season_field), r.get(season_field),
                                     opt.get("name"), r.get("task"))).lower()
                if summer:
                    summer_total += cost
                else:
                    total += cost
                items.append({"name": name, "cost": cost, "summer": summer})

    over = ceiling is not None and total > ceiling
    summer_over = summer_ceiling is not None and summer_total > summer_ceiling
    return {
        "year_total": round(total, 2),
        "year_ceiling": ceiling,
        "summer_total": round(summer_total, 2),
        "summer_ceiling": summer_ceiling,
        "within_budget": not (over or summer_over),
        "over_by": round(total - ceiling, 2) if over else 0,
        "summer_over_by": round(summer_total - summer_ceiling, 2) if summer_over else 0,
        "items": sorted(items, key=lambda x: -(x["cost"] or 0)),
        "geographically_blocked": geo_blocked,
        "above_session_ceiling": session_blocked,
        "note": ("Costed items only. An option with no stated price is not free — it is "
                 "unpriced, and a family cannot plan against it, so confirm it before "
                 "committing. Geographic blocks are not a money problem: dropping "
                 "something else does not make them possible."),
    }


def _ceiling(v):
    """The TOP of a stated money range, which is what a ceiling means."""
    import re as _re
    if v is None:
        return None
    nums = [float(x.replace(",", "")) for x in _re.findall(r"[\d,]+(?:\.\d+)?", str(v))]
    return max(nums) if nums else None


def _rec_options(r):
    """Every priced option inside a recommendation, whatever shape it came in."""
    if not isinstance(r, dict):
        return []
    out = []
    for key in ("recommendations", "options", "alternates"):
        v = r.get(key)
        if isinstance(v, list):
            out += [x for x in v if isinstance(x, dict)]
    for key in ("primary",):
        if isinstance(r.get(key), dict):
            out.append(r[key])
    return out or ([r] if r.get("cost") or r.get("price") else [])
