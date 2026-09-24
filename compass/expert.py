"""
The expert corpus — practitioner advice, retrieved by section.  [#73]

A FOURTH evidence source, and the only one that is not measured. Keep the four apart:

    corpus         what an admit to this school looked like      (our CSV, 30,414 rows)
    admit_rates    how selective this school is                  (published rates)
    college_weights what this school says it weighs              (CDS C7)
    THIS           what experienced practitioners advise         (advisory only)

ADVISORY MEANS ADVISORY. It informs; it never overrides a measurement. If our corpus says
admits to these six schools held debate at the school rung and a practitioner says
national, the measurement wins and the disagreement is worth noting. That is not a
judgment about the practitioners — it is that 137 rules from four sources, 71 of them
resting on a single speaker and 34 on one Instagram account that promotes its own
programs, is a different kind of thing from 30,414 rows.

TWO THINGS THE CORPUS ITSELF WARNS ABOUT, and we honour both:

  * §0.4 — "Most advice targets Ivy+ / highly selective schools (<=10% admit rate). For
    students targeting less selective schools, relax intensity-related rules (rigor
    maxing, national awards) but keep authenticity, depth, and narrative rules."
    Ignoring this turns the corpus into a machine for telling a student aiming at a
    30%-admit school that he needs national awards. `tier()` computes the band.
  * §16 — the vendor statistics (RSI -> HYPS ~59-60%, "7.4x admit rate") are marketing,
    show correlation not causation, and must never reach a family as fact.

RETRIEVAL, NOT INJECTION. The whole document is ~12.9k tokens and `plan_goals` is already
~40k. Each step gets the sections that bear on its job, by ID, and cites the rules it
applied so a human can audit which advice drove which goal.
"""
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(HERE, "data", "expert_corpus.md")

# Which sections each step should see. Two of these were written for us almost verbatim:
# §14.3 is headed "Profile diagnostic checklist (for a GapAnalyst agent)", and §14.2's
# if-then heuristics are strategy's decision logic in another notation.
FOR_STEP = {
    "gap":        ["14.3"],
    "appraiser":  ["3.2", "3.3", "15"],
    "strategy":   ["1", "14.2", "15", "3.1"],
    "plan_goals": ["11", "2", "5", "6", "14.2"],
    "plan_recs":  ["5", "5.1", "6.1", "14.1"],
    "two_paths":  ["7", "1"],
    "writer":     ["7"],
    "critic":     ["14.1"],
}

# Confidence, strongest first. A rule's tag decides how hard an agent may lean on it.
CONFIDENCE = ("CONSENSUS", "SINGLE", "CONTESTED", "DATA")


def _text():
    try:
        with open(PATH) as fh:
            return fh.read()
    except OSError:
        return ""


def sections():
    """{id: title} for every numbered section and subsection."""
    out = {}
    for m in re.finditer(r"^#{2,3}\s+(\d+(?:\.\d+)?)\.?\s+(.+)$", _text(), re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def get(ids):
    """The raw markdown of the named sections, concatenated in the order given.

    A subsection (3.2) returns just that subsection; a parent (3) returns the parent and
    everything under it.
    """
    body = _text()
    if not body:
        return ""
    heads = [(m.start(), m.group(1), len(m.group(0)) - len(m.group(0).lstrip("#")))
             for m in re.finditer(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.?\s+.+$", body, re.M)]
    heads = [(m.start(), m.group(2), len(m.group(1)))
             for m in re.finditer(r"^(#{2,3})\s+(\d+(?:\.\d+)?)\.?\s+.+$", body, re.M)]
    chunks = []
    for want in ([ids] if isinstance(ids, str) else ids):
        for i, (pos, sid, level) in enumerate(heads):
            if sid != want:
                continue
            end = len(body)
            for pos2, sid2, level2 in heads[i + 1:]:
                # stop at the next heading of the same or higher rank
                if level2 <= level:
                    end = pos2
                    break
            chunks.append(body[pos:end].rstrip())
            break
    return "\n\n".join(chunks)


def by_id(rule_id):
    """One rule's row, so a citation can be checked against what it actually says."""
    for line in _text().split("\n"):
        if re.search(rf"\*\*{re.escape(str(rule_id))}\*\*", line):
            return line.strip()
    return ""


def valid_ids():
    return set(re.findall(r"\*\*([A-Z]{2,8}-\d{2})\*\*", _text()))


def tier(admit_rates):
    """Which intensity band this student's targets sit in, per §0.4.

    Takes {school: rate_pct}. Uses the MOST selective target, because the plan aims at the
    whole list — but reports the spread, since a list running 4.9% to 16% is a different
    problem from one clustered at 30%, and the difference is exactly where over-goaling
    comes from.
    """
    vals = [float(v.get("rate") if isinstance(v, dict) else v)
            for v in (admit_rates or {}).values()
            if (v.get("rate") if isinstance(v, dict) else v) is not None]
    if not vals:
        return {"band": "unknown", "apply_intensity": False,
                "note": "no published rates held — do not apply intensity advice on a guess"}
    lo, hi = min(vals), max(vals)
    if lo <= 10:
        band, apply_ = "ivy_plus", True
    elif lo <= 20:
        band, apply_ = "highly_selective", "partial"
    else:
        band, apply_ = "selective", False
    return {
        "band": band,
        "most_selective_pct": round(lo, 2),
        "least_selective_pct": round(hi, 2),
        "apply_intensity": apply_,
        "note": (
            "The expert corpus is calibrated to Ivy+ (<=10% admit). Intensity advice — "
            "rigour maxing, national awards, award counts — applies at FULL strength only "
            "to targets at or under 10%. For the rest, relax intensity and keep the "
            "authenticity, depth and narrative rules, which hold at every tier. "
            f"This list runs {round(lo,1)}% to {round(hi,1)}%, so "
            + ("some targets are in band and most are not — size the plan to the school, "
               "not to the hardest one on the list."
               if lo <= 10 < hi else
               "apply the band uniformly.")
        ),
    }


def for_step(step, admit_rates=None):
    """Everything a step needs: its sections, the tier verdict, and the standing rules."""
    ids = FOR_STEP.get(step, [])
    if not ids:
        return {}
    return {
        "sections": get(ids),
        "section_ids": ids,
        "tier": tier(admit_rates),
        "how_to_use": [
            "ADVISORY. This never overrides a measurement. Where it disagrees with the "
            "corpus, the admit pattern or a school's own CDS, the measurement wins and "
            "you note the disagreement rather than splitting the difference.",
            "CITE THE RULE ID you applied (e.g. EC-20, ACAD-14) so a human can audit "
            "which advice drove which goal.",
            "WEIGH BY TAG: [CONSENSUS] is two or more independent sources and can be "
            "leaned on. [SINGLE] is one speaker — use it, hedge it, never build a plan's "
            "centre on it. [CONTESTED] means the sources disagree; see §15 and decide "
            "from this student's situation. [DATA] figures from vendor webinars are "
            "marketing and never reach a family as fact.",
            "NEVER RECOMMEND anything in §14.1 — pay-to-play research, bought passion "
            "projects, AI-written essays, fabricated claims.",
        ],
    }
