"""
Self-extending published admit-rate table.  [feedback log #25]

The corpus cannot produce an admit rate (self-selected, and a third of posts omit
rejections). Published rates come from the web. When a school is not yet in
data/admit_rates.json, this looks it up live, verifies it, and writes it back — so
the table grows as new families bring new school lists, instead of a human
hand-maintaining it.

    python -m compass.refresh_rates "Boston University" "Emory University"
    python -m compass.refresh_rates --missing-from out/plan.state.json
"""
import json, os, sys
from . import data_access, llm
import settings

QUESTION = ("What is {college}'s most recent published OVERALL undergraduate admit rate "
            "(percentage of applicants admitted)? Give the percentage, the class year or "
            "admission cycle it refers to, the number admitted and the number of applicants "
            "if stated, and the source URL. Prefer the university's own admissions or "
            "newsroom page, or its Common Data Set.")


def ensure_rate(college, write=True):
    """Return the published rate for `college`, looking it up live if absent."""
    have = data_access.published_admit_rate(college)
    if have:
        return have
    got = llm.research_fact(QUESTION.format(college=college))
    if not got.get("found"):
        return {"college": college, "rate_pct": None, "found": False,
                "notes": got.get("notes", "not found"),
                "guidance": "Say the figure isn't on hand. Never estimate one."}
    row = {"rate": float(got["value"]), "class_of": got.get("year"),
           "source_url": got.get("source_url"), "source_name": got.get("source_name"),
           "confidence": got.get("confidence", "medium"),
           "retrieved_by": "live lookup", "notes": got.get("notes", "")}
    if write:
        _write(college, row)
        data_access._RATES = None          # invalidate cache
    return data_access.published_admit_rate(college) or {"college": college, **row}


def _write(college, row):
    path = settings.ADMIT_RATES_JSON
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d.setdefault("rates", {})[data_access.canonical_college(college)] = row
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)


def ensure_many(colleges):
    return {c: ensure_rate(c) for c in colleges}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for c, r in ensure_many(args).items():
        print(f"{c:42s} {r.get('rate_pct') or r.get('rate') or '—'}  {r.get('notes','')}")
