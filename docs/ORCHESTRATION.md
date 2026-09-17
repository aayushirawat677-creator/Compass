# Compass — agent orchestration

How the pieces actually run. Every box below exists in the code: agent steps
resolve through `compass/prompts.py::BY_STEP`, deterministic steps through
`compass/modules.py`, gates through `compass/gates.py`, and the order is
`compass/pipeline.py::run()`.

**Shape grammar:** stadium = LLM agent · rectangle = deterministic module ·
cylinder = stored data · hexagon = runtime gate · parallelogram = input ·
dashed edge = failure path (retry, rewrite, escalate).

```mermaid
flowchart TB

  subgraph OFFLINE["REFERENCE DATA — built once, read by every run"]
    direction TB
    SRC[/"Reddit results posts<br/>parsed + verified"/]
    PUB[/"Published sources<br/>CDS / official"/]
    CORPUS[("corpus.csv<br/>2,613 students")]
    APPROWS[("application rows<br/>30,414 after explode")]
    RATES[("admit_rates.json<br/>33 schools + aliases")]
    FIND[("findings.json")]
    CIRC[("tabroom_circuits.csv")]
    CAT[("catalog.csv<br/>verified programs")]
    SRC --> CORPUS
    CORPUS -->|"load_corpus(applications=True)"| APPROWS
    PUB -->|"refresh_rates.ensure_rate()"| RATES
    CTX["context.py<br/>retrieval layer"]
    RATES --> CTX
    FIND --> CTX
    CIRC --> CTX
    CAT --> CTX
  end

  subgraph RUNTIME["RUNTIME — per student"]
    direction TB
    IN[/"Intake form<br/>parent + student"/]
    G0{{"gate: intake"}}
    S1(["1 · Profile<br/>describes the kid"])
    G1{{"gate: profile"}}
    S2(["2 · Projected Profile<br/>best-case anchor"])
    S3["3 · Match &amp; Rank<br/>modules.match_rank"]
    G3{{"gate: retrieval"}}
    S4(["4 · Gap Analyst<br/>diagnoses"])
    G4{{"gate: gap"}}
    S5(["5 · Strategy<br/>decides the moves"])
    G5{{"gate: strategy"}}
    S6(["6 · Two Paths<br/>target / stretch fork"])
    G6{{"gate: two_paths"}}
    S7(["7a · Plan Goals<br/>schedules"])
    G7{{"gate: plan"}}
    S8(["7b · Recommendations<br/>fan-out, one call per task"])
    RES(["live research<br/>verified web lookup"])
    S9["7c · Constraint Guardrail<br/>modules.constraint_guardrail"]
    G8{{"gate: recs"}}
    S10["7d · Tiering<br/>modules.tiering"]
    S11(["8 · Writer<br/>composes the plan"])
    G9{{"gate: draft"}}
    S12(["9 · Critic<br/>tone / honesty / plain English"])
    RENDER["render.py"]
    PDF[("Strategic Plan PDF")]
    TRAIL["quality trail<br/>gates.summarise()"]
    HUMAN["Human review<br/>no PDF"]

    IN --> G0 --> S1 --> G1 --> S2 --> S3 --> G3 --> S4 --> G4 --> S5 --> G5 --> S6 --> G6 --> S7 --> G7 --> S8
    S8 -->|"catalog empty for this task"| RES
    RES --> S9
    S8 --> S9 --> G8 --> S10 --> S11 --> G9 --> S12 --> RENDER --> PDF

    G1 -.->|"retry once, failure as feedback"| S1
    G4 -.->|"retry once"| S4
    G5 -.->|"retry once"| S5
    G6 -.->|"retry once"| S6
    G7 -.->|"retry once"| S7
    G9 -.->|"rewrite"| S11
    S12 -.->|"findings"| S11

    G0 -.->|"ESCALATE"| HUMAN
    G3 -.->|"ESCALATE: no admits / mock fallback"| HUMAN
    G8 -.->|"ESCALATE: nothing verifiable"| HUMAN
    G3 -.->|"DEGRADE: marked, run continues"| TRAIL
    TRAIL --> PDF
  end

  APPROWS -->|"admit cards for the intended colleges"| S3
  CTX -->|"circuits + findings"| S4
  CTX -->|"what moved the needle"| S5
  CTX -->|"published rates"| S6
  CTX -->|"catalog + circuits"| S8
  CTX -->|"published rates + evidence"| S11
```

---

## The boundary the shape enforces

**Profile describes → Gap diagnoses → Strategy decides → Two Paths forks →
Plan schedules → Recommendations sources → Writer writes → Critic checks.**

No step does the job of the step before it. A profile that diagnoses, or a
writer that decides, is a bug — not a style problem. `gate_profile` fails a
profile containing numbers for exactly this reason.

## Steps

| # | Step | Kind | Reads | Gate |
|---|---|---|---|---|
| 1 | Profile | agent (top) | intake | `gate_profile` — retry |
| 2 | Projected Profile | agent (mid) | profile | — |
| 3 | Match & Rank | module | 30,414 application rows | `gate_retrieval` — escalate / degrade |
| 4 | Gap Analyst | agent (top) | profile, cards, tally, circuits + findings | `gate_gap` — retry |
| 5 | Strategy | agent (top) | gap map, profile, findings | `gate_strategy` — retry |
| 6 | Two Paths | agent (top) | selected moves, admit pattern, published rates | `gate_two_paths` — retry |
| 7a | Plan Goals | agent (mid) | selected moves, profile, grade | `gate_plan` — retry |
| 7b | Recommendations | agent (mid), fan-out per task | catalog, circuits, constraints | — |
| 7c | Constraint Guardrail | module | recommendations, constraints | `gate_recs` — escalate |
| 7d | Tiering | module | intended colleges, seed | — |
| 8 | Writer | agent (mid) | the whole plan, published rates, evidence | `gate_draft` |
| 9 | Critic | agent (top) | draft | — |
| — | Comparisons | agent (top) | profile, cards | supplement, run separately |

## Gate verdicts

A gate does not ask "is this good?" It asks **"is this good enough for the next
step to mean anything?"** Four verdicts:

- **PASS** — continue.
- **DEGRADE** — continue, but mark the run. A degraded run is always visible in
  the output; it never passes silently.
- **RETRY** — re-run the step once, handing it the failure as feedback.
- **ESCALATE** — stop. No PDF. A human decides. Used only where continuing would
  produce something a family might act on and be harmed by.

`gate_retrieval` is the one that matters most. Empty or fabricated retrieval
makes every downstream step fiction *and looks completely normal in the PDF* —
which is exactly how it caught `match_rank` returning 0 cards from a 30,414-row
table on its first live run.

## Two rules the drawing encodes

**Numbers belong to modules.** Counts, bands, tiers and rates are computed by
deterministic code and handed to agents. An agent that states a number it was
not handed is a bug, not a phrasing issue.

**The corpus and the rate table answer different questions.** The corpus answers
*"what does an admit to this school look like?"* The published rate table
answers *"how selective is this school?"* The corpus never produces an admit
rate — it is self-selected, and 32.6% of posts omit rejections.

---

Source: [`orchestration.mmd`](orchestration.mmd) · Rendered image for slides:
[`orchestration.png`](orchestration.png) · Standalone page:
[`orchestration_page.html`](orchestration_page.html) · Rules and their history:
[`ENGINE_FEEDBACK_LOG.md`](../ENGINE_FEEDBACK_LOG.md) · Gate detail:
[`evals/GATES.md`](../evals/GATES.md)
