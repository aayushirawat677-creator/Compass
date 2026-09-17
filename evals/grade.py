"""
Rubric grader for the RENDERED PLAN — i.e. R9's writing and the modules' numbers.

SCOPE, because this was wrong once: the rendered plan is what R9 WROTE. R1's profile
object and the Gap Analyst's gap map are internal and never appear here, so this file
cannot grade them — use evals/grade_agents.py for those. Labelling a writing defect as
an R1 defect sends you to fix the wrong prompt.

Scores against the rules in ENGINE_FEEDBACK_LOG.md.

WHY PROGRAMMATIC: every check below traces to a defect Aayushi caught by hand. If the
grader can't catch it, the rubric isn't real. Run it on any plan JSON to see which rules
hold and which leak. Checks are deliberately literal — a FAIL is evidence, not opinion.

    python evals/grade.py out/neerav_plan.plan.json
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _txt(o):
    if isinstance(o, str): return o
    if isinstance(o, dict): return " ".join(_txt(v) for v in o.values())
    if isinstance(o, list): return " ".join(_txt(v) for v in o)
    return ""

def C(rule, ok, detail=""):  return {"rule": rule, "pass": bool(ok), "detail": detail}

# --------------------------------------------------------------------------
def grade_profile(p):
    t = _txt(p); out = []
    judg = re.findall(r"\b(protect these|don't expand|keep it, don't|should drop|must drop|worth keeping as they are)\b", t, re.I)
    out.append(C("#1 profile describes, never judges", not judg, f"found: {judg}"))
    stats = re.findall(r"\b\d{1,3}\s?%|\bcohort\b|\badmits\b(?! to)", t, re.I)
    out.append(C("#20 no cohort statistics on the profile", not stats, f"found: {stats[:4]}"))
    bad = re.findall(r"\b(argumentative|perfectionist|needy|struggles with|shuts down|actual customers|some comfort)\b", t, re.I)
    out.append(C("#8 no pejorative / faint-praise wording", not bad, f"found: {bad}"))
    abs_ = re.findall(r"\b(always|never quits|any setback|will quit|won't last)\b", t, re.I)
    out.append(C("#15 no absolutes about the child", not abs_, f"found: {abs_}"))
    fam = re.findall(r"\b(divorce[d]?|two homes|two-home|custody|tires quickly|can't carry)\b", t, re.I)
    out.append(C("#5 no sensitive family cause named", not fam, f"found: {fam}"))
    pipe = re.findall(r"\b(strategy step|the engine|our pipeline|this agent|backend)\b", t, re.I)
    out.append(C("#7 no internal process talk", not pipe, f"found: {pipe}"))
    echo = []
    for b in p.get("blocks", []):
        th = set(re.findall(r"\w{5,}", (b.get("thesis") or "").lower()))
        bo = set(re.findall(r"\w{5,}", (b.get("body") or "").lower()))
        if th and len(th & bo) / len(th) > 0.55: echo.append(b.get("subhead", "")[:40])
    out.append(C("#7 body does not restate its thesis", not echo, f"echoing: {echo}"))
    throat = [b.get("subhead","")[:30] for b in p.get("blocks", [])
              if re.match(r"^(here is|set apart|a note on)", (b.get("body") or ""), re.I)]
    out.append(C("#7 no throat-clearing opener", not throat, f"found: {throat}"))
    return out

def grade_card(card, name):
    t = _txt(card); out = []
    out.append(C(f"#19 {name}: label not 'PROJECTED'", "PROJECTED" not in (card.get("label") or "")))
    stats = re.findall(r"\b\d{1,3}\s?%\s*of (?:this )?cohort|cohort\b|~\d{1,3}%", _txt(card.get("credentials")), re.I)
    out.append(C(f"#20 {name}: no cohort stats in credentials", not stats, f"found: {stats[:3]}"))
    statkeys = " ".join(s.get("k","") for s in card.get("stats", [])).lower()
    dup = [c["h"] for c in card.get("credentials", [])
           if re.search(r"\b(gpa|1500|sat|act|aps?\b|calculus)\b", c.get("h",""), re.I)]
    out.append(C(f"#20 {name}: credentials don't repeat the stat row", not dup, f"found: {dup}"))
    itin = [c["h"] for c in card.get("credentials", [])
            if re.search(r"\b(fall|spring|summer|grade \d|this year|then)\b", _txt(c), re.I)]
    out.append(C(f"#17a {name}: achievements, not an itinerary", not itin, f"found: {itin}"))
    vague = [c["h"] for c in card.get("credentials", [])
             if re.search(r"\b(a real credential|a sustained role|meaningful|strong result)\b", c.get("h",""), re.I)]
    out.append(C(f"#17a {name}: no vague virtue nouns", not vague, f"found: {vague}"))
    noLevel = [c["h"] for c in card.get("credentials", [])
               if not re.search(r"\b(state|national|captain|award|medal|five-year|four-year|registered|top[- ]\w+|qualifier|delegate|placement)\b", _txt(c), re.I)]
    out.append(C(f"#20 {name}: every credential names a level", not noLevel, f"missing: {noLevel}"))
    tk = card.get("takeaway","")
    out.append(C(f"#19 {name}: takeaway <= 2 sentences", len(re.findall(r"[.!?]", tk)) <= 2, tk[:60]))
    return out

def grade_numbers(plan, rates):
    out = []; t = _txt(plan)
    odds = re.findall(r"\b(his (?:chance|odds|probability)|chance of (?:getting|admission)|turned into odds)\b", t, re.I)
    out.append(C("#24 no personal-odds phrasing", not odds, f"found: {odds}"))
    pcts = set(re.findall(r"(\d{1,3}(?:\.\d)?)\s?%", t))
    known = {f"{v['rate']}" for v in rates.values()} | {f"{int(v['rate'])}" for v in rates.values()}
    band_edges = {"15","35","60","8","20","50"}
    unex = sorted(p for p in pcts if p not in known and p not in band_edges)
    out.append(C("#24 every % traces to the published table or a band edge",
                 not unex, f"untraceable: {unex[:8]}"))
    years = re.findall(r"class of 20\d\d", t, re.I)
    out.append(C("#24 rates carry a class year", bool(years), f"found {len(years)}"))
    # band scheme must be the PUBLISHED-rate one (<8 / <20 / <50 / else), not the old corpus one
    old = re.findall(r"(?:<\s?15%|15[–-]35%|35[–-]60%|60%\+)", t)
    out.append(C("#24 bands use the published-rate scheme (<8 / <20 / <50)",
                 not old, f"stale corpus-era bands: {sorted(set(old))}"))
    src = re.search(r"cohort rates|from a cohort of|in your dataset", t, re.I)
    out.append(C("#24 bands not sourced from the corpus", not src,
                 f"corpus-sourced wording: {src.group(0) if src else ''}"))
    return out

def grade_planning(plan):
    """STRUCTURAL checks. Earlier versions matched boilerplate phrases, which a plan
    could satisfy by pasting a sentence in without changing the strategy. These count
    and inspect what the plan actually does."""
    out = []; t = _txt(plan)
    rm = plan.get("roadmap", {}); grades = rm.get("grades", [])

    # 1. HORIZON — structural: later years carry no bookable specifics
    later = " ".join(_txt(g) for g in grades[1:])
    spec = re.findall(r"\(\d{3}\)\s?\d{3}|\b[\w.-]+\.(?:com|org)\b|\$\d", later)
    out.append(C("#21 horizon: later years carry no bookable specifics", not spec, f"found: {spec[:4]}"))

    # 2. HORIZON — is the limitation disclosed anywhere, in any wording?
    disc = re.search(r"(come later|when we can confirm|general direction|update it every year|"
                     r"stays at goals|revisit|directional)", t, re.I)
    out.append(C("#21 horizon: limitation disclosed to the parent", bool(disc),
                 "no sentence explains why later years are less specific"))

    # 3. JOIN, DON'T FOUND — tightened so "we found the class" is not a false positive
    bad = re.findall(r"\b(founded|founding|start(?:s|ing)? (?:a|his own) (?:club|nonprofit|program\w*|initiative)|"
                     r"(?:program\w*|initiative|club) of his own|his own (?:program\w*|initiative))\b", t, re.I)
    out.append(C("#21 join, don't found", not bad, f"found: {sorted(set(bad))[:4]}"))

    # 4. ACTIVITY CAP — COUNT the threads carried once committed (grade 10+), don't phrase-match
    counts = {}
    for g in grades:
        gname = g.get("grade", "")
        if re.search(r"1[012]", gname):
            counts[gname] = len(g.get("rows", []))
    over = {k: v for k, v in counts.items() if v > 4}
    out.append(C("#21 activity load actually capped (<=4 threads from grade 10)",
                 not over, f"threads per grade: {counts}"))

    # 5. SUMMER LADDER — do the summers actually escalate?
    summers = {}
    for g in grades:
        for row in g.get("rows", []):
            for tk in row.get("tasks", []):
                if re.search(r"summer", tk.get("term", ""), re.I):
                    summers[g.get("grade", "")] = tk.get("text", "")
    job = any(re.search(r"\b(job|internship|paid work|employment|real work|work experience)\b", v, re.I) for v in summers.values())
    app = any(re.search(r"\b(essay|application|common app|strategy)\b", v, re.I) for v in summers.values())
    out.append(C("#21 summers escalate (a real job, then application work)",
                 job and app, f"summers found: {list(summers)} | job={job} app={app}"))

    # 6. Real sanctioning bodies, not generic descriptions
    out.append(C("#21 real bodies named (not generic)",
                 bool(re.search(r"\bNSDA\b|\bTOC\b|\bGGSA\b|\bDECA\b|Coast Forensic", t)),
                 "looked for NSDA / TOC / GGSA / DECA"))

    # 7. CARD <-> PLAN RECONCILIATION (#17) — every credential must have plan work behind it
    plan_words = set(re.findall(r"[a-z]{5,}", _txt(rm).lower() + _txt(plan.get("this_year", {})).lower()))
    orphans = []
    for side in ("target", "stretch"):
        for c in plan.get(side, {}).get("card", {}).get("credentials", []):
            kw = set(re.findall(r"[a-z]{5,}", c.get("h", "").lower()))
            if kw and not (kw & plan_words):
                orphans.append(f"{side}: {c['h'][:40]}")
    out.append(C("#17 every card credential is earned by plan work", not orphans, f"orphans: {orphans}"))

    # 8. CONSTRAINTS actually respected in what is recommended
    cons = _txt(plan.get("profile", {}).get("blocks", []))
    budget = re.search(r"\$([\d,]+)\s*[–-]\s*\$?([\d,]+)", cons)
    over_b = []
    if budget:
        cap = float(budget.group(2).replace(",", ""))
        for m in re.findall(r"\$([\d,]{3,})", _txt(plan.get("this_year", {}))):
            if float(m.replace(",", "")) > cap: over_b.append(m)
    out.append(C("#21 no recommendation exceeds the stated budget", not over_b, f"over cap: {over_b}"))
    return out


def grade_recs(plan):
    out = []; cards = [c for term in plan.get("this_year", {}).get("terms", []) for c in term.get("cards", [])]
    out.append(C("#catalog no placeholders", "[CATALOG]" not in _txt(plan)))
    nocontact = [c["title"][:40] for c in cards if not c.get("contact") and not re.search(r"free|school", _txt(c), re.I)]
    out.append(C("#catalog every rec has a contact", not nocontact, f"missing: {nocontact}"))
    out.append(C("#catalog age fit stated somewhere",
                 bool(re.search(r"ages? \d+.\d+|8–14|8-14", _txt(plan)))))
    noby = [c["title"][:40] for c in cards if not c.get("plan_by")]
    out.append(C("#catalog every rec has a deadline", not noby, f"missing: {noby}"))
    return out

def main(path):
    plan = json.load(open(path))
    rates = json.load(open("data/admit_rates.json"))["rates"]
    groups = [
        ("R9 WRITING — profile section",  grade_profile(plan.get("profile", {}))),
        ("R9 WRITING — target card",      grade_card(plan.get("target", {}).get("card", {}), "target")),
        ("R9 WRITING — stretch card",     grade_card(plan.get("stretch", {}).get("card", {}), "stretch")),
        ("NUMBERS INTEGRITY (modules)",  grade_numbers(plan, rates)),
        ("R4/R6 as RENDERED — strategy",  grade_planning(plan)),
        ("R7 as RENDERED — recs",         grade_recs(plan)),
    ]
    tot = pas = 0
    print(f"\nRUBRIC REPORT  ·  {os.path.basename(path)}\n" + "="*74)
    for title, checks in groups:
        p = sum(c["pass"] for c in checks); n = len(checks); tot += n; pas += p
        print(f"\n{title}   {p}/{n}")
        for c in checks:
            mark = "PASS" if c["pass"] else "FAIL"
            print(f"   [{mark}] {c['rule']}")
            if not c["pass"] and c["detail"]: print(f"          -> {c['detail'][:100]}")
    print("\n" + "="*74)
    print(f"OVERALL  {pas}/{tot}  ({pas/tot*100:.0f}%)")
    return pas, tot

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out/neerav_plan.plan.json")
