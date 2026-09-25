# Compass Strategy Engine — v1 Build Package

**What this is.** Everything you need to turn the Compass strategy engine from a design proposal
(`COMPASS_AGENT_ARCHITECTURE`) plus a hand-run prompt (`Compass_Plan_Generation_Prompt`) into a
running, hosted system that produces a strategic plan per student — automatically, reproducibly,
and for ~$2 of model spend per report.

It is built to **one architectural decision**, taken straight from your own doc:

> **An orchestrated DAG with a validation gate — not a single agent, and not an autonomous mesh.**
> Role-specialized LLM agents at fixed stages, deterministic engines for every number, a
> deterministic validator holding the veto, and a narrow adversarial critic for the judgment the
> validator cannot make.

If you read the plan you generated for Neerav by hand, this package is that same reasoning, decomposed
into steps a machine runs the same way every time.

---

## Read this first: why "mesh" is the wrong frame (and what to build instead)

You asked for a "multi-agent mesh." Your architecture doc argues explicitly *against* that, and it's
right for this product. Here's the one-paragraph version so the whole team is aligned:

A **mesh / autonomous swarm** — where agents decide at runtime who to call next — earns its keep when
the *shape of the output is unknown ahead of time* (open-ended research, coding a novel feature). A
Compass plan is the opposite: **the output shape is fixed** (cover → profile → priorities → two paths →
the plan → recommendations → parent actions). When the shape is fixed, dynamic delegation "buys
nothing, costs more, and destroys reproducibility." Worse, a mesh lets any agent emit any number, which
is exactly the failure this product cannot have — a fabricated admit probability in a document a family
pays for and makes decisions on.

So the topology is a **DAG** (directed acyclic graph): a fixed pipeline of stages, plus a small number
of *typed* cycles for the validation gate. Two design moves make it safe:

1. **Every number is produced by a deterministic module, never by an agent.** Agents only *interpret,
   plan, and write*. Cohort matching, tiering, the scenario sweep, scheduling, and validation are code.
   This is also why it's cheap: the expensive work is code, so the LLM only ever sees a summary.
2. **The validator runs *before* the writer, not after.** It computes the closed set of claims the
   writer is *allowed* to assert ("the claims budget"). The writer is *constrained*, not *corrected*.
   Fabrication becomes structurally unavailable rather than something you hope a smart critic catches.

That is the whole philosophy. Everything in this package serves it.

---

## What "v1 pragmatic" means here

Per your doc, v1 ships **7 LLM agents** and defers the rest. Concretely:

