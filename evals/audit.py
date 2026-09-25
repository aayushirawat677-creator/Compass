"""
Is the engine actually running everything it claims to?  [#71]

Not "do the rules exist" — that is easy and reassuring and wrong. This asks whether each
one is WIRED and whether it can FAIL. Both questions have caught real defects:

  * #42  `gate_draft` was defined in gates.py, documented in GATES.md and drawn on the
         orchestration diagram — and pipeline.py never called it. A gate nobody runs is
         worse than no gate, because the diagram says it is there.
  * #67  `gate_card_plan`, minutes after being written, PASSED a deliberately planted
         credential ("a published research paper with a university laboratory mentor")
         that the plan never builds. A gate that cannot fail is decoration.

Run:  python evals/audit.py
Exit code is non-zero when anything is unwired, unfireable, or undocumented.
"""
import importlib
import inspect
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from compass import gates as G           # noqa: E402
from compass import prompts as P         # noqa: E402
from compass import pipeline as PL       # noqa: E402

PIPE = inspect.getsource(PL)
PRM = open(os.path.join(ROOT, "compass", "prompts.py")).read()
GTS = open(os.path.join(ROOT, "compass", "gates.py")).read()
LOG = open(os.path.join(ROOT, "ENGINE_FEEDBACK_LOG.md")).read()

failures, notes = [], []


def check(ok, msg, detail=""):
    (notes if ok else failures).append(f"{'ok  ' if ok else 'FAIL'}  {msg}"
                                       + (f"\n        {detail}" if detail and not ok else ""))


# ---------------------------------------------------------------- 1. steps
def audit_steps():
    declared = set(P.BY_STEP)
    called = set(re.findall(r'_agent\(\s*"([a-z_]+)"', PIPE)) | \
             set(re.findall(r'_gated\(\s*\n?\s*"([a-z_]+)"', PIPE))
    orphans = sorted(declared - called - {"comparisons"})   # comparisons runs separately
    check(not orphans, f"every prompt is called by the pipeline ({len(declared)} declared)",
          f"declared but never called: {orphans}")
    ghosts = sorted(called - declared)
    check(not ghosts, "no step is called that has no prompt", f"called but undeclared: {ghosts}")


# ---------------------------------------------------------------- 2. gates wired
def audit_gates_wired():
    defined = {n for n, _ in inspect.getmembers(G, inspect.isfunction)
               if n.startswith("gate_")}
    called = set(re.findall(r"gates\.(gate_[a-z_]+)", PIPE))
    unwired = sorted(defined - called)
    check(not unwired, f"every gate is called by the pipeline ({len(defined)} defined)",
          f"defined but never called — this is the #42 bug: {unwired}")


# ---------------------------------------------------------------- 3. gates can fail
def audit_gates_fire():
    """Feed each gate input it MUST reject. A gate that passes garbage is decoration."""
    bad_plan = {"grades": [{"grade": 12, "goals": [
        {"goal": "Qualify for the state DECA conference with his rung raised",
         "track": "target",
         "tasks": [{"term": "Fall", "text": "Pay $95 by Mar 3"},
                   {"term": "Fall", "text": "Do it"}]}]}]}
    appr = [{"activity": "card business",
             "appraisal": {"verdict": "convert", "why": "",
                           "conversion": {"becomes": "x", "grade": 9}},
             "needs_family_input": False, "type_knowledge": {}}]
    cases = [
        ("intake", lambda: G.gate_intake({})),
        ("profile", lambda: G.gate_profile({"spine": "", "constraints": {},
                                            "note": "tier 1, 40% odds"})),
        ("retrieval", lambda: G.gate_retrieval({"cards": []})),
        ("gap", lambda: G.gate_gap({"gaps": []})),
        ("strategy", lambda: G.gate_strategy({"selected_moves": []}, {"gaps": []}, {})),
        ("plan", lambda: G.gate_plan({}, {"selected_moves": []})),
        ("two_paths", lambda: G.gate_two_paths({})),
        ("appraisal", lambda: G.gate_appraisal(
            [{"activity": "a", "appraisal": {"verdict": "nonsense"}}],
            [{"name": "a", "signals": {"hours_per_week": 9}},
             {"name": "unappraised", "signals": {}}])),
        ("document", lambda: G.gate_document(
            {"roadmap": {"grades": []}}, {"grades": [{"grade": 8, "goals": [
                {"goal": "A goal nobody rendered", "tasks": []}]}]})),
        ("honours_appraisal", lambda: G.gate_honours_appraisal(
            {"grades": [{"grade": 12, "goals": [
                {"goal": "Keep trading his cards alone", "tasks": []}]}]}, appr)),
        ("open_questions", lambda: G.gate_open_questions(
            {"grades": []}, [{"activity": "chess", "needs_family_input": True,
                              "family_question": "",
                              "appraisal": {"verdict": "retire"}}])),
        ("horizon", lambda: G.gate_horizon(bad_plan, 8)),
        ("academics", lambda: G.gate_academics(
            {"grades": [{"grade": g, "goals": [{"goal": "Play sport", "tasks": []}]}
                        for g in (8, 9, 10, 11, 12)]}, None, 8)),
        ("card_plan", lambda: G.gate_card_plan(
            {"target_variant": {"achievement_profile": [
                {"credential": "A published research paper with a university lab mentor"}]}},
            {"grades": [{"grade": 8, "goals": [
                {"goal": "Sell at a fair", "tasks": []}]}]})),
        ("parent_voice", lambda: G.gate_parent_voice(
            {"profile": {"lead": "We only have one thing on record about his cooking, "
                                 "and we do not know whether he still does it."}})),
        ("budget", lambda: G.gate_budget({"over_budget": [{"x": 1}],
                                          "outside_region": [{"y": 2}]})),
    ]
    for name, fn in cases:
        try:
            res = fn()
            check(res.verdict != G.PASS, f"gate_{name} rejects input it must reject",
                  f"PASSED deliberately bad input — it cannot fail, so it is decoration")
        except Exception as e:                                  # noqa: BLE001
            check(False, f"gate_{name} rejects input it must reject",
                  f"raised {type(e).__name__}: {e}")


