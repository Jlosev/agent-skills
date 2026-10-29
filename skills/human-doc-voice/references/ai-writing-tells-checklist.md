---
created: 2026-09-04
updated: 2026-10-29
intent: scan hints for any text a person will read
keywords: ai-writing, humanizer, wikipedia
type: spec
---

# AI-writing tells – compact checklist

Scan hints for the apply pass. Fix a hit in the same pass. Do not treat this file as an approval gate.

**Source:** [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (WikiProject AI Cleanup), checked 2026-10-29. Russian marker lines: [Википедия:Признаки сгенерированности текста](https://ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста). The Russian page lags. What counts as live follows the English page.

**As of 2026-10-29.** Live tells are the October 2026 block and the rows marked live. Delve, tapestry, knowledge cutoff, «in conclusion», em dash, and elegant variation are historical. Do not scan them.

**Not imported into human-doc-voice:** em-dash ban, en-dash ban, «kill all adverbs», reader-in-the-room / you / personality, curly-quote conversion, a length quota, translating a domain term, stripping modality («может», «возможно»). See `structural-tells.md` §Excluded.

## Content

| # | Look for | Example markers |
| --- | --- | --- |
| C1 | Inflated importance | pivotal, crucial, testament, underscores, broader movement, evolving landscape |
| C2 | Name-dropping without context | media list / follower count to prove importance |
| C3 | -ing as fake depth | highlighting, underscoring, symbolizing, fostering, showcasing |
| C4 | Sales tone | vibrant, nestled, breathtaking, must-visit, rich heritage |
| C5 | Vague sources | experts argue, industry reports, observers note – no named source |
| C6 | Stock challenges / outlook | Despite its… faces challenges… continues to thrive |
| C7 | Link without a relation (live, Oct 2026) | associated with, in connection with, «связан с» / «в связи с» when who-does-what is missing. Do not ban the words |
| C8 | Source disclaimer instead of a short gap (live, Oct 2026) | While specific details are limited…; based on available information; should be treated as X rather than Y; does not by itself establish…; then a guess («скорее всего», «likely») |

## Language and grammar

| # | Look for | Example markers |
| --- | --- | --- |
| L1 | Stock AI lexicon (in clusters) | Live mid-2026: challenge, clearer, dependable, echoed, foster, leverage, matters, multifaceted, practical, prioritize, quietly, steady, universally. Older cluster (delve, tapestry, pivotal, underscore) is historical. One word is not a hit |
| L2 | Avoiding is/are | serves as, boasts, features instead of plain «is / has». Russian «является» / «представляет собой» / «обеспечивает» are not a ban |
| L3 | Not X but Y | not only… but…, it's not X it's Y, Y rather than X (live), clipped negation («…, no guessing») |
| L4 | Rule of three | three parallel items where one or two suffice |
| L5 | Synonym cycle / same openings | Historical as a detector. One entity, one name stays a readability rule |
| L6 | False from X to Y | «from A to B» without a real range |
| L7 | Passive without subject | see SKILL §5 contract – separate from «reader in the room» |

## Style and chatbot artifacts

| # | Look for | Example markers |
| --- | --- | --- |
| S1 | Excess bold | **word:** on every list item |
| S2 | Title Case headings | Every Word Capitalized |
| S3 | Emoji in body | decorative rockets / checkmarks |
| S4 | Chatbot tail | I hope this helps, let me know, Would you like… |
| S5 | Knowledge-cutoff disclaimer | Historical (2022–2023): as of my last training. A guess after «not documented» is C8, still live |
| S6 | Agreeable opener | Great question!, You're absolutely right! |
| S7 | Layered filler / hedging | in order to, due to the fact that, could potentially possibly |
| S8 | Generic positive ending | bright future, exciting times ahead instead of last fact |
| S9 | «Deeper truth» | at its core, the real question is, what really matters |
| S10 | Announcement | Let's dive in, Here's what you need to know |
| S11 | Heading = first sentence | H2 then one-line restate of H2 |
| S12 | Fake alternative | One might be tempted to… but… – option nobody considered |
| S13 | Chat paste leftover | `contentReference[oaicite:…]`, `utm_source=chatgpt.com`, `utm_source=openai`, `referrer=grok.com`. From the essay’s markup and citation sections |

## False positives (do not flag alone)

- one em/en dash, one *however*, one short emphasis sentence;
- academic diction without stock-word clusters;
- quotes, titles, UI strings, frontmatter, code;
- en dash «–» per project typography in formal reports – **not** an error.

**Strong signal:** several patterns from different groups in one paragraph or in close succession.
