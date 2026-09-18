"""
Context packs — the retrieval layer.  [feedback log #22]

Before this existed, every agent was called with only the previous step's JSON.
Tabroom and the findings report were not data sources at all, and plan_recs was
handed `catalog_json: []` on every run — which is why recommendations came back
as placeholders. An agent cannot use evidence it is never given.

Each pack assembles the slice of reference data THAT step needs, deterministically,
in Python. Nothing here asks a model to go find anything.
"""
from . import data_access
from . import programs


def _state_of(profile):
    loc = ((profile.get("constraints") or {}).get("location")
           or (profile.get("intended") or {}).get("location") or "")
    for token in str(loc).replace(",", " ").split():
        if len(token) == 2 and token.isalpha() and token.isupper():
            return token
    return "CA" if "california" in str(loc).lower() else ""


def _track_of(profile):
    intended = profile.get("intended") or {}
    major = str(intended.get("major") or intended.get("direction") or "").lower()
    for key, hit in [("business", "business"), ("finance", "business"),
                     ("law", "social_science"), ("public", "social_science"),
                     ("politic", "social_science"), ("social", "social_science"),
                     ("human", "humanities"), ("writ", "humanities"),
                     ("cs", "cs"), ("computer", "cs"), ("engineer", "stem_non_cs")]:
        if key in major:
            return hit
    return "social_science"


def _activities_of(profile):
    """Which registry activities this kid actually does, from the profile's own
    activity list. Empty means we have no named activity to climb — the planner
    should be told that rather than handed a debate ladder by default."""
    out, seen = [], set()
    for a in (profile.get("activities") or []):
        text = a if isinstance(a, str) else " ".join(str(v) for v in a.values())
        act = programs.activity_of(text)
        if act and act not in seen:
            seen.add(act)
            out.append(act)
    return out


def for_gap(profile):
    """Gap analysis needs to know which signals actually separate admits."""
    return {"findings": data_access.findings_for(_track_of(profile))}


def for_strategy(profile):
    """Strategy needs the findings AND the real competitive ladder, so it can
    aim at a named level instead of inventing one.

    The ladder comes from the program registry, so it is per-activity: whichever
    activities this kid actually does, not debate by assumption.
    """
    state = _state_of(profile)
    ladders = {a: programs.ladder(a, state) for a in _activities_of(profile)}
    return {"findings": data_access.findings_for(_track_of(profile)),
            "ladders": ladders,
            "registry_coverage": programs.coverage(),
            "debate_circuits": data_access.circuits_for(state)}   # legacy key


def for_recs(profile, task=None):
    """Recommendations need real programs, filtered to what this family can use.

    Sourced from the program registry (data/sources.json), so a new competition
    database becomes available to this step the moment it is registered — no
    change here. The activity is inferred from the task text only to choose which
    slice to hand over; it never becomes a claim.
    """
    cons = profile.get("constraints") or {}
    state = _state_of(profile)
    grade = (profile.get("cover") or {}).get("grade") or (profile.get("intended") or {}).get("grade")
    text = task if isinstance(task, str) else (task or {}).get("task_title") or str(task or "")
    activity = programs.activity_of(text)

    rows = programs.find(activity=activity, state=state, grade=grade)
    if not rows and activity:
        rows = programs.find(state=state, grade=grade)      # widen before giving up

    cov = programs.coverage()
    return {"catalog": rows,                                 # legacy key, new rows
            "programs": rows,
            "activity": activity,
            "ladder": programs.ladder(activity, state, grade) if activity else {},
            "constraints": cons,
            "sources": cov["active_sources"],
            "no_data_for": cov["no_data_for"],
            "debate_circuits": data_access.circuits_for(state),   # legacy key
            "coverage": bool(rows)}


def for_writer(profile, colleges=None):
    """Findings framing + PUBLISHED selectivity for each school on the list.
    Rates never come from the corpus (#24); anything missing is flagged for a
    live lookup rather than estimated (#25)."""
    pack = {"findings": data_access.findings_for(_track_of(profile))}
    if colleges:
        have, missing = {}, []
        for c in colleges:
            name = c.get("college") if isinstance(c, dict) else c   # seed rows are dicts
            r = data_access.selectivity_band(name)
            c = name
            (have.__setitem__(c, r) if r else missing.append(c))
        pack["published_rates"] = have
        pack["rates_not_on_hand"] = missing
        pack["rates_note"] = ("These are the schools' OWN published admit rates with their class "
                              "year — not this student's odds, and never from the corpus.")
    return pack
