# Intake form → engine fields

The form asks more than the engine reads. This maps the questions that matter to
the fields the pipeline uses, so a new intake record can be built without guessing.
Source: `Peggy/Intake/intake_answers-export-*.csv` (semicolon-delimited; one row per
answer, keyed by `question_id`).

## The ones that decide whether a run can happen

| Q | Question | Engine field | Why it matters |
|---|---|---|---|
| **Q8** | *Has [child] mentioned any schools they like — even casually?* | `parent_answers.schools_child_mentioned` → `profile.intended.colleges` | **The run stops at step 3 without it.** Retrieval searches the corpus by college; with no college there is nothing to retrieve, and `gate_retrieval` escalates. Real answers in the export look like "NYU, Stanford, Berkeley, Chicago" or "no" — casual is fine, a list of five from a family still exploring is normal. |
| Q1 | *When you think about college for [child], where's your head at?* | `parent_answers.college_ambition` → `profile.intended.school_preference_verbatim` | The ambition **band** — most selective / strong and well-known / right fit over prestige. It says how high, not where. Never treat it as a school list. |
| Q45 | *Any alumni connections or professional networks tied to specific colleges?* | `parent_answers.alumni_connections` → `profile.tailwinds` | A hook, and never a target. A mother's Columbia degree is a fact about her. R1 inferring targets from this is the exact failure `gate_intake` and rule #37 exist to prevent. |
| Q6 | *Has [child] mentioned any career interests?* | `parent_answers.intended_direction` | Feeds the major track used to filter the corpus. |
| Q15 | *How important is financial aid?* | `parent_answers.constraints.financial_aid` | A hard constraint on every recommendation. |

## Still unmapped, and worth mapping

| Q | Question | Why |
|---|---|---|
| Q4 | What matters most to you in a college? | Would let the college list be filtered on fit, not just selectivity. |
| Q43 | How aligned are you and [child] on the college topic? | Tone. A family that "hasn't talked much about it" needs a different opening than one that talks about it "maybe too much". |
| VS1 | Forget specific schools — what does it look like when things go really well? | The parent's own words for success. The best raw material the final note has, and it is currently thrown away. |
| Q7 | How much does [child] understand about admissions? | How much the document has to explain. |

## Rules that hold whatever the record looks like

- **A school named by a parent about themselves is never a target.** Q45 is tailwinds; Q8 is targets.
- **A band is not a list.** Q1 answers the "how high" question, not the "where".
- **Empty is a legitimate answer** — and it stops the run on purpose. The fix is asking the parent, not inventing a list.
