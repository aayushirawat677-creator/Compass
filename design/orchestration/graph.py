"""
Compass strategy engine — the LangGraph StateGraph.

This wires the six phases of ARCHITECTURE.md into a compiled graph. Phases are sequential; work inside
a phase runs in parallel. The only cycles are the typed validation gate (routing.py). The Postgres
checkpointer is what lets Phase 1 suspend for days/weeks and resume.

`graph` (compiled at import) is the object langgraph.json points the Platform at.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from . import nodes, routing
from .state import PlanState


def build() -> StateGraph:
    g = StateGraph(PlanState)

    # ---- nodes ----
    g.add_node("collect", nodes.collect)                       # Phase 1

    g.add_node("r1_profile_analyst", nodes.r1_profile_analyst)  # Phase 2
    g.add_node("r1b_capacity_modeler", nodes.r1b_capacity_modeler)

    g.add_node("r2_neighbor_matcher", nodes.r2_neighbor_matcher)  # Phase 3
    g.add_node("r3_tiering", nodes.r3_tiering)
    g.add_node("r3b_admissibility", nodes.r3b_admissibility)

    g.add_node("load_candidate_levers", nodes.load_candidate_levers)  # Phase 4
    g.add_node("r4_strategy_council", nodes.r4_strategy_council)
    g.add_node("r5_scenario_simulator", nodes.r5_scenario_simulator)
    g.add_node("r5b_scheduler", nodes.r5b_scheduler)

    g.add_node("r6_horizon_planner", nodes.r6_horizon_planner)  # Phase 5
    g.add_node("r7a_modality_selector", nodes.r7a_modality_selector)
    g.add_node("r7_recommend_one", nodes.r7_recommend_one)      # fan-out target

    g.add_node("r8a_validator", nodes.r8a_validator)            # Phase 6
    g.add_node("r9_narrative_writer", nodes.r9_narrative_writer)
    g.add_node("r8_calibration_critic", nodes.r8_calibration_critic)
    g.add_node("render", nodes.render)
    g.add_node("human_escalation", nodes.human_escalation)

    # ---- Phase 1 -> 2 ----
    g.add_edge(START, "collect")
    g.add_edge("collect", "r1_profile_analyst")
    g.add_edge("r1_profile_analyst", "r1b_capacity_modeler")

    # ---- Phase 2 -> 3 (position core; strictly sequential: R2 -> R3 -> R3b) ----
    g.add_edge("r1b_capacity_modeler", "r2_neighbor_matcher")
    g.add_edge("r2_neighbor_matcher", "r3_tiering")
    g.add_edge("r3_tiering", "r3b_admissibility")

    # ---- Phase 3 -> 4 ----
    g.add_edge("r3b_admissibility", "load_candidate_levers")
    g.add_edge("load_candidate_levers", "r4_strategy_council")
    g.add_edge("r4_strategy_council", "r5_scenario_simulator")
    g.add_edge("r5_scenario_simulator", "r5b_scheduler")

    # ---- Phase 4 -> 5 ----
    g.add_edge("r5b_scheduler", "r6_horizon_planner")
    g.add_edge("r6_horizon_planner", "r7a_modality_selector")
    # R7 fan-out: r7a -> (Send per task) -> r7_recommend_one -> join at r8a
    g.add_conditional_edges("r7a_modality_selector", nodes.fan_out_tasks, ["r7_recommend_one"])

    # ---- Phase 5 -> 6: the validation gate ----
    g.add_edge("r7_recommend_one", "r8a_validator")            # join: all task branches merge here
    g.add_conditional_edges(
        "r8a_validator",
        routing.route_after_validator,
        # every possible destination the router can return:
        ["r9_narrative_writer", "r3_tiering", "r4_strategy_council",
         "r6_horizon_planner", "r7a_modality_selector", "human_escalation"],
    )
    g.add_edge("r9_narrative_writer", "r8_calibration_critic")
    g.add_conditional_edges(
        "r8_calibration_critic",
        routing.route_after_critic,
        ["render", "r9_narrative_writer", "human_escalation"],
    )

    g.add_edge("render", END)
    g.add_edge("human_escalation", END)
    return g


# On LangGraph Platform the checkpointer/store are provisioned for you; compiling bare is correct.
# For local runs, compile with a Postgres checkpointer:
#     from langgraph.checkpoint.postgres import PostgresSaver
#     graph = build().compile(checkpointer=PostgresSaver.from_conn_string(DB_URI))
graph = build().compile()
