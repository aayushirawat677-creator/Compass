"""
The activity-ceilings cache.  [#59]

The APPRAISER agent does the work — it searches, reads and judges every activity of every
student, every run.  This module is only the memory around it:

    lookup()   is there layer-1 knowledge about this TYPE of activity already?
    record()   write back what the agent learned, so the next family is cheaper.

The distinction the whole design rests on:

    LAYER 1 — the TYPE.  What a solo resale venture can reach, what transfers out of it,
              the routes students take.  Identical for every student who has one.
              Cacheable.  Reviewable by a human.  Lives in data/activity_ceilings.json.

    LAYER 2 — THIS STUDENT.  His grade, his two years in it, his hours, his six target
              schools.  Never cacheable.  Always the agent, every time.

So an empty cache is a normal state, not a blocked one: the engine runs fine on day one and
the file fills itself.  Nothing here decides anything — a cache that made judgments would be
a stale prompt with extra steps.
"""
import json
import os
import re
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(HERE, "data", "activity_ceilings.json")

LADDER = ["school", "district", "regional", "state", "national", "international"]

# Anything with dates, prices or programme names in it goes stale.  A ceiling reason does
# not, but we re-verify the whole entry rather than trying to age each field separately.
STALE_AFTER_DAYS = 548  # 18 months


def _load():
    try:
        with open(PATH) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"types": {}}


def _save(doc):
    tmp = PATH + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, PATH)


def slug(name):
    """A stable key for an activity TYPE.

    Deliberately crude.  The agent supplies `type_name`; this only normalises it, so two
    families whose agents wrote "Solo Resale Venture" and "solo resale venture" land on one
    entry instead of two.
    """
    s = re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")
    return s or "unknown"


def rung_index(rung):
    """Position on the shared ladder, or -1 for an unknown rung.

    Unknown is returned rather than guessed.  An empty rung means we have not established
    one, which is a different claim from establishing that it is low. [#59]
    """
    try:
        return LADDER.index(str(rung or "").strip().lower())
    except ValueError:
        return -1


def _age_days(entry):
    stamp = str(entry.get("verified_on") or "")
    try:
        t = time.mktime(time.strptime(stamp, "%Y-%m-%d"))
    except ValueError:
        return 10**6
    return (time.time() - t) / 86400.0


def lookup(type_name):
    """Layer-1 knowledge for this activity type, or None.

    Returns None on a miss AND on a stale hit, so the caller's path is the same either way:
    hand the agent whatever came back (possibly nothing) and let it search.
    """
    key = slug(type_name)
    entry = (_load().get("types") or {}).get(key)
    if not entry:
        return None
    if _age_days(entry) > STALE_AFTER_DAYS:
        return None
    return entry


def candidates(activity_text, limit=3):
    """Cheap pre-search: cached types whose words overlap the activity description.

    The agent names the type itself, but it names it better with a shortlist in hand — and
    without this, two families with the same activity phrased differently never share an
    entry.  Overlap only; no attempt to be clever.
    """
    words = set(re.findall(r"[a-z]{4,}", str(activity_text or "").lower()))
    if not words:
        return []
    scored = []
    for key, entry in (_load().get("types") or {}).items():
        blob = f"{key} {entry.get('what_it_is','')} {' '.join(entry.get('transfers_to') or [])}"
        overlap = words & set(re.findall(r"[a-z]{4,}", blob.lower()))
        if overlap:
            scored.append((len(overlap), key, entry))
    scored.sort(reverse=True, key=lambda r: r[0])
    return [e for _, _, e in scored[:limit]]


def record(type_knowledge):
    """Write back what the agent learned about the TYPE.

    Refuses anything that fails the layer separation or arrives without a source, because a
    cache entry nobody can trace is worse than a cache miss — the miss costs a search, the
    untraceable entry costs every future family the same wrong answer. [#59]

    Returns (ok, reason).
    """
    tk = dict(type_knowledge or {})
    name = tk.get("type_name")
    if not name:
        return False, "no type_name"
    if not (tk.get("sources") or []):
        return False, "no sources — an untraceable entry is worse than a miss"
    if not tk.get("ceiling_reason"):
        return False, "no ceiling_reason — a rung with no reason cannot be reviewed"

    # Layer separation, enforced rather than requested.
    #
    # The first version of this guard rejected the pronouns "his"/"her" and threw away all
    # five entries of the first real run — "a student carries his trading history into the
    # role" is generic prose, not a leak.  A pronoun is not a fact.  What actually betrays
    # a child is a FACT that could only be true of one student: a specific grade, a tenure,
    # an hours figure, a named school or city. [#59]
    blob = json.dumps(tk).lower()
    LEAKS = [
        (r"\bgrade \d+\b", "a specific grade"),
        (r"\b\d+(\.\d+)?\s*(-|to)?\s*\d*\s*(hours|hrs)\b", "an hours figure"),
        (r"\b(he|she|they) (has|have) (been )?(run|done|played|traded)", "this student's tenure"),
        (r"\bfor (the )?(past |last )?(one|two|three|four|five|\d+) years?\b", "a tenure"),
        (r"\b(berkeley|stanford|penn|georgetown|ucla|michigan|nyu)\b", "a named target school"),
    ]
    for pattern, what in LEAKS:
        if re.search(pattern, blob):
            return False, f"child-specific detail in type knowledge: {what}"

    doc = _load()
    doc.setdefault("types", {})
    key = slug(name)
    prior = doc["types"].get(key) or {}
    tk["type_name"] = key
    tk.setdefault("verified_on", time.strftime("%Y-%m-%d"))
    tk["seen_count"] = int(prior.get("seen_count") or 0) + 1
    doc["types"][key] = tk
    _save(doc)
    return True, "recorded"


def coverage():
    """What the cache currently holds — for the handoff doc and for a quick sanity check."""
    types = _load().get("types") or {}
    return {
        "types": len(types),
        "by_rung": {r: sum(1 for e in types.values()
                           if str(e.get("ceiling_rung", "")).lower() == r)
                    for r in LADDER},
        "unrated": sum(1 for e in types.values() if rung_index(e.get("ceiling_rung")) < 0),
        "stale": sum(1 for e in types.values() if _age_days(e) > STALE_AFTER_DAYS),
        "total_applications": sum(int(e.get("seen_count") or 0) for e in types.values()),
    }
