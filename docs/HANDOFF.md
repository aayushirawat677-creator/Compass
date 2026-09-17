# Handoff — what to do first

*For the engineer picking this up. Ordered by value, not by effort.*

---

## Day one: prove it actually works

Everything so far has run in **mock mode**, which returns canned fixtures and never calls a model.
So the prompts are written, wired and **entirely unmeasured**. Nothing else on this list matters
until that changes.

```bash
export LLM_MODE=real ANTHROPIC_API_KEY=...
python run.py --intake data/neerav_intake.json --out out/neerav.pdf --dump-state
python evals/grade_agents.py out/neerav.state.json
python evals/grade.py        out/neerav.plan.json
```

You need `data/acceptance_rejected_college_data_verified.csv` in place first
(`DATA_REQUIREMENTS.md`), or the retrieval gate will correctly block the run.

**Expect it to be worse than it looks.** A hand-written plan for the same student scores 79% on
`grade.py`, but that plan was written by a human, not produced by the engine. The first real run
is the first honest measurement. Read the quality trail and the per-agent Fitness grades before
changing anything.

---

## Then, in order

**1. Refresh `compass/mockdata.py`.** The fixtures predate several schema additions, so mock runs
fail gates that the prompts would pass. Once you have a good real run, use its `--dump-state`
output as the new fixtures. This makes mock mode a genuine regression test instead of a
misleading one.

**2. Wire the graders into the run.** `grade.py` and `grade_agents.py` are manual today. Run them
after each plan and persist the Fitness grades. Without this, "are the prompts still working?" is
answered by someone reading a PDF.

**3. Give escalations somewhere to go.** When a gate escalates, the run stops and produces no PDF
— correct behaviour, but silent. Unattended operation needs a queue, an email, a Slack message.
Anything that reaches a human.

**4. Grow the catalog.** `data/catalog.csv` has five verified rows covering one metro area.
Everything else escalates to live research, which works but costs a call and re-verifies the same
programs for every family. Catalog coverage is the main lever on both cost and quality.

**5. Build the seeded-defect test set.** The Critic's rubric cannot be scored without it: take a
known-good plan, inject one defect at a time (a pejorative word, a fabricated rate, a founder
credential, an itinerary on a card), and record what it catches and what it wrongly flags. See
`evals/R8_critic_rubric.md`.

---

## Two decisions that need a product owner, not an engineer

**The band grid.** Under published rates a school's band is fixed — Harvard is 3.59% whether or
not the student improves. So Target and Stretch currently show identical bands, and the "moves up
a band" arrows in the original design can't mean what they appear to. Either show fixed
selectivity plus a *fit* indicator that changes between paths, or redefine a band as fit.
Unresolved. `evals/R5_twopaths_rubric.md` has both options.

**"First-gen".** The findings report cites a 1.5× first-gen effect but never says whether that
means first-generation *college* or first-generation *immigrant*. The guard is deliberately
conservative (never applies the hook to a student with college-graduate parents) until someone
checks the source data.

---

## How to change behaviour safely

Almost every rule in `prompts.py` carries a `[#n]` tag pointing into `ENGINE_FEEDBACK_LOG.md`,
where the finding that produced it is written up — usually with the exact sentence that shipped
before the rule existed.

**Read the log entry before deleting a line.** Most of what looks like over-specification is there
because the engine did the opposite once, in front of a real family's plan. Examples: the profile
telling a family which activities to drop; a card crediting the student with founding a nonprofit,
directly against the strategy; percentages beside university names that nobody computed.

If a rule applies to more than one agent, it belongs in a **contract** (`EVIDENCE`, `TONE`,
`PROSE`, `PLANNING`, `CARD_GRAMMAR`), not copied into each prompt. Edit the contract.

---

## The one-line architecture

`R1 describes → Gap diagnoses → R4 decides → R5 forks → R6 schedules → R7 sources → R9 writes → R8 checks.`

Every rubric has a "What it is NOT graded on" section naming which step owns each excluded
question. If two rubrics both claim a question, there is an ownership bug in the pipeline — and
that section is where you find out.
