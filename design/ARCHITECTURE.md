# Compass Strategy Engine — Architecture (v1)

This is the contract every other file in the package conforms to. If a prompt, module, or node
disagrees with this file, this file wins.

---

## 1. The shape: an orchestrated DAG with a validation gate

```
                          OFFLINE DATA PLANE (batch, amortized across all students)
   Reddit ──D1──▶ posts ──D2*──▶ ApplicantOutcome Corpus ──┐
   IPEDS  ──D3──▶ Institution Store ───────────────────────┼──D6──▶ Lever Lift Tables
   (hand-seeded CSV) ──▶ Program Catalog                    │  D7 (alias map: name → UNITID)
                                                            ▼
════════════════════════════════ RUNTIME (per student) ════════════════════════════════

 Phase 1  COLLECT      [web form] ──▶ StudentDossier                      (v1: form, not R0/R0b)
 Phase 2  UNDERSTAND   R1* ─▶ profile ─▶ R1b ─▶ CapacityProfile
 Phase 3  POSITION     R2 ─▶ cohort ─▶ R3 ─▶ tier_table ─▶ R3b ─▶ verdicts    (all modules)
 Phase 4  STRATEGIZE   R4* (strategy council) ─▶ R5 ─▶ R5b ─▶ scheduled_levers
 Phase 5  PLAN         R6* ─▶ goal_tree ─▶ R7a ─▶ modality ─▶  R7* ⇉ (fan-out per task)
 Phase 6  VERIFY+WRITE R8a ─▶ claims_budget ─▶ R9* ─▶ draft ─▶ R8* ─▶ renderer ─▶ StrategicPlan
                          │                                       │
                          └────────── typed rejection edges ──────┘ (max 3 iters, then human)

 * = LLM agent. Everything else is deterministic code.
```

**Two topology choices that are the whole safety story:**

1. **`R8a` (validator) sits before `R9` (writer).** It computes the *claims budget* — the closed set
   of claim IDs the writer may assert, each bound to an `Evidence` record — before the writer runs.
   The writer is constrained, not corrected. An uncited number is a mechanical rejection.
2. **Rejection edges are typed.** A violation routes back to the *stage that can actually fix it*,
   carrying an executable constraint change, not a complaint. See §5.

---

## 2. The six phases

> Everything inside a phase runs in parallel; phases are sequential.

| Phase | Steps | Mode | Wall clock | Output |
|---|---|---|---|---|
| 1 · Collect | web form (→ later R0, R0b) | structured input | **days–weeks** (waits on human) | `StudentDossier` |
| 2 · Understand | **R1** (agent), R1b (module) | 1 top-tier call, then scoring | seconds | profile + `CapacityProfile` |
| 3 · Position | R2 → R3 → R3b (modules) | deterministic | sub-second | cohort, `tier_table`, verdicts |
| 4 · Strategize | **R4** (agent) → R5 → R5b (modules) | 1 call, then sweep + schedule | seconds | classified levers, reach-plan table, scheduled levers |
| 5 · Plan | **R6** (agent), R7a (module), **R7** fan-out (agent) | ~6 goals, verdicts, ~8 tasks parallel | ~1 min | `goal_tree` with recommendations |
| 6 · Verify+write | R8a (module) → **R9** → **R8** (agents) → renderer | validate, write, judge, render | ~1–2 min | rendered `StrategicPlan` PDF |

Phases 2–6 complete in **3–4 minutes**. Phase 1 dominates elapsed time. ~**25 model calls** per report,
only 3–4 top-tier; R7 alone ≈ 8.

**Fan-out points:** D2 (batch over posts, offline) and **R7 (map-reduce over ~8 tasks)** — the primary
runtime fan-out, via LangGraph's `Send` API.

---

## 3. The governing rule (memorize this)

> **Every number in the final document is produced by a module, never by an agent. Agents only
> interpret, plan, and write.**

