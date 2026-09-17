"""
Adapters over your real data. Everything reads paths + column names from settings.py.
If a file is missing (e.g. in the cloud test), the adapter falls back to a small mock set
so the pipeline still runs. Point settings.DATA_DIR at your Peggy folder for real data.
"""
import os, sqlite3, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import settings

try:
    import pandas as pd
except Exception:
    pd = None

_corpus_cache = None


def load_corpus(applications=True):
    """Load the verified corpus.

    THE FILE IS STUDENT-LEVEL: one row per Reddit post, with outcomes stored as
    "; "-separated college LISTS (accepted_colleges, rejected_colleges, ...).
    A student legitimately appears as an admit at some schools and a deny at
    others — that pairing is what supplies the denominator (#18).

    applications=True (default) explodes it into one row per (student, college,
    result), which is the only shape a rate may be computed from.
    """
    if pd is None or not os.path.exists(settings.CORPUS_CSV):
        return None
    cols = settings.CORPUS_COLUMNS
    df = pd.read_csv(settings.CORPUS_CSV, engine="python",
                     on_bad_lines="skip", dtype=str).fillna("")

    # row-quality gates: drop duplicates and unusable posts
    if cols["dedup"] in df.columns:
        df = df[df[cols["dedup"]].str.strip().str.lower() == "yes"]
    if cols["status"] in df.columns:
        df = df[df[cols["status"]].str.contains("Valid", case=False, na=False)]
    if not applications:
        return df

    sep = settings.COLLEGE_LIST_SEP
    keep = [cols[k] for k in ("student_id", "major", "gpa", "test") if cols[k] in df.columns]
    frames = []
    for result, col in (("admit", cols["accepted"]), ("deny", cols["rejected"]),
                        ("waitlist", cols["waitlisted"]), ("defer", cols["deferred"])):
        if col not in df.columns:
            continue
        sub = df[keep + [col]].copy()
        sub = sub[sub[col].str.strip() != ""]
        sub["college"] = sub[col].str.split(sep)
        sub = sub.explode("college")
        sub["college"] = sub["college"].str.strip()
        sub = sub[sub["college"] != ""]
        sub["result"] = result
        frames.append(sub.drop(columns=[col]))
    if not frames:
        return df
    out = pd.concat(frames, ignore_index=True)
    # one decision per (student, college) — a repeat must not inflate n
    return out.drop_duplicates(subset=[cols["student_id"], "college"])


def _sniff_semicolon(path):
    with open(path, "r", errors="ignore") as f:
        head = f.readline()
    return head.count(";") > head.count(",")


def ipeds_published_rate(college: str):
    """Published admit rate for a college from IPEDS, or None if unavailable."""
    if not os.path.exists(settings.IPEDS_SQLITE):
        return None
    try:
        con = sqlite3.connect(settings.IPEDS_SQLITE)
        # NOTE: adjust table/column to your IPEDS schema (e.g. ADM2024: APPLCN, ADMSSN)
        cur = con.execute(
            "SELECT ADMSSN*1.0/NULLIF(APPLCN,0) FROM ADM2024 "
            "JOIN institutions USING(UNITID) WHERE institutions.name LIKE ? LIMIT 1",
            (f"%{college}%",),
        )
        row = cur.fetchone()
        con.close()
        return float(row[0]) if row and row[0] is not None else None
    except Exception:
        return None


def load_catalog():
    if pd is None or not os.path.exists(settings.CATALOG_CSV):
        return None
    return pd.read_csv(settings.CATALOG_CSV, dtype=str)


# ===========================================================================
# REFERENCE SOURCES  [feedback log #22]
# Previously Tabroom and the findings report were not data sources at all —
# no setting, no loader, passed to no step. That is why an agent could never
# have used them however the prompt was worded.
# ===========================================================================

