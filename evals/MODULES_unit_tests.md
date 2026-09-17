# Modules — Unit Tests, Not Rubrics (v1)

*Why some steps get no rubric. Written to discuss and refine.*

**The rule we set early and should keep:** grade **agents** with rubrics, test **modules** with
unit tests. A rubric judges reasoning that could reasonably go several ways. A module either
computes the right answer or it doesn't — and a rubric there would be a slower, vaguer test.

## What is a module (no rubric — write tests)
- **Match & Rank** (step 3) — retrieval and tally over the corpus
- **cohort_rates / admit_pattern** — application-level maths
- **published_admit_rate / selectivity_band** — table lookup and banding
- **constraint_guardrail** — budget, radius, hard-no enforcement
- **tiering** — attaching published rates to the school list
- **context packs** — assembling each step's evidence

## The tests that matter most
1. **The explode is lossless** — application rows = sum of the four outcome list lengths, after
   dedupe. Regression guard for the student-level → application-level transform.
2. **A duplicate (student, college) row cannot inflate n.** Verified: it doesn't.
3. **Suppression fires below the threshold** — a school with 1 decision returns no rate.
4. **Admits-only vs admits+denies never cross** — credential frequencies use admits only; rates
   use both. A test that asserts each function's input pool.
5. **The guardrail blocks what it should and nothing else** — it once blocked every
   recommendation because "in-person" was read as out-of-area.
6. **Alias resolution** — "UCLA", "UC Berkeley", "San José State" all resolve to canonical names.
7. **No rate without a class year** — the table cannot contain a rate missing its year.
8. **Context packs are non-empty** — `for_recs` must never hand the agent an empty catalog
   silently. That exact bug shipped `[CATALOG]` placeholders to a real plan for weeks.

## Where a module failure shows up
Module bugs surface as *agent* failures, which is what makes them expensive to find: an empty
catalog looks like a lazy recommendation agent; a bad tally looks like a hallucinating Gap
Analyst. **When an agent scores low, check its inputs before rewriting its prompt.** That is
what the BAD_INPUT fix lever is for.