| In v1 | Deferred to v1.x / v2 |
|---|---|
| Web-form intake (structured) | R0 conversational Intake Interviewer |
| Parent types GPA / scores | R0b Document Ingestor (transcript/score-report parsing) |
| Hand-seeded catalog (~150 programs) | D4 Program Catalog Builder + D5 Catalog Verifier (automated) |
| Single-model 4-lens strategy council (R4) | v2 genuine multi-model council |
| The full deterministic core + validation gate | — (this ships in full; it's the safety story) |

**The 7 v1 agents:**

| # | Agent | Phase | Job | Model tier |
|---|---|---|---|---|
| 1 | **D2 · Profile Extractor** | Offline | Reddit post → strict `ApplicantOutcome` record (builds the corpus) | cheap |
| 2 | **R1 · Profile Analyst** | Understand | Dossier → spine / texture / temperament / tailwinds | top |
| 3 | **R4 · Strategy Council** | Strategize | Cohort + candidate levers → selected & sequenced lever set | top |
| 4 | **R6 · Horizon Planner** | Plan | Scheduled levers → goals + dated tasks | mid |
| 5 | **R7 · Recommendation Matcher** | Plan (fan-out) | Each task → 1 recommended + 2–3 alternates from catalog | mid |
| 6 | **R9 · Narrative Writer** | Write | Claims budget + plan state → the prose, in Compass voice | mid |
| 7 | **R8 · Calibration Critic** | Verify | Adversarially judge overpromising / sycophancy / drift | top |

Everything else in the runtime (`R1b, R2, R3, R3b, R5, R5b, R7a, R8a`, the renderer) is **deterministic
code, not an agent** — specs in `modules/MODULES.md`.

---

## Package map

```
compass-v1-build/
├── README.md                      ← you are here (how to proceed + roadmap)
├── ARCHITECTURE.md                ← the DAG, six phases, PlanState, data contracts, routing table
├── agents/                        ← paste-ready system prompts + I/O contracts (the 7 agents)
│   ├── D2_profile_extractor.md
│   ├── R1_profile_analyst.md
│   ├── R4_strategy_council.md
│   ├── R6_horizon_planner.md
│   ├── R7_recommendation_matcher.md
│   ├── R9_narrative_writer.md
│   └── R8_calibration_critic.md
├── modules/
│   └── MODULES.md                 ← deterministic module specs (numbers, scheduling, validation)
├── orchestration/                 ← the LangGraph app (this is what you deploy)
│   ├── state.py                   ← PlanState + every typed contract
│   ├── nodes.py                   ← one node per agent/module (agent calls stubbed to your LLM client)
│   ├── routing.py                 ← the validation gate + typed rejection routing
│   ├── graph.py                   ← StateGraph wiring: edges, Send fan-out, conditional gate
│   └── langgraph.json             ← LangGraph Platform deploy manifest
├── evals/
│   └── EVALS.md                   ← the release gate you build *before* the agents
└── HOSTING.md                     ← LangGraph Platform + Postgres deploy, models, cost, secrets
```

---

## How to proceed — the build order that de-risks it

Do **not** build agent-first. Your doc says "build the eval before the agents," and the reason is
that the deterministic core is where correctness lives; the agents are the easy, swappable part.
Recommended sequence:

**Step 0 — Stand up the data plane (1–2 weeks, mostly done).**
You already have the Reddit corpus (2,617 posts, 842 colleges) and IPEDS SQLite. Finish: run **D2**
over the corpus to produce `ApplicantOutcome` records; build the **Institution Store** (D3, pure ETL
from IPEDS); build the **alias map** (D7) canonicalizing college names to IPEDS `UNITID` — *this join
key is load-bearing; without it Reddit and IPEDS silently fail to join and colleges show n=0*; compute
**Lever Lift Tables** (D6). Hand-seed the ~150-program catalog as a CSV.

**Step 1 — Build the deterministic core + the validator (the heart).**
`modules/MODULES.md` specifies `R2` (neighbor matcher), `R3` (tiering, empirical-Bayes partial
pooling), `R3b` (admissibility), `R5` (scenario simulator), `R5b` (scheduler), `R7a` (modality
selector), `R1b` (capacity modeler), and **`R8a` (constraint validator)**. Write these as plain Python
with **unit tests**, not prompts. Build `R8a` and its injection test set first — it's the safety net
everything else relies on.

**Step 2 — Build the eval harness.** `evals/EVALS.md`. Aggregate calibration (bucket held-out
applicants by predicted band, compare to empirical frequency), a temporal held-out slice, and a
release gate (per-band calibration error + Brier score threshold). Plus the `R8a` injection set as
unit tests.

**Step 3 — Add the 7 agents.** Paste the prompts from `agents/` into your agent definitions. Wire each
to its node in `orchestration/nodes.py`. Because the validator already exists, a bad agent output is
caught, not shipped.

**Step 4 — Wire the graph & deploy.** `orchestration/graph.py` is the LangGraph `StateGraph`. Deploy to
LangGraph Platform per `HOSTING.md`. The checkpointer is the load-bearing reason for LangGraph: Phase 1
(intake) waits days/weeks on a human, so the run must durably suspend and resume.

**Step 5 — Human-review every plan, then earn review down.** Ship the service model (plan + review call +
response commitment). Review every plan until `R8a`/`R8` show measured catch rates; then review becomes
exception-only. *Escalation volume, not token spend, is the number to drive down.*

---

## The one number to re-verify before you quote anyone

The ~$2/report figure assumes current model prices and ~25 calls (only 3–4 top-tier; R7 fan-out is ~8).
Model prices are the single input to re-check before you put a cost in front of Neerav or Rob. See the
cost model in `HOSTING.md`.
