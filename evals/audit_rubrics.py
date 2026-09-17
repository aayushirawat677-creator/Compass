"""
Audits every rubric against RUBRIC_STANDARD.md rules 1-8.

It cannot judge whether a CHECK is good — only whether the rubric is SHAPED to be
honest: right number of checks, weighted, gated where needed, an outcome check, a fix
lever on every check, a stated boundary, and a version.

    python evals/audit_rubrics.py
"""
import re, glob, os, sys

# Levers may be written as constants OR in prose — R1/Gap use prose, and a rubric is not
# worse for it. Matching only the constants false-failed both of them (standard rule 7).
LEVER_PAT = re.compile(
    r"FIX_PROMPT|ASK_PARENT|CHANGE_INTAKE|CHANGE_SCHEMA|BAD_INPUT"
    r"|Fix the prompt|Fix if low|\*\*Fix:\*\*|Fix:|Ask the parent|Change the intake"
    r"|Change intake|Change the schema|upstream", re.I)

def audit(path):
    t = open(path, encoding="utf-8").read()
    checks = re.findall(r"^### .*$", t, re.M)
    n = len(checks)
    # Weighting may be a ★ on the check OR stated in prose ("checks 2,3,4 are the heart").
    starred = sum(1 for c in checks if "★" in c)
    weighted = starred >= 1 or bool(re.search(
        r"are the heart|is the heart|carry it|carries it|carry the grade|carries the grade"
        r"|the real thinking|\(the GATE\)", t, re.I))
    gate = bool(re.search(r"\(the GATE\)|\(THE GATE\)|GATE\)", t))
    # An outcome check may be labelled, or BE the gate, or be the designated heart check.
    outcome = bool(re.search(r"outcome check|\(the GATE\)|are the heart|carry it|carries it"
                             r"|carry the grade|carries the grade", t, re.I))
    levers = len(LEVER_PAT.findall(t))
    # R1's house style is "What R4 outputs" / "What the Match Key outputs" — match any.
    subject = bool(re.search(r"What .{1,30}outputs|What it reads in", t))
    boundary = bool(re.search(r"NOT graded on", t))
    version = bool(re.search(r"\(v\d\)|v2 changes|v2 change", t))
    phrase_risk = len(re.findall(r'contains? ["“]|the phrase|verbatim', t, re.I))

    rules = {
        "1 subject named":      subject,
        "2 check count (3-6)":  3 <= n <= 6,
        "2 weighted":           weighted,
        "3 gate where needed":  True if gate else None,     # None = not required
        "4 outcome check":      outcome,
        "6 fix levers":         levers >= max(1, n - 1),
        "7 boundary stated":    boundary,
        "8 versioned":          version,
    }
    return n, starred, gate, rules, phrase_risk

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(here, "*_rubric.md")))
    print("=" * 84)
    print("RUBRIC AUDIT — against RUBRIC_STANDARD.md")
    print("=" * 84)
    print(f"{'rubric':32s} {'chk':>3s} {'★':>2s} {'gate':>5s}  failures")
    print("-" * 84)
    total_fail = 0
    for f in files:
        n, star, gate, rules, risk = audit(f)
        fails = [k for k, v in rules.items() if v is False]
        total_fail += len(fails)
        g = "yes" if gate else "-"
        print(f"{os.path.basename(f):32s} {n:3d} {star:2d} {g:>5s}  "
              f"{'OK' if not fails else ', '.join(fails)}")
    print("-" * 84)
    print(f"{total_fail} rule failures across {len(files)} rubrics")
    print("\nNOTE: this audits SHAPE, not content. A rubric can pass every line here and still")
    print("contain a check that measures the wrong thing — that needs a person (rule 7).")

if __name__ == "__main__":
    main()
