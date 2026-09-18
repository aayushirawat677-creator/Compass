# Compass Engine

Turns one college-planning intake form into a designed, multi-page **Strategic Plan PDF** for a
family — via nine agent/module steps, with runtime gates that stop bad output propagating and a
rubric suite for grading each step.

```
intake.json  ──▶  9 numbered steps · 10 agent calls + 4 modules · 9 gates  ──▶  Strategic_Plan.pdf
```

---

## Start here — in this order

1. **`examples/neerav_plan_reference.pdf`** — what the product is. Two minutes, and it makes
   everything below make sense. (Hand-authored, not a pipeline run — see `examples/README.md`.)
2. **`docs/ORCHESTRATION.md`** — how it runs, as one diagram: agents, modules, gates, data plane.
3. **Quick start below** — clone, install, `python run.py`. Mock mode produces a PDF in about a
   minute with no API key.
4. **`docs/HANDOFF.md`** — what to do first, ordered by value. The first real run is task one.
5. **`ENGINE_FEEDBACK_LOG.md`** — why the rules are the way they are. Read the relevant entry
   before deleting anything that looks redundant; most of it is there because the engine shipped
   the opposite once.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# weasyprint needs native libs. macOS: brew install pango libffi
# Debian/Ubuntu: apt install libpango-1.0-0 libpangoft2-1.0-0 libffi-dev

# 1) Mock mode — no API key, no cost. Verifies the plumbing end to end.
python run.py --intake data/neerav_intake.json --out out/plan.pdf --dump-state

# 2) Real mode — the prompts actually run.
export LLM_MODE=real
export ANTHROPIC_API_KEY=...        # never commit this
python run.py --intake data/neerav_intake.json --out out/plan.pdf --dump-state

# 3) Grade the run
python evals/grade_agents.py out/plan.state.json   # per-agent, against each rubric
python evals/grade.py        out/plan.plan.json    # the rendered document
```

> **Mock vs real matters more than it looks.** In mock mode `llm.ask_json()` returns a canned
> fixture from `compass/mockdata.py` and **never calls a model** — every run produces the same
> output whatever intake you give it. Mock mode tests the plumbing; only real mode tests the
> prompts.

---

## The pipeline

| # | Step | Kind | What it does |
|---|---|---|---|
| 1 | **Profile** (R1) | agent | Reads the intake → a structured picture of the student. Describes; never judges. |
| 2 | **Match Key** | agent | A projection used *only* to retrieve similar admitted students. Never rendered. |
| 3 | **Match & Rank** | module | Retrieval + tally over the corpus. |
| 4 | **Gap Analyst** | agent | Student vs. similar admits → a complete, unranked gap map. Diagnoses; never prescribes. |
| 5 | **Strategy** (R4) | agent | Decides which gaps matter → prioritised moves. **All judgment lives here.** |
| 6 | **Two Paths** (R5) | agent | Forks into Target and Stretch variants. Stretch = intensify + add on. |
| 7 | **Plan** (R6) + **Recommendations** (R7) | agent | Goals/tasks by term; real bookable options. |
| 8 | **Writer** (R9) | agent | The document a parent reads. |
| 9 | **Critic** (R8) | agent | Last check on how it is written. Flags; never rewrites. |

Plus a **Profile Comparisons** supplement (`COMPARISONS`) — a two-page pack of real applicant
outcomes, run separately.

**The boundary that holds the design together:**
`R1 describes → Gap diagnoses → R4 decides → R5 forks → R6 schedules → R7 sources → R9 writes → R8 checks.`
Numbers belong to modules at every step. An agent stating a number it wasn't handed is a bug.

---

## Repo layout

```
compass/
  prompts.py        all agent prompts + 5 shared contracts (see below)
  pipeline.py       the orchestrator; wires steps and gates
  gates.py          runtime acceptance gates (PASS / DEGRADE / RETRY / ESCALATE)
  modules.py        deterministic maths: retrieval, tally, rates, guardrail
  data_access.py    corpus, circuits, findings, catalog, published rates
  context.py        per-step "context packs" — the retrieval layer
  llm.py            model client; mock + real; verified web research
  refresh_rates.py  self-extending published admit-rate table
  render.py         plan JSON → HTML → PDF
  programs.py       program / competition registry + the six-rung ladder
  mockdata.py       fixtures for mock mode (STALE — see Known gaps)

evals/              10 rubrics, 3 graders, the rubric standard, gate docs
data/               the corpus, published rates, findings, and the program
                    registry (sources.json + programs.csv) — see data/README.md