This is both the accuracy story *and* the cost story. The five expensive operations are made
deterministic instead of generative: cohort matching (R2), tier assignment (R3), the scenario sweep
(R5), lift statistics (D6), and rendering. The LLM only ever sees a *summary* of the cohort — a few
thousand tokens — never the corpus. Multi-agent here is *cheaper* than single-agent, because splitting
the work is what lets most of it be code.

**Agent vs module:**
- **Agent** = an LLM-backed step with a prompt, an output schema, a model tier, and its own failure
  modes. (D2, R1, R4, R6, R7, R9, R8)
- **Module** = deterministic code that needs unit tests, not prompt engineering. (everything else)

---

## 4. Shared state: one typed `PlanState`

A single typed `PlanState` object is threaded through the graph. **Stages append and never mutate prior
fields**, so any claim is traceable to the stage that produced it. Append-only / parallel-merged fields
use LangGraph reducers so R7's parallel branches merge without clobbering. Full definitions live in
`orchestration/state.py`; this is the contract.

### 4.1 The typed data contracts

| Contract | Produced by | Consumed by | What it holds |
|---|---|---|---|
| `StudentDossier` | web form (R0/R0b later) | R1, R1b, R3b | student facts: name, grade, school, location, GPA/test (or null+confirm), activities, declared college list, budget, geography, hours, fixed commitments, accommodations, hard-nos, stated worry, intended major |
| `Profile` | **R1** | R4, R6, R9 | `spine`, `texture[]` (each maintain/demote), `temperament[]`, `tailwinds[]` |
| `CapacityProfile` | R1b | R4, R6, R7, R7a, R8a | hard constraints (see §4.2) |
| `ApplicantOutcome` | **D2** | R2, D6 | one Reddit applicant: GPA (UW/W), per-section test, AP count+load, hooks, school type, income band, region, ranked ECs, awards w/ level, LOR/interview self-rating, per-college decisions w/ round |
| `Institution` | D3 | R2, R3, R3b | IPEDS: applicants/admits, test percentiles, `ADMCON` factors, aid, program size, `UNITID` |
| `Cohort` | R2 | R3, R3b, R4 | k nearest `ApplicantOutcome` records + per-college outcomes + `radius` + weak-cohort flag |
| `tier_table` | R3 | R3b, R4, R5 | per school: band (Far Reach/Reach/Target/Likely) + posterior interval + n |
| `AdmissibilityVerdict` | R3b | R6, R9 | per declared school: evidence-supported / outside-range / no-evidence + a proposed balanced list |
| `Lever` | D6 (candidates), **R4** (selected) | R5, R5b | id, description, domain, corpus_support, cohort_n, est_hours, est_cost, status (supported/unsupported) |
| `scenario_result` | R5 | R5b, R6 | Big Mover vs Compounder classification + reach-plan tier-shift table |
| `scheduled_levers` | R5b | R6 | levers assigned to years under deadline/eligibility/prereq/capacity constraints |
| `MultiYearArc` + `CurrentYearPlan` | **R6** | R7a, R7, R9 | coarse arc + dated current-year goal tree (≤6 goals) |
| `ModalityVerdict` | R7a | R7, R8a | per task: free-self-serve / AI-tool / paid-human / institution |
| `ProgramCatalogEntry` | hand-seed (D4/D5 later) | R7 | name, category, domain tags, cost, format, location, deadline window, selectivity, eligible grades, URL, last_verified, confidence |
| `Recommendation` | **R7** | R8a, R9 | per task: 1 recommended + 2–3 alternates, each w/ cost/format/link/why/choose_if + guardrail_check |
| `Evidence` | every module producing a number | R8a | `{source, n, query, retrieved_at}` — attached to every numeric claim |
| `claims_budget` | R8a | R9, R8 | the closed set of claim IDs R9 may assert, each bound to its `Evidence` |
| `StrategicPlan` | R9 → renderer | family | the final typed doc → PDF |
| `ReportProvenance` | graph | audit / re-run | corpus snapshot id, lift-table version, catalog version, institution-store version, model ids, prompt hashes |

### 4.2 `CapacityProfile` — the hard-constraint object (field → derived from → consumed by)

