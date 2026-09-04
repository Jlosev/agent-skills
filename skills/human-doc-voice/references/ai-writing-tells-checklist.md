---
created: 2026-09-04
updated: 2026-09-04
intent: detect-only scan checklist for outbound leadership reports
keywords: ai-writing, humanizer, wikipedia, detect-only
type: spec
---

# AI-writing tells – compact checklist

Detect-only reference. **Do not rewrite from this file** – flags only; edits after user «ok» (see SKILL.md §Detect-only).

**Source:** [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup); condensed from [blader/humanizer](https://github.com/blader/humanizer) (MIT). We do not copy the upstream skill wholesale.

**Not imported into human-doc-voice:** em-dash ban, «kill all adverbs», reader-in-the-room / you / personality – see `structural-tells.md` §Excluded.

## Content

| # | Look for | Example markers |
| --- | --- | --- |
| C1 | Inflated importance | pivotal, crucial, testament, underscores, broader movement, evolving landscape |
| C2 | Name-dropping without context | media list / follower count to prove importance |
| C3 | -ing as fake depth | highlighting, underscoring, symbolizing, fostering, showcasing |
| C4 | Sales tone | vibrant, nestled, breathtaking, must-visit, rich heritage |
| C5 | Vague sources | experts argue, industry reports, observers note – no named source |
| C6 | Stock challenges / outlook | Despite its… faces challenges… continues to thrive |

## Language and grammar

| # | Look for | Example markers |
| --- | --- | --- |
| L1 | Stock AI lexicon (in clusters) | additionally, delve, landscape (abstract), tapestry, pivotal, underscore (v.) |
| L2 | Avoiding is/are | serves as, boasts, features instead of plain «is / has» |
| L3 | Not X but Y | not only… but…, it's not X it's Y, clipped negation («…, no guessing») |
| L4 | Rule of three | three parallel items where one or two suffice |
| L5 | Synonym cycle / same openings | protagonist → main character → central figure; She… She… She… |
| L6 | False from X to Y | «from A to B» without a real range |
| L7 | Passive without subject | see SKILL §5 contract – separate from «reader in the room» |

## Style and chatbot artifacts

| # | Look for | Example markers |
| --- | --- | --- |
| S1 | Excess bold | **word:** on every list item |
| S2 | Title Case headings | Every Word Capitalized |
| S3 | Emoji in body | decorative rockets / checkmarks |
| S4 | Chatbot tail | I hope this helps, let me know, Would you like… |
| S5 | Knowledge-cutoff / guess-fill | as of my training, likely grew up, not publicly available → invention |
| S6 | Agreeable opener | Great question!, You're absolutely right! |
| S7 | Layered filler / hedging | in order to, due to the fact that, could potentially possibly |
| S8 | Generic positive ending | bright future, exciting times ahead instead of last fact |
| S9 | «Deeper truth» | at its core, the real question is, what really matters |
| S10 | Announcement | Let's dive in, Here's what you need to know |
| S11 | Heading = first sentence | H2 then one-line restate of H2 |
| S12 | Fake alternative | One might be tempted to… but… – option nobody considered |

## False positives (do not flag alone)

- one em/en dash, one *however*, one short emphasis sentence;
- academic diction without stock-word clusters;
- quotes, titles, UI strings, frontmatter, code;
- en dash «–» per project typography in formal reports – **not** an error.

**Strong signal:** several patterns from different groups in one paragraph or in close succession.