def load_circuits():
    """Tabroom circuit inventory: Abbr, Circuit Name, Locale, tournament count."""
    import csv, os
    path = settings.CIRCUITS_CSV
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            try:
                n = int(str(r.get("2026-2027 Tournaments", "") or 0).strip() or 0)
            except ValueError:
                n = 0
            rows.append({"abbr": (r.get("Abbr") or "").strip(),
                         "name": (r.get("Circuit Name") or "").strip(),
                         "locale": (r.get("Locale") or "").strip(),
                         "tournaments": n})
    return rows


def circuits_for(state_code, top_n=6):
    """The real competitive ladder for a student in `state_code`:
    their local circuits by activity, plus the national rungs."""
    rows = load_circuits()
    local = sorted([r for r in rows if r["locale"] == (state_code or "").upper()],
                   key=lambda r: -r["tournaments"])[:top_n]
    wanted = {"NSDA", "NatCir", "TOC-UK", "NIETOC", "Middle School", "Summer"}
    national = sorted([r for r in rows if r["abbr"] in wanted or r["name"] in wanted],
                      key=lambda r: -r["tournaments"])
    entry = [r for r in rows if r["abbr"] in {"MSPDP"} or r["name"] == "Middle School"]
    return {"local": local, "national": national, "entry_level": entry,
            "note": "Tournament counts are 2026-27 activity, i.e. how live each circuit is."}


def load_findings():
    """The admissions findings report, as structured claims."""
    import json, os
    path = settings.FINDINGS_JSON
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def findings_for(major_track):
    """Universal findings + the rung for this student's track."""
    f = load_findings()
    if not f:
        return {}
    key = (major_track or "").strip().lower().replace(" ", "_").replace("/", "_")
    alias = {"business_finance": "business", "finance": "business", "econ": "business",
             "law": "social_science", "public_affairs": "social_science",
             "politics": "social_science", "social_sciences": "social_science",
             "arts": "humanities", "writing": "humanities"}
    key = alias.get(key, key)
    return {"source": f.get("source"), "caveat": f.get("caveat"), "thesis": f.get("thesis"),
            "universal": f.get("universal", []),
            "track": key, "track_findings": f.get("by_major", {}).get(key)}


# ===========================================================================
# PUBLISHED ADMIT RATES — from the web, never from the corpus  [#24]
# ===========================================================================
# Division of labour, and it must not blur:
#   CORPUS  -> what an admit LOOKS like (profile pattern, activities, hooks)
#   THIS    -> how selective the school IS (official institution-wide rate)
# The corpus cannot give an honest rate: it is self-selected AND a third of
# posts omit rejections entirely (measured: inflates top-school rates 6-7 pts).

_RATES = None


def _rates():
    global _RATES
    if _RATES is None:
        import json
        try:
            with open(settings.ADMIT_RATES_JSON, encoding="utf-8") as fh:
                _RATES = json.load(fh)
        except Exception:
            _RATES = {"rates": {}, "aliases": {}}
    return _RATES


def canonical_college(name):
    d = _rates()
    n = (name or "").strip()
    return d.get("aliases", {}).get(n, n)


def published_admit_rate(college):
    """Official admit rate for one college, or None. Always carries its source year."""
    d = _rates()
    row = d.get("rates", {}).get(canonical_college(college))
    if not row:
        return None
    return {"college": canonical_college(college), "rate_pct": row["rate"],
            "class_of": row.get("class_of"), "admits": row.get("admits"),
            "applicants": row.get("applicants"),
            "confidence": row.get("confidence", "high"),
            "note": row.get("note"), "retrieved": d.get("_retrieved"),
            "kind": "published institution-wide admit rate — not this student's odds"}


def selectivity_band(college):
    """Band a school by its PUBLISHED rate. Bands describe the school, not the student."""
    r = published_admit_rate(college)
    if not r:
        return None
    p = r["rate_pct"]
    r["band"] = ("Far Reach" if p < 8 else "Reach" if p < 20
                 else "Target" if p < 50 else "Likely")
    return r
