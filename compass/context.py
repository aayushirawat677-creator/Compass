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


def for_gap(profile):
    """Gap analysis needs to know which signals actually separate admits."""
    return {"findings": data_access.findings_for(_track_of(profile))}


def for_strategy(profile):
    """Strategy needs the findings AND the real competitive ladder, so it can
    aim at a named level instead of inventing one."""
    return {"findings": data_access.findings_for(_track_of(profile)),
            "debate_circuits": data_access.circuits_for(_state_of(profile))}


def for_recs(profile, task=None):
    """Recommendations need an actual catalog, filtered to what this family can use."""
    cat = data_access.load_catalog()
    if cat is None:
        rows = []
    elif hasattr(cat, "to_dict"):          # pandas DataFrame
        rows = cat.fillna("").to_dict("records")
    else:
        rows = list(cat)
    cons = profile.get("constraints") or {}
    state = _state_of(profile)
    if state:
        rows = [r for r in rows
                if not str(r.get("state") or "").strip()
                or str(r.get("state")).strip().upper() == state]
    return {"catalog": rows,
            "constraints": cons,
            "debate_circuits": data_access.circuits_for(state),
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
