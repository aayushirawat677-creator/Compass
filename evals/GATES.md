# Runtime Acceptance Gates — stopping bad output before it propagates

*Rubrics grade a run after it finishes. Gates run during it. Different jobs.*

---

## The problem they solve

Without gates, one bad step quietly poisons everything after it — and the failure surfaces at
the very end, in the PDF, **looking like a writing problem**. A profile with no constraints does
not merely score badly; it makes every recommendation downstream unbounded. Retrieval that
returns nothing does not weaken the gap map; it makes the gap map fiction. The plan still comes
out looking complete, which is what makes it dangerous.

**The question a gate asks is not "is this good?" but "is this good enough for the NEXT step to
be meaningful?"** Fitness for purpose, checked at every boundary.

Gates are **deterministic and cheap**, so they run on every step of every run for free.

## The four verdicts

| verdict | what happens | when |
|---|---|---|
| **PASS** | continue | output is usable |
| **DEGRADE** | continue, but mark the state so downstream and the output know what is thin | usable but weaker than we'd like — **never silent** |
| **RETRY** | re-run the step once, handing it the failure as feedback | a fixable, self-contained miss |
| **ESCALATE** | **stop. No PDF.** A human decides | continuing would produce something a family might act on and be harmed by |

---

## The gates

| # | Gate | Fails when | Verdict |
|---|---|---|---|
| 0 | **intake** | no constraints (every rec would be unbounded) · no intended direction (retrieval has no target) | ESCALATE |
| 1 | **profile** | no spine and no honest "no clear spine" flag · constraints not carried · **any number in the object** | RETRY |
| 2 | **retrieval** | **no admits · fell back to MOCK cards** · fewer than the minimum | ESCALATE / DEGRADE |
| 3 | **gap** | no gaps · invalid categories · gaps citing no tally frequency (invented counts) · prescriptive language | RETRY |
| 4 | **strategy** | nothing selected · selected nearly every gap (a pass-through, not a choice) · >6 moves (no spike) · moves dropped with no tensions recorded | RETRY |
| 5 | **plan** | no current-year plan (parent has nothing to act on) · no task carries a date | RETRY |
| 6 | **recommendations** | placeholder shipped · anything neither verified nor escalated | **ESCALATE — no retry** |
| 7 | **writer** | required sections missing · a percentage never handed to the writer · personal-odds phrasing | RETRY |

**Why recommendations never retries:** a fabricated program is the one defect a family acts on —
they phone the number. That goes straight to a human, not back to the model.

**Why retrieval is the most important gate:** it is the only failure that makes *everything*
downstream fiction while looking completely normal in the output.

---

## It caught a real bug the first time it ran

Wiring the gates in blocked the very first run: **`retrieval returned NO admits`**.

The cause was real. `match_rank` had been written against the corpus schema we *assumed*
(`student_id`, a `result` containing "accept"). After the corpus was rewritten to explode into
application rows (#23), those columns no longer existed — so it returned **zero cards from a
30,414-row corpus** and the pipeline carried on with mock cards. Every gap, every strategy call
and both cards would have been computed against fictional students, and the PDF would have looked
entirely normal.

That bug had been live and invisible. The gate found it in one run.

After the fix: **334 cards · 38 real admitted students · modal GPA band 3.8+ (89%) · modal test
band 1500+/34+ (79%)**, plus peer colleges discovered from the admits themselves.

---

## The quality trail

Every run records what each gate said. `state["quality"]` carries `overall`, the per-step
`trail`, and `blocked`. A run that degraded is visible as a degraded run — it never passes
silently, and the trail says exactly where it weakened.

```
python run.py --intake <intake.json> --out out/plan.pdf --dump-state
```

A blocked run produces **no PDF, by design**, and says which step stopped it and why.
**A blocked run is a success of the system, not a failure of it.**

---

## Where gates end and rubrics begin

- **Gates** are deterministic, run every time, and answer *can the next step proceed?*
- **Rubrics** need judgment, run on a sample, and answer *how well did this step do its job?*

A gate can only catch what is mechanically checkable — an empty field, an invalid category, a
number nobody handed over. It cannot tell you the strategy picked the wrong spike, or that the
profile subtly misread the child. That is what the nine rubrics are for, and why both exist.
