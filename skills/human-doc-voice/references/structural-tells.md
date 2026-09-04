---
created: 2026-09-04
updated: 2026-09-04
intent: structural AI tells for detect-only scan
keywords: stop-slop, structures, rule-of-three, antithesis, rhythm
type: spec
---

# Structural tells – detect-only

Condensed from [hardikpandya/stop-slop `references/structures.md`](https://github.com/hardikpandya/stop-slop/blob/main/references/structures.md). Flags only; edits after «ok» (SKILL.md §Detect-only).

Frequency thresholds for antithesis and linkers – SKILL §5 + `scripts/tics.py`. This file covers **structure and rhythm**, not lexicon.

## Excluded (not imported)

| Upstream rule | Why we skip it |
| --- | --- |
| Ban em dash; «no em dashes at all» | Formal reports may use en dash «–» (U+2013); em dash (U+2014) – no |
| Kill all adverbs (-ly, really, just…) | Too broad; cut only empty emphasis in slop context |
| Reader in the room / «you» / personality | Register is formal leadership report, not blog; SKILL §1 |
| Narrator-from-a-distance → «put reader in the seat» | Same – do not shift report into direct address |
| False agency → always «name the human» | Only when hidden owner/actor breaks the report; not as «you» style |

## Not X but Y (binary contrasts)

Flag when the contrast is **formulaic**, not informative:

| Pattern | Flag when |
| --- | --- |
| Not because X. Because Y. / not X, but Y | Telegraphic reversal with no new information |
| The answer isn't X. It's Y. | Predictable pivot |
| It's not this. It's that. / isn't X, it's Y | Mechanical contrast |
| not just X but also Y | Additive hedge |
| Negative listing: Not A… Not B… Z. | «Striptease» through negations |

**Fix (after «ok»):** state Y directly; keep antithesis only where contrast is the point (see `tics.py` threshold >3).

## Rule of three

| Pattern | Flag when |
| --- | --- |
| Three parallel nouns/verbs/adjectives | «innovation, inspiration, and insights» – two or one may suffice |
| Three list items with identical grammar | Template «completeness» |
| Three short fragments in a row | X. And Y. And Z. – staccato drama |

**Fix:** keep 1–2 strong elements; do not pad for rhythm.

## Metronomic sentence length

| Pattern | Flag when |
| --- | --- |
| All sentences ~same length (mid band) | No short and long mix – generator cadence |
| Every paragraph: fact → moral of same length | Same rhythm across sections (SKILL §5 tics) |
| Every list item ends with a punch | Performative punchline |
| Series of dramatic fragments | Then X arrived. No Y. No Z. – manufactured profundity |

**Fix:** merge or break rhythm where meaning is clear; do not add a «moral» to every section.

## Other structures (brief)

| Pattern | Flag |
| --- | --- |
| Rhetorical setup | What if…?, Here's what I mean:, Think about it: |
| Heading restated in line 1 | H2 + restate H2 |
| Wh- sentence openers as crutch | What makes this hard is… → lead with subject/fact |
| Paragraph starts with So | Filler opener |
| Lazy extremes | every, always, never without numeric support |

## Detect-only output format

Table: `location | tell-id | excerpt | suggested direction` – no file edits until «ok».
