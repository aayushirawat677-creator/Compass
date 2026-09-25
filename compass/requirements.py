"""
What each school says to TAKE — the fifth evidence source. [#82]

C7 (college_weights) tells us a school rates rigour Very Important. It does not tell us
which courses. This does, from each school's own admissions pages, and unlike the Common
Data Set it is published in plain HTML — the five of six schools whose CDS we could not
read are all readable here.

THE WORD MATTERS MORE THAN THE NUMBER:

    required     an application is incomplete without it   (UC A-G is the only hard gate
                                                            on this family's list)
    recommended  the school says it helps
    expected     the school describing its admits, not setting a bar

Collapsing those three into "needs" is over-goaling in the one place a parent cannot check
us — they will not read six admissions sites to find out we rounded a recommendation up.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(HERE, "data", "course_requirements.json")

# The only three framings a row may carry, strongest first.
FORCE = ("required", "recommended", "expected")


def _load():
    try:
        with open(PATH) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def for_schools(names):
    """The published requirements for this family's list, with the UC standard expanded.

    Matching goes through `modules.college_variants`, NOT substring containment. "NYU" and
    "New York University" share no substring, and neither do "UCLA" and "University of
    California, Los Angeles" — a containment match silently dropped both, which is the
    same bug `COLLEGE_ALIASES` was written for when UCLA matched zero admits.

    Returns {school: entry}. A school we hold nothing for is ABSENT rather than empty: the
    caller must be able to tell "we did not find it" from "the school asks nothing",
    because those license completely different sentences on the page.
    """
    from . import modules
    d = _load()
    schools = d.get("schools") or {}
    keyed = {k: set(modules.college_variants(k)) | {k.lower()} for k in schools}
    out = {}
    for n in (names or []):
        want = set(modules.college_variants(n)) | {str(n).lower()}
        hit = next((k for k, v in keyed.items() if v & want), None)
        if hit is None:
            continue
        entry = dict(schools[hit])
        if entry.get("see"):
            shared = d.get(entry["see"]) or {}
            entry = {**entry, **{k: v for k, v in shared.items() if k != "applies_to"}}
        out[n] = entry
    return out


def unquantified(names):
    """Schools on this list that publish NO year counts at all.

    Penn is the live case: named expectations ("calculus for Wharton"), no figures. The
    failure mode is a writer supplying plausible numbers that look exactly like the
    sourced rows, so naming these lets a gate say so.

    A school carrying `areas` (the UC A-G table) DOES state counts — they simply live
    under a different key. An earlier version checked `units` alone and reported Berkeley,
    whose requirements are the only hard gate on this family's list, as unquantified.
    """
    out = []
    for k, v in for_schools(names).items():
        if v.get("units") or v.get("areas"):
            continue
        out.append(k)
    return sorted(out)


def payload(names):
    """What the writer and the course step receive."""
    got = for_schools(names)
    return {
        "schools": got,
        "held_for": sorted(got),
        "not_held_for": sorted(n for n in (names or []) if n not in got),
        "publishes_no_year_counts": unquantified(names),
        "how_to_use": [
            "EVERY requirements row comes from here. A row with no school behind it is a "
            "fabrication, however reasonable it sounds.",
            "USE THE SCHOOL'S OWN WORD. required / recommended / expected are three "
            "different claims and a parent cannot check which one we meant.",
            "A school in `publishes_no_year_counts` states NO figures. Do not supply any; "
            "cite what it does say, by name.",
            "A school in `not_held_for` is one we have not read. Say nothing about what it "
            "asks — an absence in our record is not a fact about the school either.",
            "UC A-G credit depends on the course appearing on that high school's approved "
            "list. A subject taken is not automatically a subject counted, so an A-G row "
            "about a course the student already has is a CHECK, not a confirmation.",
        ],
    }
