# `design/` — how the system was designed

**Read this first, because it decides which file wins.**

These documents are the design of Compass. Some of them describe what was
built; some describe what was intended before it was built. They are kept
because the reasoning in them is worth having — but where a document and the
code disagree, **the code is what runs**, and `ENGINE_FEEDBACK_LOG.md` at the
repo root is the record of why it ended up that way.

| File | Status | What it's for |
|---|---|---|
| `COMPASS_SHORT_PIPELINE.md` | **Current** | The per-step spec: what each of the 8 steps does, its input, its output, its prompt and its rubric. The closest document to what the engine actually does. |
| `ARCHITECTURE.md` | **Intent, partly built** | The DAG, the six phases, the typed `PlanState` contracts, `CapacityProfile`, R8a's nine checks, typed rejection routing, determinism boundaries, the untrusted-input rule. The reasoning holds; several component names do not match the code. |
| `HOSTING.md` | **Proposal** | Runtime on LangGraph Platform, model tiers, secrets, cost model, rollout. Nothing here has been deployed. |
| `V1_BUILD_PACKAGE.md` | **Intent** | The original build brief — why "mesh" was the wrong frame, what "v1 pragmatic" means, the build order that de-risks it. |
| `agents/` | **Superseded** | The original per-agent specs (D2, R1, R4, R6, R7, R8, R9). The live prompts are in `compass/prompts.py`; these predate roughly 30 of the rules in the feedback log. Useful for the reasoning behind each agent's job, not as prompt text. |
| `MODULES.md` | **Intent** | The deterministic modules as originally specified. Implemented set is in `compass/modules.py`. |
| `orchestration/` | **Target, not current** | A LangGraph skeleton — `graph.py`, `nodes.py`, `routing.py`, `state.py`, `langgraph.json`. The engine today runs through `compass/pipeline.py`, a plain sequential orchestrator. This is where it goes if and when it moves onto LangGraph. |

## What changed between the design and the build

Worth knowing before reading the older documents, because these are the
differences most likely to mislead:

- **Names.** Neighbor Matcher, Tiering Engine, Admissibility Screen, Scenario
  Simulator and Trajectory Scheduler became `modules.match_rank`, `two_paths`,
  `plan_goals` and `modules.tiering`. `docs/ORCHESTRATION.md` has the current
  map.
- **Gates.** The runtime acceptance gates in `compass/gates.py` did not exist in
  the original design. They are the main structural addition: nine of them, four
  verdicts, and they are what stops a bad step propagating.
- **Retrieval.** `compass/context.py` did not exist either. Before it, agents
  received only the previous step's JSON, which is why recommendations came back
  as placeholders.
- **The two critic loops** in the original design collapsed into one Critic plus
  the `gate_draft` check.
- **Rates.** The corpus was originally going to supply admit rates. It does not,
  and must not — see the feedback log and `data/README.md`.

## Where the current truth lives

| Question | File |
|---|---|
| What runs, in what order? | `compass/pipeline.py`, drawn in `docs/ORCHESTRATION.md` |
| What does each agent actually say? | `compass/prompts.py` |
| Why is this rule here? | `ENGINE_FEEDBACK_LOG.md` |
| What stops bad output? | `compass/gates.py`, `evals/GATES.md` |
| How is a step judged? | `evals/*_rubric.md` |
| What do I do first? | `docs/HANDOFF.md` |