docs/               ORCHESTRATION.md (the diagram), HANDOFF.md (what to do first)
design/             how it was designed; its README says which parts are current
examples/           the reference plan PDF and the script that renders it
ENGINE_FEEDBACK_LOG.md   31 numbered rules, each traced to a real review finding
```

### The shared contracts
`prompts.py` defines five contracts injected into the prompts that need them, so a rule lives in
exactly one place and cannot drift between agents:

- **EVIDENCE** — grounding, no overclaiming, no chained inference, and the numbers/odds rules
- **TONE** — a parent is reading this about their own child
- **PROSE** — every sentence earns its place
- **PLANNING** — horizon rule, explore-then-commit, join-don't-found, activity cap
- **CARD_GRAMMAR** — shared by the Outcome Cards and the Comparison cards

**Edit the contracts, not the copies.** Every rule carries a `[#n]` tag back to
`ENGINE_FEEDBACK_LOG.md`, where the finding that produced it is written up. If a line looks
verbose, read its log entry before deleting it — most of them are there because the engine
shipped the opposite once.

---

## Two things that are easy to get wrong

**1. The corpus is application-level, not student-level.**
`acceptance_rejected_college_data_verified.csv` has **one row per student** with outcomes stored as
`"; "`-separated lists (`accepted_colleges`, `rejected_colleges`, …). `data_access.load_corpus()`
explodes it into one row per *(student, college, result)* — 30,414 application rows from 2,613
students. A student is legitimately an admit at some schools and a deny at others; that pairing is
what supplies a denominator. GPA and test are **bands** ("3.8+"), not numbers.

**2. Admit rates come from the web, never from the corpus.**
- **Corpus** answers *"what does an admit look like"* — patterns, credential frequencies. Never a rate.
- **`data/admit_rates.json`** answers *"how selective is the school"* — official published rates
  with class year and source.

The corpus is self-selected **and** a third of its posts omit rejections entirely (measured: that
inflates top-school rates by 6–7 points). A school's published rate is the school's, not the
student's — so bands describe the school, and nothing in the output may be worded as the
student's personal odds.

---

## Runtime gates

Eight deterministic gates run inside the pipeline, one per boundary. They ask *"is this good enough
for the NEXT step to be meaningful?"* — not *"is this good?"*

| verdict | effect |
|---|---|
| PASS | continue |
| DEGRADE | continue, but mark the state — never silently |
| RETRY | re-run the step once with the failure as feedback |
| ESCALATE | **stop. No PDF.** A human decides. |

Every run records a **quality trail** in `state["quality"]`. A blocked run producing no PDF is a
success of the system, not a failure of it. See `evals/GATES.md`.

> The retrieval gate caught a live bug on its first run: `match_rank` was querying columns that no
> longer existed, returning **zero cards from a 30,414-row corpus** while the pipeline carried on
> with mock cards. Every downstream judgment was being made against fictional students, and the
> PDF looked entirely normal.

---

## Evals

**Ten rubrics**, one per agent, in `evals/`. Each: 4–5 checks scored 0–3, rolling to one
**Fitness grade (A–F)**, with a **gate** where failure makes downstream meaningless and a **fix
lever** on every sub-3 check (`FIX_PROMPT` / `ASK_PARENT` / `CHANGE_INTAKE` / `CHANGE_SCHEMA` /
`BAD_INPUT`). `evals/RUBRIC_INDEX.md` maps them; `evals/RUBRIC_STANDARD.md` is the meta-rubric
they are themselves held to, with `audit_rubrics.py` checking it mechanically.

**Modules get unit tests, not rubrics** — see `evals/MODULES_unit_tests.md`. A rubric judges
reasoning that could reasonably go several ways; a module either computes the right answer or it
doesn't.

**When an agent scores low, check its inputs before rewriting its prompt.** Module bugs surface as
agent failures — an empty catalog reads as a lazy recommendation agent. That is what `BAD_INPUT`
is for.

---

## Known gaps — read before starting

1. **No real run has ever happened.** Everything to date ran in mock mode. The prompts are
   written and wired but **unmeasured**. First real run is the highest-value next step.
2. **`mockdata.py` fixtures are stale.** They predate several schema additions, so mock runs fail
   some gates (`plan_goals` currently RETRYs) and score badly on the per-agent rubrics. That is
   the fixtures, not the prompts.
3. **The corpus is committed; IPEDS is not.** The corpus lives at
   `data/acceptance_rejected_college_data_verified.csv` — keep this repo private, and read
   `data/README.md` before using it. IPEDS is still gitignored; see `DATA_REQUIREMENTS.md`.
4. **The program registry is thin.** 135 rows, and only debate has real depth. Robotics, math,
   science research, CS, Model UN, writing, arts, music, athletics and leadership have no rows
   yet — `programs.coverage()` lists them. Anything uncovered escalates to live research, which
   works but costs a call per recommendation.
5. **Escalations have nowhere to go.** A blocked run stops correctly but nothing notifies anyone.
   Needed before unattended operation.
6. **Graders are manual.** `grade.py` / `grade_agents.py` should run after each plan and store the
   Fitness grades.
7. **Open product question:** under published rates a school's band is fixed, so Target and Stretch
   show identical bands. Either show fixed selectivity + a changing *fit* indicator, or redefine a
   band as fit. Unresolved — see `evals/R5_twopaths_rubric.md`.
8. **Open data question:** does the findings report's "first-gen" mean first-gen *college* or
   first-gen *immigrant*? The guard is conservative until answered.

---

## Cost

Roughly 13 agent calls per plan, plus one per recommendation and any live research lookups —
call it 15–20 model calls. Measure it on the first real run rather than estimating.

---

## Credentials

Never commit a key. `ANTHROPIC_API_KEY` is read from the environment; `.gitignore` covers `.env`
and `*.key`.

The corpus **is** committed, because the Outcome Cards cannot be built without it. It carries
Reddit usernames, post links and full post bodies — public posts, but traceable to individuals.
Keep this repo private, don't redistribute the file, and never surface `author` or post text in a
generated plan. `data/README.md` has the handling rules.
