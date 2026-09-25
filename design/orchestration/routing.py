"""
Compass strategy engine — the validation gate + typed rejection routing.

This is the only place cycles exist in an otherwise acyclic graph, and they are TYPED: a violation
routes to the stage that can fix it (ARCHITECTURE.md §5), carrying an executable constraint change,
capped at MAX_ITERS, then escalated. A plan never ships having failed validation.
"""
from __future__ import annotations

from typing import Literal

from .state import MAX_ITERS, PlanState

# The map from a rejection target to the graph node that re-runs.
_TARGET_NODE = {
    "R3": "r3_tiering",
    "R4": "r4_strategy_council",
    "R6": "r6_horizon_planner",
    "R7": "r7a_modality_selector",  # re-enters the fan-out via r7a (scoped by task_id in the branch)
    "R9": "r9_narrative_writer",
}


def route_after_validator(
    state: PlanState,
) -> Literal["r9_narrative_writer", "r3_tiering", "r4_strategy_council",
             "r6_horizon_planner", "r7a_modality_selector", "human_escalation"]:
    """
    After R8a:
      - no rejection this pass  -> proceed to the writer (claims_budget was issued)
      - a rejection, iters left -> back to the stage that owns the fix
      - a rejection, iters spent -> human escalation
    """
    rejections = state.get("rejections", [])
    # A rejection with no consumed claims_budget means this pass FAILED.
    if not rejections or state.get("claims_budget"):
        return "r9_narrative_writer"

    if state.get("iteration", 0) >= MAX_ITERS:
        return "human_escalation"

    latest = rejections[-1]
    return _TARGET_NODE[latest.target]


def route_after_critic(
    state: PlanState,
) -> Literal["render", "r9_narrative_writer", "human_escalation"]:
    """
    After R8 (Calibration Critic):
      - pass      -> render
      - rewrite, iters left -> back to R9 with the findings
      - escalate / iters spent -> human
    """
    verdict = state.get("critic_verdict", {}).get("verdict", "pass")
    if verdict == "pass":
        return "render"
    if verdict == "escalate" or state.get("iteration", 0) >= MAX_ITERS:
        return "human_escalation"
    return "r9_narrative_writer"
