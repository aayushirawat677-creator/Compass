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
