"""
The orchestrator — runs the 8-step short pipeline in order, threading one state object.
Agent steps -> compass.llm ; deterministic steps -> compass.modules.
"""
import json, os, sys
import settings
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from compass import llm, modules, context, gates
from compass.prompts import BY_STEP


def _agent(step, payload):
    system, tier = BY_STEP[step]
    user = json.dumps(payload, indent=2, default=str)
    return llm.ask_json(step, system, user, tier)


def _gated(step, payload, gate_fn, state, log, tier_retry=True):
    """Run a step, gate its output, retry ONCE with the failure as feedback. [#30]"""
    out = _agent(step, payload)
    res = gate_fn(out)
    if res.verdict == gates.RETRY and tier_retry:
        log(f"      gate: {res.verdict} — {'; '.join(res.failures)}  -> retrying once")
        p2 = dict(payload)
        p2["_gate_feedback"] = ("The previous attempt was rejected for: "
                               + "; ".join(res.failures) + ". Fix exactly these.")
        out = _agent(step, p2)
        res = gate_fn(out)
    state.setdefault("_gates", []).append(res)
    if res.verdict != gates.PASS:
        log(f"      gate: {res.verdict} — {'; '.join(res.failures) or res.notes}")
    return out, res


def run(intake: dict, log=print) -> dict:
    state = {"intake": intake}

    log("  1/9  Profile ............ reading the kid")
    g0 = gates.gate_intake(intake)
    state.setdefault("_gates", []).append(g0)
    if g0.verdict == gates.ESCALATE:
        log(f"  ✗ BLOCKED at intake: {'; '.join(g0.failures)}")
        state["blocked"] = g0.__dict__
        return state

    state["profile"], _ = _gated("profile", {"intake_json": intake},
                                 gates.gate_profile, state, log)
    profile = state["profile"]

    log("  2/9  Projected Profile .. backend best-case card")
    state["projected"] = _agent("projected", {"profile_json": profile,
                                              "intended": profile.get("intended", {})})

    log("  3/9  Match & Rank ....... pulling + ranking admit cards  [deterministic]")
    intended = profile.get("intended", {}).get("colleges", [])
    major = profile.get("intended", {}).get("major", "")
    mr = modules.match_rank(intended, major, state["projected"])
    state["cards"] = mr
    gr = gates.gate_retrieval(mr, settings.MIN_ADMITS_PER_SCHOOL
                              if hasattr(settings, "MIN_ADMITS_PER_SCHOOL") else 5)
    state.setdefault("_gates", []).append(gr)
    if gr.verdict == gates.ESCALATE:
        log(f"  ✗ BLOCKED at retrieval: {'; '.join(gr.failures)} — {gr.notes}")
        state["blocked"] = gr.__dict__
        return state
    if gr.verdict == gates.DEGRADE:
        log(f"      gate: DEGRADE — {'; '.join(gr.failures)}")
        state["degraded"] = gr.failures
    if mr.get("escalate_thin_data"):
        log("       ! thin data for the intended college(s) — flag for human review")

    log("  4/9  Gap Analyst ....... current profile vs cards")
    state["gap"], _ = _gated("gap", {"profile_json": profile, "cards_json": mr["cards"],
                                  "reference_json": context.for_gap(profile),
                                   "tally_json": mr["tally"],
                                   "grade": _grade(profile)}, gates.gate_gap, state, log)

    log("  5/9  Strategy .......... ranking gaps -> moves")
    state["strategy"], _ = _gated(
        "strategy",
        {"gap_map_json": state["gap"], "profile_json": profile,
         "reference_json": context.for_strategy(profile),
         "intended": profile.get("intended", {})},
        lambda o: gates.gate_strategy(o, state["gap"], profile.get("constraints", {})),
        state, log)

    log("  6/9  Two Paths ........ target & stretch variants")
    state["two_paths"], _ = _gated(
        "two_paths",
        {"moves_json": state["strategy"].get("selected_moves", []),
         "profile_json": profile,
         "admit_pattern_json": mr.get("tally", {}),
         "published_rates_json": context.for_writer(profile, _college_seed(intended)).get("published_rates", {}),
         "constraints_json": profile.get("constraints", {})},
        lambda o: gates.gate_two_paths(o, state["strategy"]),
        state, log)

    log("  7/9  Plan ............. goals, tasks, recommendations, tiers")
    state["plan_goals"], _ = _gated("plan_goals", {"moves_json": state["strategy"].get("selected_moves", []),
                                                "profile_json": profile, "grade": _grade(profile)}, lambda o: gates.gate_plan(o, state["strategy"]), state, log)
    # recommendations for near-term tasks (fan-out; mock returns one)
    constraints = profile.get("constraints", {})
    recs, blocked = [], []
    for goal in state["plan_goals"].get("current_year", [])[:4]:
        for task in goal.get("tasks", [])[:2]:
            pack = context.for_recs(profile, task)
            rec = _agent("plan_recs", {"task_json": task,
                                       "catalog_json": pack["catalog"],
                                       "debate_circuits_json": pack["debate_circuits"],
                                       "constraints_json": constraints})
            # Catalog had nothing usable for this task -> research it live, then verify.
            if rec.get("escalate") or not rec.get("recommendations"):
                found = llm.research_json(task.get("text") or str(task), constraints)
                rec["researched"] = found
                if found.get("recommendations"):
                    rec["recommendations"] = found["recommendations"]
                    rec["escalate"] = False
                    rec["source"] = "live research (verified)"
                else:
                    rec["escalate"] = True
                    rec["escalate_reason"] = found.get("notes")
            ok, violations = modules.constraint_guardrail(rec, constraints)   # 6c guardrail
            if ok:
                recs.append(rec)
            else:
                blocked.append({"task": task.get("task_title"), "violations": violations})
    state["recommendations"] = recs
    grc = gates.gate_recs(recs); state.setdefault("_gates", []).append(grc)
    if grc.verdict == gates.ESCALATE:
        log(f"      gate: ESCALATE — {'; '.join(grc.failures)} ({grc.notes})")
    state["blocked_by_guardrail"] = blocked
    if blocked:
        log(f"       ! {len(blocked)} recommendation(s) blocked by the constraint guardrail")
    # 6d tiering seed
    state["college_tiers"] = modules.tiering(intended, _college_seed(intended))

    log("  8/9  Writer ........... composing the plan")
    state["draft"] = _agent("writer", {"plan_json": {"profile": profile, "gap": state["gap"],
                                        "strategy": state["strategy"], "plan": state["plan_goals"], "two_paths": state.get("two_paths", {}),
                                        "recommendations": recs, "college_tiers": state["college_tiers"]},
                                        "profile_json": profile,
                                        "worry": constraints.get("stated_worry", ""),
                                        "numbers_json": {"tiers": state["college_tiers"], "tally": mr["tally"]},
                                        "reference_json": context.for_writer(profile, _college_seed(intended))})

    log("  9/9  Critic ........... tone / honesty / plain English")
    verdict = _agent("critic", {"strategic_plan_json": state["draft"]})
    state["critic"] = verdict

    # the quality trail — what degraded, and where  [#30]
    state["quality"] = gates.summarise(state.get("_gates", []))
    state.pop("_gates", None)
    q = state["quality"]
    if q["overall"] != gates.PASS:
        log(f"\n  quality trail: {q['overall']}")
        for row in q["trail"]:
            if row["verdict"] != gates.PASS:
                log(f"      {row['step']:12s} {row['verdict']:9s} {'; '.join(row['failures'])[:70]}")
    if verdict.get("verdict") != "pass":
        log(f"       ! critic: {verdict.get('verdict')} — {len(verdict.get('findings', []))} note(s)")

    return state


def _grade(profile):
    return profile.get("cover", {}).get("grade") or \
        profile.get("intended", {}).get("grade") or "9"


def _college_seed(intended):
    seed = [{"college": c, "tier": "reach"} for c in (intended or [])]
    seed += [{"college": "Carnegie Mellon", "tier": "reach"},
             {"college": "Georgia Tech", "tier": "target"},
             {"college": "UIUC", "tier": "target"}]
    return seed
