# `comparisons` — R10 Profile Comparisons (prompt spec)

**Component:** R10 · Profile Comparisons supplement
**Phase:** runs separately from the ten-step chain; a two-page companion document
**Model tier:** Mid. Presentation of retrieved rows, not contested judgment.
**Rubric:** `evals/Comparisons_rubric.md`

---

## Why it exists

The plan **cannot honestly state this student's odds.** The corpus is self-selected — its
accept share for a typical six-school list runs **3.7× to 7.7× above the published rate**,
because people post to a results forum when the news is good — and a published admit rate is
a property of the school, not of a child. [#88]

So this supplement answers the calibration question a different way: **show real applicants
with real outcomes at the schools on the child's list**, and let the parent see for
themselves what each level of credentials actually bought. No inference, no forecast, just
what happened to other people.

---

## What it does / does not do

**Does:** present real, retrieved applicant profiles with outcomes that already happened, at
schools on this family's list.

**Does not:**
- **Blend with the Outcome Cards.** Those are about THIS student, projected. These are about
  OTHER students, resolved. Never let a comparison card read as a prediction.
- **Imply a rate.** A set of examples is not a base rate, and the reader must not be able to
  count them and come away with one.
- **Surface anything identifying.** The corpus carries `author`, `reddit_post_link` and
  `post_body`. **None of the three may appear in a generated document**, in any form,
  including paraphrase close enough to search for.

---

## Card colouring

Coloured by **which bands the applicant's strongest admit falls into**, never by the
school's absolute prestige:

```
GOLD    dream admit   admitted to a school in this student's Far Reach band
PURPLE  reach admit   admitted in the Reach band, rejected from Far Reach
```

---

## Gates

`gate_retrieval` — nothing usable retrieved is a stop, not a degrade. A comparison
supplement built on too few rows invites exactly the base-rate inference it exists to avoid.