| Field | Derived from | Consumed by |
|---|---|---|
| `discretionary_hours_per_week` | hours + fixed commitments + grade homework norm | R6 hard cap, R8a |
| `perceived_load_headroom` | love scores + quit-intent count | R6, R8a (**strongest single signal**) |
| `marginal_load_tolerance` | tolerance answers | R6 sequencing |
| `pressure_regime` | competitiveness × stakes response | R7 (whether to recommend competition) |
| `novelty_tolerance` | openness to new things | R7 (gates cold-start recs) |
| `autonomy_ratio` | parent-driven vs child-driven activity split | R4, R6 (**a parent-driven spine is fragile**) |
| `attrition_risk` | quit history + fragility signals | R7 per recommendation |
| `executive_function_support` | 504/IEP/ADHD + structure needs | R7 format filter |
| `recharge_mode` | how the student recovers | R7 (residential vs local, cohort vs 1:1) |

---

## 5. The validation gate & typed rejection routing

`R8a` runs the nine deterministic checks. On pass, it emits the `claims_budget`. On any failure, it
emits a **typed rejection edge** that routes to the stage that can fix it, carrying the constraint
change. **Capped at 3 iterations** (counter in state); a third failure escalates to a human reviewer —
a plan **never ships having failed validation**.

### R8a's nine checks
1. Every number traces to an `Evidence` record.
2. No tier claim on insufficient n / too-wide posterior interval.
3. **No tier percentage on a no-evidence school.** (absolute)
4. No program / price / URL absent from the catalog.
5. Total cost within family ceiling **and** per-year cost within annual ceiling.
6. Total weekly hours within `CapacityProfile` budget.
7. No task past its deadline window.
8. No paid recommendation where R7a says free suffices (absent recorded justification).
9. No tier improvement exceeding what R5 computed.

### Typed rejection routing table

| Violation | Routes to | Constraint change carried |
|---|---|---|
| Tier claim on insufficient n / too-wide interval | **R3** | Drop college, widen band, or raise n floor |
| Weekly hours exceed CapacityProfile budget | **R6** | Reduce committed hours by measured overage |
| Cost exceeds family ceiling | **R7** | Re-match within reduced ceiling |
| Program / price / URL absent from catalog | **R7** | Re-match against catalog entries only |
| Tier improvement beyond what R5 computed | **R4** | Re-select levers within measured lift |
| Narrative overpromises vs claims budget | **R9** | Rewrite, citing approved claim IDs only |

`R8` (Calibration Critic) is separate: a *judgment* reviewer, not a fact checker. It runs after R9 and
can send "overreach: rewrite" back to R9, or escalate after 3 failures. It never touches numbers —
that's R8a's job.

---

## 6. Determinism boundaries (honesty caveats baked into the design)

- **Numbers are exactly reproducible; prose is not.** Pinned inputs + deterministic modules guarantee
  identical tiers/levers/recommendations on a re-run. LLM stages reproduce only approximately, even at
  temperature 0. This is why `ReportProvenance` exists.
- **Lever effects are associational, not causal.** The corpus licenses "cohort patterns," not
  promises. Report them that way. Big Mover defaults conservative when evidence is thin.
- **Posting-selection bias is unfixable from inside the corpus.** Corpus-internal eval validates the
  *arithmetic*, never real-world calibration. Own-client outcomes are the only real-calibration path.
- **Multi-year sequencing is constructed, not observed.** The end state is measured; the path is
  planning logic.
- **Bands are profile-conditional, and self-selection is signal, not noise.** Duke at 26% in-corpus vs
  ~6% published is the actual signal for this profile — do not "correct" it to the published rate. Every
  band says: *reflects this student's profile given the work each plan describes — not published rates.*

---

## 7. Untrusted-input rule (security)

D2 and R0b (later) ingest uncontrolled content (Reddit posts, uploaded docs). Rule: untrusted text is
**data, never instruction**. Never concatenate it into instruction position; use constrained-schema
returns; keep visible separation; verify catalog entries twice (D5 later). Screen the corpus for
coordinated posting (near-identical phrasing bursts, new-account clusters, volume anomalies) before D6
recomputes.
