"""
Compass strategy engine — graph nodes.

One node per agent or module. Agent nodes call `run_agent(...)`, a thin wrapper over your LLM client
(Anthropic Messages API) that: loads the agent's system prompt from agents/<X>.md, assembles the user
message from PlanState, calls the model at the agent's tier, parses+validates the JSON (one reask on a
parse failure), and records the model id + prompt hash into provenance. Module nodes call plain Python
in `compass.modules.*` — no model.

Everything marked `# IMPL:` is where you wire your real code. The graph structure (graph.py) and the
validation gate (routing.py) are complete and correct as written.
"""
from __future__ import annotations

from typing import Any

from langgraph.types import Send, interrupt

from .state import Claim, PlanState

# ---------------------------------------------------------------------------
# Agent runner + model tiers (see HOSTING.md for the actual model ids)
# ---------------------------------------------------------------------------

TIER = {
    "D2": "cheap", "R1": "top", "R4": "top", "R6": "mid",
    "R7": "mid", "R9": "mid", "R8": "top",
}


def run_agent(agent: str, user_message: str, *, expect_schema: dict) -> dict:
    """
    IMPL: call your LLM client at TIER[agent] with the system prompt from agents/<agent>.md and
    `user_message`; parse JSON; on parse/schema failure, reask ONCE; then raise to trigger escalation.
    Record model id + prompt hash into provenance. Enable prompt caching on the system block.
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Phase 1 — Collect  (v1: web form; the run suspends here waiting on a human)
# ---------------------------------------------------------------------------


def collect(state: PlanState) -> dict:
    # The load-bearing reason we use LangGraph: Phase 1 waits days/weeks on the family.
    # interrupt() durably suspends the run (Postgres checkpointer) until the form is submitted.
    dossier = interrupt({"awaiting": "student_dossier", "student_id": state["student_id"]})
    return {"dossier": dossier}


# ---------------------------------------------------------------------------
# Phase 2 — Understand
# ---------------------------------------------------------------------------


def r1_profile_analyst(state: PlanState) -> dict:
    msg = assemble_r1_user_message(state["dossier"])          # IMPL: fill the template in agents/R1_*.md
    return {"profile": run_agent("R1", msg, expect_schema=PROFILE_SCHEMA)}


def r1b_capacity_modeler(state: PlanState) -> dict:
    from compass.modules import capacity                      # IMPL
    return {"capacity": capacity.model(state["dossier"], state["profile"])}


# ---------------------------------------------------------------------------
# Phase 3 — Position (all deterministic modules)
# ---------------------------------------------------------------------------


def r2_neighbor_matcher(state: PlanState) -> dict:
    from compass.modules import neighbors                     # IMPL
    return {"cohort": neighbors.match(state["profile"])}


def r3_tiering(state: PlanState) -> dict:
    from compass.modules import tiering                       # IMPL (empirical-Bayes partial pooling)
    return {"tier_table": tiering.assign(state["cohort"])}


def r3b_admissibility(state: PlanState) -> dict:
    from compass.modules import admissibility                 # IMPL (pure arithmetic; no-evidence => no %)
    return {"verdicts": admissibility.screen(state["dossier"], state["cohort"])}


# ---------------------------------------------------------------------------
# Phase 4 — Strategize
# ---------------------------------------------------------------------------


def load_candidate_levers(state: PlanState) -> dict:
    from compass.modules import lift                          # IMPL (read D6 lift tables for this cohort)
    return {"candidate_levers": lift.candidates(state["cohort"], state["profile"])}


def r4_strategy_council(state: PlanState) -> dict:
    msg = assemble_r4_user_message(state)                     # IMPL: template in agents/R4_*.md
    return {"council": run_agent("R4", msg, expect_schema=COUNCIL_SCHEMA)}


def r5_scenario_simulator(state: PlanState) -> dict:
    from compass.modules import scenario                      # IMPL (re-runs R3 under lever completion)
    return {"scenario_result": scenario.simulate(state["council"], state["cohort"])}


def r5b_scheduler(state: PlanState) -> dict:
    from compass.modules import scheduler                     # IMPL (topological order under 4 constraints)
    return {"scheduled_levers": scheduler.assign(state["scenario_result"], state["capacity"])}


# ---------------------------------------------------------------------------
# Phase 5 — Plan  (R6 -> R7a -> R7 fan-out)
# ---------------------------------------------------------------------------


def r6_horizon_planner(state: PlanState) -> dict:
    msg = assemble_r6_user_message(state)                     # IMPL
    out = run_agent("R6", msg, expect_schema=HORIZON_SCHEMA)
    return {"multi_year_arc": out["multi_year_arc"], "current_year_plan": out["current_year_plan"]}


def r7a_modality_selector(state: PlanState) -> dict:
    from compass.modules import modality                      # IMPL (deterministic gap-type mapping)
    return {"modality": modality.select(state["current_year_plan"], state["capacity"])}


def fan_out_tasks(state: PlanState) -> list[Send]:
    """Map-reduce: one R7 branch per task (~8, in parallel) via the Send API."""
    tasks = [t for g in state["current_year_plan"]["goals"] for t in g["tasks"]]
    return [Send("r7_recommend_one", {"task": t, "state": state}) for t in tasks]


def r7_recommend_one(payload: dict) -> dict:
    """One task. Appends a single Recommendation; the `recommendations` reducer concatenates them."""
    state, task = payload["state"], payload["task"]
    from compass.modules import catalog                       # IMPL: pre-filter candidates by constraints
    candidates = catalog.prefilter(task, state["capacity"], state["dossier"])
    msg = assemble_r7_user_message(task, state["modality"][task["task_id"]], candidates, state)
    return {"recommendations": [run_agent("R7", msg, expect_schema=REC_SCHEMA)]}


# ---------------------------------------------------------------------------
# Phase 6 — Verify + write  (R8a -> R9 -> R8 -> renderer)
# ---------------------------------------------------------------------------


def r8a_validator(state: PlanState) -> dict:
    """
    The deterministic veto. Runs the nine checks. On PASS: emit claims_budget.
    On FAIL: emit a Rejection (routing.py reads it). Never mutates prior fields.
    """
    from compass.modules import validator                     # IMPL: the nine checks + injection tests
    result = validator.check(state)                           # -> {"ok": bool, "claims": [...], "rejection": Rejection|None}
    if result["ok"]:
        return {"claims_budget": [Claim(**c) for c in result["claims"]]}
    return {"rejections": [result["rejection"]], "iteration": 1}


def r9_narrative_writer(state: PlanState) -> dict:
    msg = assemble_r9_user_message(state)                     # IMPL: includes claims_budget + section spec
    return {"draft": run_agent("R9", msg, expect_schema=PLAN_SCHEMA)}


def r8_calibration_critic(state: PlanState) -> dict:
    msg = assemble_r8_user_message(state)                     # IMPL
    verdict = run_agent("R8", msg, expect_schema=VERDICT_SCHEMA)
    updates: dict[str, Any] = {"critic_verdict": verdict}
    if verdict["verdict"] != "pass":
        updates["iteration"] = 1
    return updates


def render(state: PlanState) -> dict:
    from compass.modules import renderer                      # IMPL: WeasyPrint over StrategicPlan + CSS
    return {"rendered_pdf_path": renderer.to_pdf(state["draft"], state)}


def human_escalation(state: PlanState) -> dict:
    """
    Reached after MAX_ITERS. Hand the reviewer the violated constraint, the offending claim, its
    Evidence, and the diff across retries. A plan NEVER ships having failed validation.
    """
    interrupt({
        "escalation": True,
        "student_id": state["student_id"],
        "rejections": state.get("rejections", []),
        "critic_verdict": state.get("critic_verdict"),
    })
    return {"escalated": True}


# ---------------------------------------------------------------------------
# Placeholders the IMPL points fill (schemas + user-message assemblers).
# Keep the schemas in one module so agents and validator share one definition.
# ---------------------------------------------------------------------------
PROFILE_SCHEMA = COUNCIL_SCHEMA = HORIZON_SCHEMA = REC_SCHEMA = {}
PLAN_SCHEMA = VERDICT_SCHEMA = {}


def assemble_r1_user_message(dossier): raise NotImplementedError
def assemble_r4_user_message(state): raise NotImplementedError
def assemble_r6_user_message(state): raise NotImplementedError
def assemble_r7_user_message(task, modality, candidates, state): raise NotImplementedError
def assemble_r9_user_message(state): raise NotImplementedError
def assemble_r8_user_message(state): raise NotImplementedError
