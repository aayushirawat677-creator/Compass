"""
THE PROGRAM / COMPETITION REGISTRY.

One question this answers: "what could this kid actually do, and what is the next
rung up?" — for any activity, not just debate.

Shape of the thing:

    data/sources.json   the registry: every database we draw on, what it covers,
                        which adapter turns it into rows, and what is still missing
    data/programs.csv   the common schema every source resolves to
    ADAPTERS (below)    one small function per source whose raw shape differs

Adding a new competition database is: drop the file in data/, add an entry to
sources.json, and — only if its columns differ — add an adapter here. No step,
prompt or gate changes.

THE LADDER is the load-bearing part. Step 6 (Two Paths) builds a stretch path by
INTENSIFY: same activity, next rung up. That only works if every source maps its
levels onto the same ordered six:

    school -> district -> regional -> state -> national -> international

A source that invents a seventh rung silently breaks the stretch logic, so the
loader drops unknown levels to blank rather than passing them through.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import settings

LADDER = ["school", "district", "regional", "state", "national", "international"]

FIELDS = ["program_id", "name", "org", "activity", "kind", "level", "selection",
          "format", "city", "state", "country", "age_min", "age_max",
          "grade_min", "grade_max", "season", "deadline_note", "cost_usd",
          "cost_note", "contact", "url", "source_id", "verified_on", "notes"]

_SOURCES = None
_PROGRAMS = None


def _path(name, default):
    return getattr(settings, name, os.path.join(settings.DATA_DIR, default))


# ---------------------------------------------------------------- registry ---
def sources(refresh=False):
    """The registry itself. Callers read `status` — a planned source is a known
    gap, not a failure, and should be reported as such rather than hidden."""
    global _SOURCES
    if _SOURCES is None or refresh:
        path = _path("SOURCES_JSON", "sources.json")
        try:
            with open(path, encoding="utf-8") as fh:
                _SOURCES = json.load(fh)
        except Exception:
            _SOURCES = {"sources": [], "ladder": LADDER, "activities": []}
    return _SOURCES


def active_sources():
    return [s for s in sources().get("sources", []) if s.get("status") == "active"]


def planned_sources():
    return [s for s in sources().get("sources", []) if s.get("status") == "planned"]


# ---------------------------------------------------------------- adapters ---
def _blank():
    return {k: "" for k in FIELDS}


def _adapt_programs_csv(src):
    """Rows already in the common schema."""
    path = os.path.join(settings.DATA_DIR, src.get("file") or "programs.csv")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for raw in csv.DictReader(fh):
            row = _blank()
            for k in FIELDS:
                row[k] = (raw.get(k) or "").strip()
            row["source_id"] = row["source_id"] or src["id"]
            out.append(row)
    return out


def _adapt_tabroom(src):
    """Tabroom's circuit inventory -> program rows.

    A circuit is a competition ladder, not a program you sign up for, so each row
    is kind='circuit'. The tournament count says how LIVE a circuit is; it ranks
    circuits and never becomes a claim about the student.
    """
    path = os.path.join(settings.DATA_DIR, src.get("file") or "tabroom_circuits.csv")
    if not os.path.exists(path):
        return []
    national_abbr = {"NSDA", "NatCir", "TOC-UK", "NIETOC"}
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for raw in csv.DictReader(fh):
            abbr = (raw.get("Abbr") or "").strip()
            name = (raw.get("Circuit Name") or "").strip()
            locale = (raw.get("Locale") or "").strip().upper()
            if not name:
                continue
            try:
                n = int(str(raw.get("2026-2027 Tournaments", "") or 0).strip() or 0)
            except ValueError:
                n = 0
            level = "national" if (locale == "US" or abbr in national_abbr) else "state"
            row = _blank()
            row.update({
                "program_id": f"tabroom-{(abbr or name).lower().replace(' ', '-')}",
                "name": name, "org": abbr or "Tabroom", "activity": "debate",
                "kind": "circuit", "level": level, "selection": "open",
                "format": "in_person", "state": "" if locale == "US" else locale,
                "country": "US", "season": "school year",
                "source_id": src["id"], "verified_on": src.get("verified_on", ""),
                "notes": f"{n} tournaments in 2026-27" if n else "",
            })
            row["_activity_count"] = n          # ranking only, never shown
            out.append(row)
    return out


ADAPTERS = {
    "programs_csv": _adapt_programs_csv,
    "tabroom": _adapt_tabroom,
}


# ------------------------------------------------------------------ loading --
def load(refresh=False):
    """Every active source, resolved into the common schema."""
    global _PROGRAMS
    if _PROGRAMS is not None and not refresh:
        return _PROGRAMS
    rows = []
    for src in active_sources():
        fn = ADAPTERS.get(src.get("adapter"))
        if not fn:
            continue
        try:
            rows.extend(fn(src))
        except Exception:
            continue                            # one bad source never kills a run
    for r in rows:
        if r.get("level") not in LADDER:
            r["level"] = ""                     # unknown rung -> no rung
    _PROGRAMS = rows
    return rows


def _num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def _fits_grade(row, grade):
    g = _num(grade)
    if g is None:
        return True
    lo, hi = _num(row.get("grade_min")), _num(row.get("grade_max"))
    if lo is not None and g < lo:
        return False
    if hi is not None and g > hi:
        return False
    # sources that state ages instead of grades: US grade + 5 ≈ age, stated either way
    alo, ahi = _num(row.get("age_min")), _num(row.get("age_max"))
    if alo is not None or ahi is not None:
        age = g + 5
        if alo is not None and age < alo - 1:
            return False
        if ahi is not None and age > ahi + 1:
            return False
    return True


def find(activity=None, state=None, grade=None, max_cost=None, level=None, limit=40):
    """Programs this student could actually do. Filters are all optional.

    A row with a blank state is national or school-based and stays in; a row with
    a different state is dropped. Cost filtering keeps rows with no stated cost —
    unknown is not the same as unaffordable, and the guardrail checks it later.
    """
    rows = load()
    act = (activity or "").strip().lower()
    st = (state or "").strip().upper()
    if act:
        rows = [r for r in rows if (r.get("activity") or "").lower() == act]
    if st:
        rows = [r for r in rows if not r.get("state") or r["state"].upper() == st]
    if level:
        rows = [r for r in rows if r.get("level") == level]
    rows = [r for r in rows if _fits_grade(r, grade)]
    if max_cost is not None:
        keep = []
        for r in rows:
            c = _num(r.get("cost_usd"))
            if c is None or c <= max_cost:
                keep.append(r)
        rows = keep
    rows.sort(key=lambda r: (-(r.get("_activity_count") or 0), r.get("name", "")))
    return [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows[:limit]]


def ladder(activity, state=None, grade=None, per_rung=4):
    """The rungs, in order, with what is available on each — the input Step 6
    needs to INTENSIFY a credential (same activity, next rung up).

    `next_rung` is what a student currently at rung X would climb to. Returning
    an empty rung is the honest answer and is better than inventing one: it tells
    the planner this activity has no verified path upward in our data yet.
    """
    rows = find(activity=activity, state=state, grade=grade, limit=500)
    rungs = {}
    for lvl in LADDER:
        rungs[lvl] = [r for r in rows if r.get("level") == lvl][:per_rung]
    return {
        "activity": activity,
        "rungs": rungs,
        "unplaced": [r for r in rows if not r.get("level")][:per_rung],
        "covered": [lvl for lvl in LADDER if rungs[lvl]],
        "note": ("Rungs with no entries are gaps in our data, not evidence that no "
                 "such competition exists. Do not promote a claim to a rung we "
                 "cannot name."),
    }


def next_rung(level):
    """The rung above `level`, or None at the top."""
    if level in LADDER and level != LADDER[-1]:
        return LADDER[LADDER.index(level) + 1]
    return None


def coverage():
    """What the registry can and cannot answer. Feeds the retrieval gate and the
    handoff doc — a thin activity should surface as DEGRADE, never as silence."""
    rows = load()
    by_activity = {}
    for r in rows:
        a = r.get("activity") or "other"
        by_activity[a] = by_activity.get(a, 0) + 1
    wanted = sources().get("activities", [])
    return {
        "rows": len(rows),
        "active_sources": [s["id"] for s in active_sources()],
        "by_activity": dict(sorted(by_activity.items(), key=lambda kv: -kv[1])),
        "no_data_for": [a for a in wanted if a not in by_activity],
        "planned_sources": [{"id": s["id"], "activities": s.get("activities", [])}
                            for s in planned_sources()],
    }


# ------------------------------------------------------- activity inference --
_ACTIVITY_WORDS = {
    "debate": ["debate", "forensics", "parli", "lincoln-douglas", "public forum", "congress"],
    "speech": ["speech", "oratory", "public speaking", "extemp"],
    "robotics": ["robot", "first tech", "ftc", "frc", "vex", "battlebot"],
    "math": ["math", "amc", "aime", "mathcounts", "olympiad problem"],
    "science_research": ["science fair", "research", "lab", "biology", "chemistry", "physics", "isef"],
    "computer_science": ["coding", "code", "programming", "hackathon", "app", "usaco", "computer science"],
    "venture": ["business", "venture", "startup", "sell", "customer", "entrepreneur", "market"],
    "service": ["volunteer", "service", "food bank", "shelter", "nonprofit", "community"],
    "model_un": ["model un", "mun", "model united nations"],
    "writing": ["essay", "writing", "journalism", "newspaper", "poetry", "blog"],
    "arts": ["art", "design", "portfolio", "photography", "film"],
    "music": ["music", "orchestra", "band", "instrument", "choir"],
    "athletics": ["team sport", "soccer", "basketball", "track", "swim", "tennis"],
    "leadership": ["club president", "lead the", "found a club", "officer", "captain"],
}


def activity_of(text):
    """Best-guess activity for a task, or '' when nothing matches.

    A guess, explicitly: it chooses which slice of the registry to hand an agent.
    It never becomes a claim in the plan, and '' simply means 'search everything'.
    """
    t = (text or "").lower()
    best, hits = "", 0
    for act, words in _ACTIVITY_WORDS.items():
        n = sum(1 for w in words if w in t)
        if n > hits:
            best, hits = act, n
    return best


if __name__ == "__main__":
    import pprint
    pprint.pprint(coverage())
