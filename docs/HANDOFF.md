# Handoff — what to do first

*For whoever picks this up. Ordered by value, not by effort.*

---

## Day one: run the writer for real. Nothing else on this list matters yet.

**Every page of the current document was hand-built.** From v12 onward I edited
`out_writer.json` directly to show Aayushi the shape, and the prompt was updated to match
afterwards. The prompt now describes all of it and 26 gates enforce it — but **the writer
has never once been run against the new spec.** There is no API key in the dev container.

So the honest status is: the repo makes a claim about what it produces, and nobody has
tested the claim.

```bash
export LLM_MODE=real ANTHROPIC_API_KEY=...        # never paste a key into a chat
python run.py --intake data/neerav_intake.json --out out/neerav.pdf --dump-state
python evals/audit.py          # 64 structural checks
python evals/golden.py         # did the render change?
python evals/grade_agents.py out/neerav.state.json
python evals/grade.py        out/neerav.plan.json
```

**Expect the first run to be worse than the current PDF looks**, and read the quality trail
before changing anything. The gates will tell you exactly which shapes the writer missed —
that is what they are for. `audit_render_contract` (#89) already caught the four fields
that would have rendered blank; there may be more it cannot see.

---

## Then, in order

**1. Grade run11 against the nine rubrics.** Offered many times, never done. The audit
proves the machinery runs; it says nothing about whether the output is good. The last
graded run (Profile B, Gap C, Strategy B, Two Paths B, Plan Goals B, Recs C, Writer B)
predates the appraiser, the academics, the reordered card, the requirements source and
every rule from #76 on.

**2. Refresh `compass/mockdata.py`.** The fixtures predate a dozen schema additions, so
mock runs fail gates the prompts would pass. Use a good real run's `--dump-state` as the
new fixtures, and mock mode becomes a regression test instead of a misleading one.

**3. Replace Q8.** `data/neerav_intake.json` carries a note: the six colleges were
**supplied by the team, not by the parent**. That must be the parent's own answer before
any plan reaches a family. Everything downstream — the tiers, the requirements table, the
odds — is built on that list.

**4. Wire `debate_circuits`.** Flagged by three consecutive runs. The registry reports 132
Tabroom rows in coverage but the reference pack exposes no circuit list, so every debate
goal names a level and never a league.

**5. The other five CDS C7 schools.** Only Michigan is verified; Penn, Georgetown,
Berkeley, NYU and UCLA are `blocked` by hosting. Aayushi said leave it. Note that
`course_requirements.json` covers all six anyway, from plain HTML — the CDS is not the
only door.

---

## Things that will bite you

**A stale `.pyc` can serve code that is not on disk.** Python compares source mtime at
one-second granularity, so an edit saved inside the same second as the last import is
ignored. Cost a confusing debugging session. `golden.py` clears `__pycache__`; your own
scripts do not. [#91]

**Rendering must not mutate the draft.** `_safe()` used to shallow-copy and then write into
the nested card dicts, so a gate run after rendering saw different data than one run
before, and a correct document failed a correct gate on ordering alone. [#86]

**Every gate needs a negative control.** A test that feeds it the exact input it must
reject. Six gate bugs in one session were caught this way and none by reading.

**When a rule moves content, re-read every gate written under the old arrangement.** Five
gates so far have gone on demanding something a newer rule relocated.

---

## The standing constraints

* **Nothing system-internal in the PDF.** Our vocabulary (`reach`, `disposition`,
  `converts`), our uncertainty, our operator checklists. Said twice, violated twice more
  after that. [#75][#84]
* **No named programme, body or competition four years out** — not in the roadmap, not on
  the card, not in the flags box. [#62][#63]
* **No probability for a child.** Percentages attach to schools. [#88]
* **The corpus carries Reddit usernames, post links and full post bodies.** Keep the repo
  private, do not redistribute `data/`, never surface `author` or post text in a plan.
* **Never paste an API key into a chat.** The engine reads `ANTHROPIC_API_KEY` from the
  environment. `.env`, `*.key` and `**/secrets*` are gitignored.
