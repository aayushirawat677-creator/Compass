"""
The orchestrator — runs the 8-step short pipeline in order, threading one state object.
Agent steps -> compass.llm ; deterministic steps -> compass.modules.
"""
import json, os, sys
import settings
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from compass import llm, modules, context, gates, appraise
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

    log("  1/10 Profile ............ reading the kid")
    g0 = gates.gate_intake(intake)
    state.setdefault("_gates", []).append(g0)
    if g0.verdict == gates.ESCALATE:
        log(f"  ✗ BLOCKED at intake: {'; '.join(g0.failures)}")
        state["blocked"] = g0.__dict__
        return state

    state["profile"], _ = _gated("profile", {"intake_json": intake},
                                 gates.gate_profile, state, log)
    profile = state["profile"]

    log("  2/10 Projected Profile .. backend best-case card")
    state["projected"] = _agent("projected", {"profile_json": profile,
                                              "intended": profile.get("intended", {})})

    log("  3/10 Match & Rank ....... pulling + ranking admit cards  [deterministic]")
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

    # Computed HERE, not before Two Paths, so the steps that DECIDE can see it. [#52]
    # Gap measures distance against it; Strategy picks the rung to aim at; Plan sizes
    # the goals to it. Producing it late meant the two steps that choose what the
    # student should actually do were the only ones working blind.
    state["admit_pattern"] = modules.admit_pattern_by_school(
        intended or _seed_names(intended), major)
    thin = [x["college"] for x in state["admit_pattern"].get("schools", [])
            if not x.get("sufficient")]
    if thin:
        log(f"       ! too few admits held to assess fit at: {', '.join(thin)}")

    log("  4/10 Gap Analyst ....... current profile vs cards")
    state["gap"], _ = _gated("gap", {"profile_json": profile, "cards_json": mr["cards"],
                                  "reference_json": context.for_gap(profile),
                                   "tally_json": mr["tally"],
                                   "admit_pattern_json": state["admit_pattern"],
                                   "grade": _grade(profile)}, gates.gate_gap, state, log)

    # 4b. APPRAISER — one call per activity. Sits AFTER gap so it can judge each thread
    # against what admits to THIS student's schools actually held, and BEFORE strategy,
    # which consumes the verdicts as its CONVERT move. Until this existed, an activity
    # with a low ceiling was carried to grade 12 because no step could ask whether it
    # would ever amount to anything. [#59]
    acts = profile.get("activities") or []
    log(f"  4b/10 Appraiser ........ how far can each of {len(acts)} threads go?")
    appraisals = []
    for act in acts:
        cached = appraise.lookup(act.get("type_name") or act.get("name"))
        out = _agent("appraiser", {
            "grade": _grade(profile),
            "activity_json": act,
            "admit_pattern_json": state["admit_pattern"],
            "intended_json": profile.get("intended", {}),
            "cached_json": cached or {},
            "candidates_json": [] if cached else appraise.candidates(
                f"{act.get('name','')} {act.get('detail','')}"),
        })
        appraisals.append(out)
        # Write layer-1 knowledge back so the next family with this activity type is
        # cheaper. A rejected write is logged, never fatal — the cache is a convenience.
        ok, why = appraise.record(out.get("type_knowledge") or {})
        if not ok:
            log(f"        cache: not stored for {act.get('name','?')!r} — {why}")
    state["appraisals"] = appraisals
    ga = gates.gate_appraisal(appraisals, acts)
    state.setdefault("_gates", []).append(ga)
    if ga.failures:
        log(f"      gate: {ga.verdict} — {'; '.join(ga.failures[:2])}")
    asked = [a for a in appraisals if a.get("needs_family_input")]
    if asked:
        log(f"        {len(asked)} thread(s) go back to the family as a question")

    log("  5/10 Strategy .......... ranking gaps -> moves")
    state["strategy"], _ = _gated(
        "strategy",
        {"gap_map_json": state["gap"], "profile_json": profile,
         "reference_json": context.for_strategy(profile),
         "admit_pattern_json": state["admit_pattern"],
         "appraisals_json": appraisals,
         "intended": profile.get("intended", {})},
        lambda o: gates.gate_strategy(o, state["gap"], profile.get("constraints", {})),
        state, log)

    log("  6/10 Two Paths ........ target & stretch variants")
    state["two_paths"], _ = _gated(
        "two_paths",
        {"moves_json": state["strategy"].get("selected_moves", []),
         "profile_json": profile,
         # Per-school admit pattern, not one corpus-wide tally. Without this, every
         # school came back "not assessed" — correctly, since the step was never
         # handed an n it could assert fit from. [#44]
         "admit_pattern_json": state["admit_pattern"],
         "corpus_tally_json": mr.get("tally", {}),
         "published_rates_json": context.for_writer(profile, _college_seed(intended)).get("published_rates", {}),
         "constraints_json": profile.get("constraints", {})},
        lambda o: gates.gate_two_paths(o, state["strategy"]),
        state, log)

    log("  7/10 Plan ............. goals, tasks, recommendations, tiers")
    grade = _grade(profile)
    state["capacity"] = modules.capacity_budget(profile, grade)
    state["capacity_summer"] = modules.capacity_budget(profile, grade, "summer")
    state["stage_bands"] = modules.stage_bands(grade)
    log(f"       · capacity: {state['capacity']['free_hours_per_week']} h/week free "
        f"of {state['capacity']['total_hours_per_week']} ({state['capacity']['committed_hours_per_week']} committed)")
    state["plan_goals"], _ = _gated(
        "plan_goals",
        {"moves_json": state["strategy"].get("selected_moves", []),
         "profile_json": profile, "grade": grade,
         "capacity_json": state["capacity"],
         "summer_capacity_json": state["capacity_summer"],
         "stage_bands_json": state["stage_bands"],
         "admit_pattern_json": state["admit_pattern"],
         # The ladders the later grades name come from here, already source-checked.
         # Without them grade 11 reads "carry it one rung further" and names no rung. [#61]
         "appraisals_json": appraisals},
        lambda o: gates.gate_plan(o, state["strategy"]), state, log)

    # Correct step order does not make the plan obey. The appraiser runs before strategy
    # and the plan and both are TOLD to honour it; nothing checked that they did. [#60]
    for g in (gates.gate_honours_appraisal(state["plan_goals"], appraisals),
              gates.gate_open_questions(state["plan_goals"], appraisals),
              gates.gate_horizon(state["plan_goals"], grade, appraisals)):
        state.setdefault("_gates", []).append(g)
        if g.failures:
            log(f"      gate: {g.verdict} ({g.step}) — {'; '.join(g.failures[:2])}")
    # recommendations for near-term tasks (fan-out; mock returns one)
    constraints = profile.get("constraints", {})
    recs, blocked = [], []
    for goal in state["plan_goals"].get("current_year", [])[:4]:
        for task in goal.get("tasks", [])[:2]:
            pack = context.for_recs(profile, task)
            catalog = list(pack["catalog"])

            # RESEARCH FIRST WHEN THE REGISTRY DOES NOT COVER THIS. [#45]
            # The registry is real for debate and thin everywhere else. Sending an
            # agent an empty catalog and hoping it escalates wastes a call and
            # produces a weaker recommendation than searching properly. So when the
            # registry has nothing for this task's activity, research BEFORE asking,
            # and hand the verified findings over as the catalog. Cost is not the
            # constraint here; a real, bookable, verified option is.
            pre = None
            if not pack.get("coverage"):
                pre = llm.research_json(_task_text(task), constraints,
                                        max_searches=settings.RESEARCH_MAX_SEARCHES)
                for r in (pre.get("recommendations") or []):
                    r.setdefault("source", "live research (verified)")
                    catalog.append(r)
                log(f"       · registry has no {pack.get('activity') or 'match'} rows — "
                    f"researched live, {len(pre.get('recommendations') or [])} verified option(s)")

            rec = _agent("plan_recs", {"task_json": task,
                                       "catalog_json": catalog,
                                       "debate_circuits_json": pack["debate_circuits"],
                                       "registry_covers": bool(pack.get("coverage")),
                                       "constraints_json": constraints})
            if pre is not None:
                rec["researched"] = pre
            # Still nothing usable -> one more live pass, then escalate honestly.
            if rec.get("escalate") or not (rec.get("recommendations") or rec.get("primary")):
                found = llm.research_json(_task_text(task), constraints,
                                          max_searches=settings.RESEARCH_MAX_SEARCHES)
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
    # Sum the YEAR, not just each item. [#51]
    state["budget"] = modules.budget_ledger(recs, constraints)
    b = state["budget"]
    log(f"       · budget: ${b['year_total']:.0f} of ${b['year_ceiling'] or 0:.0f} for the year"
        + (f", ${b['summer_total']:.0f} of ${b['summer_ceiling'] or 0:.0f} for summer" if b['summer_total'] else ""))
    if not b["within_budget"]:
        log(f"       ! over budget by ${b['over_by'] + b['summer_over_by']:.0f} — "
            f"largest items: {[i['name'] for i in b['items'][:2]]}")
    for x in b["geographically_blocked"]:
        log(f"       ! dropped, outside the family's region: {x['name']}")
    grc = gates.gate_recs(recs); state.setdefault("_gates", []).append(grc)
    gb = gates.gate_budget(state["budget"]); state.setdefault("_gates", []).append(gb)
    if gb.verdict != gates.PASS:
        log(f"      gate: {gb.verdict} — {'; '.join(gb.failures)}")
    if grc.verdict == gates.ESCALATE:
        log(f"      gate: ESCALATE — {'; '.join(grc.failures)} ({grc.notes})")
    state["blocked_by_guardrail"] = blocked
    if blocked:
        log(f"       ! {len(blocked)} recommendation(s) blocked by the constraint guardrail")
    # 6d tiering seed
    state["college_tiers"] = modules.tiering(intended, _college_seed(intended))

    log("  8/10 Writer ........... composing the plan")
    state["draft"] = _agent("writer", {"plan_json": {"profile": profile, "gap": state["gap"],
                                        "strategy": state["strategy"], "plan": state["plan_goals"], "two_paths": state.get("two_paths", {}),
                                        "recommendations": recs, "college_tiers": state["college_tiers"]},
                                        "profile_json": profile,
                                        "worry": constraints.get("stated_worry", ""),
                                        "numbers_json": {"tiers": state["college_tiers"], "tally": mr["tally"]},
                                        "stage_bands_json": state["stage_bands"],
                                        "capacity_json": state["capacity"],
                                        "reference_json": context.for_writer(profile, _college_seed(intended))})

    # gate_draft was defined, documented and drawn on the diagram but never called —
    # the writer's output reached the critic ungated. [#42]
    allowed = []
    for row in (context.for_writer(profile, _college_seed(intended))
                .get("published_rates", {}) or {}).values():
        if isinstance(row, dict):
            r = row.get("rate_pct", row.get("rate"))
            if r is not None:
                allowed.append(r)
    tally = mr.get("tally", {})
    allowed += [tally.get("gpa_modal_share", 0) * 100, tally.get("test_modal_share", 0) * 100]
    gd = gates.gate_draft(state["draft"], [a for a in allowed if a is not None])
    state.setdefault("_gates", []).append(gd)
    if gd.verdict != gates.PASS:
        log(f"      gate: {gd.verdict} — {'; '.join(gd.failures)}")
    # Did every goal the plan produced survive into the document? [#50]
    gdoc = gates.gate_document(state["draft"], state["plan_goals"])
    state.setdefault("_gates", []).append(gdoc)
    if gdoc.verdict != gates.PASS:
        log(f"      gate: {gdoc.verdict} — {'; '.join(gdoc.failures)}")

    log("  9/10 Critic ........... tone / honesty / plain English")
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


def _task_text(task):
    if isinstance(task, str):
        return task
    for k in ("task", "task_title", "text", "goal"):
        if task.get(k):
            return str(task[k])
    return json.dumps(task, default=str)[:400]


def _seed_names(intended):
    return [c["college"] if isinstance(c, dict) else c for c in _college_seed(intended)]


def _college_seed(intended):
    seed = [{"college": c, "tier": "reach"} for c in (intended or [])]
    seed += [{"college": "Carnegie Mellon", "tier": "reach"},
             {"college": "Georgia Tech", "tier": "target"},
             {"college": "UIUC", "tier": "target"}]
    return seed
