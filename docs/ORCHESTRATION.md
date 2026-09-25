# How Compass runs

*Current as of rule #92. The log (`ENGINE_FEEDBACK_LOG.md`) is the reasoning; this is the map.*

---

## The pipeline

Ten steps. Each one is a separate agent call with its own prompt, its own gates, and a
verdict that can send it back.

```
1  profile      describes the child, from the intake and nothing else
2  projected     backend match key — never rendered
3  match & rank  pulls similar admitted profiles           [deterministic]
4  gap           diagnoses what is missing
4b appraiser     judges what each activity can become      [#59]
5  strategy      decides what the plan will do
6  plan_goals    schedules it, semester by semester        [#57]
7  two_paths     summarises it as Target and Stretch
8  writer        turns all of it into the document
9  critic        reads the result as a stranger would
```

**The boundary is the point.** R1 describes, gap diagnoses, the appraiser judges ceilings,
R4 decides, R6 schedules, R7 summarises, R9 writes, R8 checks. A step that reaches across
that line produces the failure modes the log is mostly about: a writer that invents, a
planner that appraises, a profile that asks questions it should have answered.

`comparisons` runs separately and is not part of the chain.

---

## The five evidence sources, and what each can answer

They are kept apart on purpose. Collapsing them is how a plan starts asserting things.

| source | answers | file |
|---|---|---|
| **corpus** | what an admit *looked like* | `acceptance_rejected_college_data_verified.csv` |
| **admit_rates** | how selective a school *is* | `admit_rates.json` |
| **college_weights** | what a school says it *weighs* (CDS C7) | `college_weights.json` |
| **course_requirements** | what a school says to *take* | `course_requirements.json` |
| **expert_corpus** | what practitioners *advise* — **advisory only** | `expert_corpus.md` |

**None of them gives a student's odds, and none may be used to imply one.** [#88]
The corpus is the trap: its accept share for this family's six schools runs **3.7× to 7.7×
above the published rate**, because people post to a results forum when the news is good.

The expert corpus is the only source that is asserted rather than measured. It never
overrides a measurement, it is tier-gated to the student's real list (§0.4), and its
vendor statistics never reach a family as fact. [#73]

---

## The gates

**26 of them**, four verdicts: `PASS` / `DEGRADE` / `RETRY` / `ESCALATE`.

```
intake       profile      retrieval    gap          strategy      plan
recs         draft        two_paths    document     budget        appraisal
honours_appraisal         open_questions            horizon       academics
card_plan    parent_voice category_sweep            expert_use
card_shape   course_page  requirements profile_grounding
score_sanity no_personal_odds
```

Every gate has a **negative control** — a test feeding it the exact input it must reject.
That rule paid for itself repeatedly: six gate bugs in one session were caught by controls,
not by reading.

### The two things gates keep teaching us

**A rule is a suggestion until something rejects the output that breaks it.** [#78]
The writer spec said "exactly 4 stats" while six rendered, "credentials 4–6" while seven
did, "never repeat the stat row in a credential" while one carried the GPA band. Four
written rules, none enforced, all four broken. The prompt is where a rule is *expressed*;
a gate is where it is *in force*.

**When a rule moves content, re-read every gate written under the old arrangement.** Five
times now a newer rule has invalidated an older gate's assumption and failed correct work
(#7, #8, #11, #16, #80→`gate_course_page`). A gate that rejects correct output is worse
than no gate: the fix a writer reaches for is to pad.

---

## The document

Twelve pages.

```
     cover
01   Profile                only what the family told us              [#84]
02   The Two Plans          both cards side by side + four tiers      [#81][#88]
03   Courses and Grades     what the schools ask for                  [#82][#87]
04   The Roadmap            five grades, semester by semester         [#57]
05   This Year, Specifically
06   Parent Actions
```

**Page 02 is one page on purpose.** The most important fact about the two plans is that
their academic figures are nearly identical, and that cannot be seen across a page turn.
The four tiers at its foot are placed by each school's **own published admit rate** —
never a probability for this child — and two of the four being empty is the finding.

---

## Reproducibility

Three different questions. [#92]

| question | answer |
|---|---|
| same draft → same document? | **Yes**, proven by `evals/golden.py`. HTML is byte-identical; the PDF is not, because WeasyPrint stamps a creation time, so the golden is the HTML. |
| same intake → same shape? | **Yes**, by the gate set. A run missing the stat row, the tiers or the citations is rejected. |
| same intake → same words? | **No**, and not a goal. Temperature is pinned to 0 at every call site (#90), which removes the variance that is ours; batching still varies. |

Watch out for stale bytecode: Python compares source mtime at **one-second granularity**,
so an edit saved inside the same second as the last import may not be the code that runs.
`golden.py` clears `__pycache__` first. [#91]

---

## Running it

```bash
python evals/audit.py      # 64 structural checks: is any of this actually wired?
python evals/golden.py     # did the render change?
python run.py --intake data/neerav_intake.json --out out/plan.pdf --dump-state
```
