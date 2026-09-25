# `two_paths` — R5 Two Paths (prompt spec)

**Component:** R5 · Two Paths
**Phase:** 7 — **after** the plan, not before it [#17]
**Model tier:** Top. It writes the Outcome Cards, the page a parent photographs.
**Rubric:** `evals/R5_twopaths_rubric.md`

---

## Why it runs after the plan

It used to run before, and produced cards describing a plan that did not yet exist —
promises with no work behind them. **The card is the OUTPUT of the plan, not an input to
it.** Moving it after R6 means every credential on it can be traced to a goal that was
actually scheduled, and `gate_card_plan` checks that in both directions: a credential with
no plan work is a promise the plan never keeps, and a headline goal with no credential
means the card under-sells the plan.

---

## What it does / does not do

**Does:** take the moves Strategy chose and produce two coherent versions of one plan —
TARGET and STRETCH — each ending in an Outcome Card.

**Does not:**
- **Re-open the strategy.** Which gaps matter is decided. It asks one question: *what does
  this student look like at the end on each path, and what does the harder path cost?*
- **State odds.** No probability for this child, ever. Percentages belong to schools. [#88]
- **Invent a higher band.** The corpus's top bands are open-ended — 3.8+ and 1500+/34+ have
  nothing recorded above them. The Stretch says where **inside** the top band to aim, and
  the sub-line says so. Aiming high inside a measurement is a plan; claiming a measurement
  above the data is a sales document. [#83]

---

## The card, as it now stands

Both cards share **one page** so their four academic figures can be compared rather than
remembered. [#81]

- **Exactly four stats:** GPA · entrance tests · rigour as the AP band · one course mark
  chosen for this student. Not six. `RIGOUR` and `ADVANCED COURSES` were the same fact
  twice; `WHAT HE CARRIES` and `TOP LEVEL REACHED` were the credential list in shorthand. [#78]
- **Four credentials, one thread each**, the activity named in the first few words. No
  programme or body named four years out. Nothing academic — that is the stat row. [#78][#63]
- **No courses on the card.** A course target is a decision the family makes at a desk; the
  card is a projection. Different kinds of statement. [#78]
- **Grades are numerals in the stat row** — "by grade 12", not "by twelfth". The row is
  scanned, not read. [#79]
- **Four tiers below both cards**, placed by each school's own published admit rate, with
  empty tiers left visibly empty. [#88]

## Gates

`gate_two_paths` · `gate_card_plan` · `gate_card_shape` · `gate_score_sanity` ·
`gate_no_personal_odds`
