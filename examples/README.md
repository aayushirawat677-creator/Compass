# `examples/` — the target output

## `neerav_plan_reference.pdf`

What a finished Strategic Plan looks like: a real intake (Neerav, grade 8),
worked all the way through to the designed multi-page PDF. This is the bar the
engine is aiming at — profile page, gap analysis, Outcome Cards, two paths,
goals and recommendations.

Open this before reading any code. It is much faster than inferring the product
from the pipeline.

## `neerav_render.py`

The script that produces it. **Important: this does not call the pipeline.** It
imports `compass.render` and passes a hand-authored plan dict — the content was
written and revised by hand over many rounds, not generated.

That makes it two useful things and one dangerous one:

- **A rendering reference** — the exact structure `render.py` expects.
- **A quality target** — the content in it is the output that survived the
  review rounds recorded in `ENGINE_FEEDBACK_LOG.md`. Most of the 31 rules in
  that log came from editing this document.
- **Not evidence the engine works.** Nothing here was produced by a model. A
  generated plan of this quality has not been demonstrated yet — the first real
  run is still the day-one task in `docs/HANDOFF.md`.

Keep that distinction sharp when comparing a generated plan against this file:
the comparison is useful, but this is a hand-made benchmark, not a baseline run.