# ---------------------------------------------------------------- 4. rules
def audit_rules():
    logged = {int(re.sub(r"\D", "", m)) for m in re.findall(r"^##+ (\d+)", LOG, re.M)}
    # Scan EVERY source file, not just the prompts and the gates. The first version of
    # this check read prompts.py and gates.py only, and reported nine rules as enforced
    # nowhere — when most of them live in pipeline.py, modules.py or the data layer, which
    # is exactly where a wiring rule should live. An audit that looks in two of six places
    # produces a confident wrong answer, which is the failure it exists to prevent. [#71]
    src = ""
    for root, _, files in os.walk(os.path.join(ROOT, "compass")):
        for fn in files:
            if fn.endswith(".py"):
                src += open(os.path.join(root, fn)).read()
    src += open(os.path.join(ROOT, "settings.py")).read()
    for fn in os.listdir(HERE):
        if fn.endswith((".py", ".md")):
            src += open(os.path.join(HERE, fn)).read()
    cited = {int(x) for x in re.findall(r"\[#(\d+)", src)}
    # This file's own rule number is cited here and logged after the first clean run.
    check(not (cited - logged - {71}), "every rule cited in code has a log entry",
          f"cited but never logged: {sorted(cited - logged - {71})}")
    # A logged rule should land SOMEWHERE — prompt, gate, or be explicitly code-only.
    # Log entries that are findings or mechanisms rather than enforceable rules.
    NOT_A_RULE = {3,    # "business claim confirmed accurate — no change needed"
                  26,   # the rubric grader itself
                  27,   # a rubric rewrite, which lives in evals/*.md
                  30,   # the gates mechanism — it IS the gates
                  42, 54, 65,   # gate bugs, which belong to the code
                  58, 71}       # meta-notes about the process (71 is this file)
    SUPERSEDED = {61}                      # reverted by #62
    homeless = sorted(logged - cited - NOT_A_RULE - SUPERSEDED)
    check(not homeless, "every logged rule is in a prompt or a gate",
          f"logged but enforced nowhere: {homeless}")


# ---------------------------------------------------------------- 5. contracts
def audit_contracts():
    NEEDS = {
        "profile": ["EVIDENCE", "TONE", "PROSE", "SCHEMA"],
        "gap": ["EVIDENCE", "SCHEMA"],
        "appraiser": ["EVIDENCE", "TONE", "PROSE", "SCHEMA"],
        "strategy": ["EVIDENCE", "PLANNING", "PLANNING_STRUCTURE", "SCHEMA"],
        "two_paths": ["EVIDENCE", "CARD_GRAMMAR", "PLANNING_STRUCTURE", "SCHEMA"],
        "plan_goals": ["EVIDENCE", "TONE", "PROSE", "PLANNING", "PLANNING_STRUCTURE", "SCHEMA"],
        "plan_recs": ["EVIDENCE", "TONE", "PROSE", "SCHEMA"],
        "writer": ["EVIDENCE", "TONE", "PROSE", "PLANNING_STRUCTURE", "CARD_GRAMMAR"],
        "critic": ["EVIDENCE", "TONE", "PROSE", "PLANNING_STRUCTURE", "CARD_GRAMMAR"],
    }
    for step, needed in NEEDS.items():
        body = P.BY_STEP[step][0]
        missing = [n for n in needed if getattr(P, n).strip()[:60] not in body]
        check(not missing, f"{step} carries the contracts it enforces",
              f"missing: {missing}")


