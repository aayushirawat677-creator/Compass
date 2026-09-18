"""
Compass strategy engine — PlanState and typed contracts.

The whole graph threads ONE PlanState. Rule: stages APPEND, they never mutate a prior field,
so every claim is traceable to the stage that produced it. Parallel branches (R7 fan-out) merge
through reducers, never by clobbering.

This is the runtime source of truth for the contracts described in ARCHITECTURE.md §4.
Types are intentionally light (TypedDict/dataclass) so they serialize cleanly into the checkpointer.
"""
from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Optional, TypedDict

# ---------------------------------------------------------------------------
# Evidence + provenance — attached to every number, never optional on a claim
# ---------------------------------------------------------------------------


@dataclass
class Evidence:
    source: str          # e.g. "cohort", "IPEDS ADM2024", "lift_table:duke_ss_award"
    n: Optional[int]     # cohort size behind the claim (None for IPEDS-published)
    query: str           # the exact query/derivation that produced the number
    retrieved_at: str    # ISO timestamp / snapshot id


@dataclass
class ReportProvenance:
    corpus_snapshot_id: str
    lift_table_version: str
    catalog_version: str
    institution_store_version: str
    model_ids: dict[str, str]        # {"R1": "...", "R4": "...", ...}
    prompt_hashes: dict[str, str]


# ---------------------------------------------------------------------------
# Claims budget — the closed set R9 is allowed to assert (issued by R8a)
# ---------------------------------------------------------------------------


@dataclass
class Claim:
    claim_id: str
    text: str            # the human-readable claim ("Duke sits in the Reach band for this profile")
    evidence: Evidence


# ---------------------------------------------------------------------------
# Typed rejection — the executable constraint change R8a/R8 route upstream
# ---------------------------------------------------------------------------

RejectTarget = Literal["R3", "R4", "R6", "R7", "R9"]


@dataclass
class Rejection:
    target: RejectTarget
    violation: str                    # which of the nine checks / which judgment finding
    constraint_change: dict[str, Any] # executable: {"cost_ceiling": 4200} / {"drop_college": "Duke"} ...
    task_id: Optional[str] = None     # set when the rejection is scoped to one R7 fan-out branch


# ---------------------------------------------------------------------------
# The PlanState
# ---------------------------------------------------------------------------


def _last(a, b):
    """Reducer: later write wins (for single-owner fields written once per stage)."""
    return b if b is not None else a


class PlanState(TypedDict, total=False):
    # ---- provenance / control ----
    student_id: str
    provenance: ReportProvenance
    iteration: Annotated[int, operator.add]          # validation-gate counter; cap at MAX_ITERS
    rejections: Annotated[list[Rejection], operator.add]  # append-only audit of every reject
    escalated: bool                                   # set True when we hand off to a human

    # ---- Phase 1: Collect ----
    dossier: dict                                     # StudentDossier (web form output)

    # ---- Phase 2: Understand ----
    profile: dict                                     # R1 output (Profile)
    capacity: dict                                    # R1b output (CapacityProfile)

    # ---- Phase 3: Position (deterministic) ----
    cohort: dict                                      # R2
    tier_table: dict                                  # R3
    verdicts: dict                                    # R3b (AdmissibilityVerdict per school)

    # ---- Phase 4: Strategize ----
    candidate_levers: list[dict]                      # D6 (read from lift tables at entry)
    council: dict                                     # R4 output (selected/dropped/tensions)
    scenario_result: dict                             # R5
    scheduled_levers: list[dict]                      # R5b

    # ---- Phase 5: Plan ----
    multi_year_arc: list[dict]                        # R6
    current_year_plan: dict                           # R6 (goal tree)
    modality: dict                                    # R7a  {task_id: ModalityVerdict}
    # R7 fan-out: each task branch appends one Recommendation; reducer concatenates
    recommendations: Annotated[list[dict], operator.add]

    # ---- Phase 6: Verify + write ----
    claims_budget: list[Claim]                        # R8a (on pass)
    draft: dict                                       # R9 (StrategicPlan)
    critic_verdict: dict                              # R8
    rendered_pdf_path: str                            # renderer


MAX_ITERS = 3   # validation-gate iteration cap; a 3rd failure escalates to a human