# ---------------------------------------------------------------- 6. rubrics
def audit_rubrics():
    files = os.listdir(HERE)
    WANT = {"profile": "R1_profile", "gap": "GapAnalyst", "appraiser": "R3_appraiser",
            "strategy": "R4_strategy", "two_paths": "R5_twopaths", "plan_goals": "R6_plan",
            "plan_recs": "R7_recommendations", "critic": "R8_critic", "writer": "R9_writer"}
    for step, stem in WANT.items():
        check(any(f.startswith(stem) for f in files), f"{step} has a rubric",
              f"no evals/{stem}*_rubric.md")


# ---------------------------------------------------------------- 7. prompts build
def audit_prompts_build():
    for step, (body, tier) in P.BY_STEP.items():
        check(isinstance(body, str) and len(body) > 500, f"{step} prompt builds",
              f"len={len(body) if isinstance(body, str) else type(body)}")
        # Only a CONTRACT name left unsubstituted is a defect. Prompts legitimately carry
        # single braces in their output — the JSON shape specs are written {{like this}}
        # in source precisely so they survive as {like this}. The first version of this
        # check flagged six prompts for that, which is the audit repeating the mistake it
        # exists to catch: matching spelling where the rule is about substance. [#71]
        CONTRACTS = ("EVIDENCE", "TONE", "PROSE", "PLANNING", "PLANNING_STRUCTURE",
                     "CARD_GRAMMAR", "SCHEMA")
        left = [c for c in CONTRACTS if "{" + c + "}" in body]
        check(not left, f"{step} has no unresolved contract placeholder",
              f"never injected: {left}")


# ------------------------------------------------- 8. template <-> spec <-> defaults
def audit_render_contract():
    """EVERY FIELD THE TEMPLATE RENDERS MUST BE SPECIFIED, AND DEFAULTED. [#89]

    This is the check that decides whether a real run produces the document we have been
    looking at. A field the TEMPLATE reads and the WRITER SPEC never names is not a subtle
    defect: the writer has no reason to emit it, so that block renders empty and nobody
    finds out until a family opens the PDF. It happened four times over — `act_on`,
    `act_on_head`, `plans_title`, `plans_lead`, which between them are the heading of the
    Two Plans page and the most useful block on the courses page.

    It is invisible precisely because the fix that introduced it worked: hand-edited
    writer output renders perfectly, so the page looks finished while the prompt that has
    to reproduce it says nothing at all.

    Three directions:
      * template reads it   -> the spec must name it
      * template reads it   -> `_safe` must default it (or a thin run raises)
      * spec promises it    -> the template should use it, or we are asking the model for
                               output nobody reads (a warning, not a failure: some fields
                               are consumed by gates rather than by the page)
    """
    import re
    tpl = open(os.path.join(ROOT, "compass", "render.py")).read()
    # Scan JINJA EXPRESSIONS ONLY. A bare search for "c." also matches the stylesheet,
    # where `.ct .c.t{...}` is two CSS classes and not a template field at all — this
    # check reporting phantom keys `c.s` and `c.t` on its first run, which is the
    # substring-for-substance mistake the audit exists to catch, committed by the audit.
    jinja = " ".join(m.group(0) for m in re.finditer(r"\{\{.*?\}\}|\{%.*?%\}", tpl, re.S))
    fields = sorted({m.group(1) for m in re.finditer(r"\bc\.([a-z_]+(?:\.[a-z_]+)*)", jinja)})
    tops = sorted({f.split(".")[0] for f in fields if f.split(".")[0] not in ("cover",)})

    unspecced = [f for f in fields
                 if f.split(".")[-1] not in ("cover", "student", "grade")
                 and not re.search(rf"\b{re.escape(f.split('.')[-1])}\b", PRM)]
    check(not unspecced,
          "every field the template renders is named in the writer spec",
          f"renders blank on a real run: {['c.' + f for f in unspecced]}")

    safe = tpl[tpl.index("def _safe("):] if "def _safe(" in tpl else ""
    undefaulted = [t for t in tops if f'"{t}"' not in safe]
    check(not undefaulted,
          "every top-level template key has a default in _safe",
          f"no default, so a thin draft raises: {undefaulted}")

    # The card macros read `card.*` rather than `c.*`; check those too.
    mac = sorted({m.group(1) for m in re.finditer(r"\bcard\.([a-z_]+)", jinja)})
    unspecced_card = [k for k in mac if not re.search(rf"\b{k}\b", PRM)]
    check(not unspecced_card,
          "every card field the macros render is named in the writer spec",
          f"renders blank: {['card.' + k for k in unspecced_card]}")


if __name__ == "__main__":
    for fn in (audit_steps, audit_gates_wired, audit_gates_fire, audit_rules,
               audit_contracts, audit_rubrics, audit_prompts_build,
               audit_render_contract):
        fn()
    for line in notes:
        print(line)
    if failures:
        print("\n" + "=" * 70)
        for line in failures:
            print(line)
        print(f"\n{len(failures)} problem(s), {len(notes)} checks passed.")
        sys.exit(1)
    print(f"\nall {len(notes)} checks passed.")
