# Scoring Rubric

Weighted 1–5 per dimension. **Evidence обязателен** — URL или цитата. «Хорошие отзывы» без ссылки = не score.

## Dimensions

| Dimension | Weight | Score 1 | Score 3 | Score 5 |
|-----------|--------|---------|---------|---------|
| JTBD fit | 30% | <30% must jobs | core jobs, edge gaps | all must + most nice |
| License / data sovereignty | 20% | proprietary lock-in, no export | export ok, some lock-in | OSS or full data ownership |
| Project / vendor health | 15% | stale >12mo, 1 maintainer | active, known issues | active community, responsive |
| TCO 3yr | 15% | >$500/yr or hidden costs | $50–500/yr transparent | free OSS or <$50/yr |
| Platform / integration fit | 10% | wrong OS, no API | works with friction | native on target stack |
| Build cost (inverse) | 10% | build <2 weeks | 1–3 months | >3 months |

**Weighted total** = Σ(score × weight). Max 5.0.

## OSS health (не stars)

Проверь для каждого OSS-кандидата:

- [ ] Last commit < 6 months (или tagged release)
- [ ] ≥2 contributors last year
- [ ] Issues answered (median response, sample 5 issues)
- [ ] License compatible (MIT/Apache vs AGPL implications)
- [ ] Docs: install + one real workflow described

Stars alone — **не evidence** для Project health.

## Paid SaaS

Evidence sources: pricing page, ToS/privacy, export/API docs, refund/trial terms.

## Build yourself row

Всегда добавь строку **Build (custom)**:

- Estimate: Whisper/local STT + overlay script / Keyboard Maestro / custom app
- Build cost score по таблице
- Когда Build выигрывает: strict privacy, niche workflow, все paid fail must jobs

## Verdict thresholds

| Weighted | Data sovereignty ≥3 | Verdict |
|----------|---------------------|---------|
| ≥3.5 | yes | **Buy** (или Adopt OSS) |
| ≥3.5 | no | **Hybrid** (OSS core + paid layer) или **Build** |
| 2.5–3.5 | any | **Pilot** top-2, then re-score |
| <2.5 | any | **Build** or **Defer** (explore more jobs) |

## Scoring table template

```markdown
| Candidate | JTBD | License | Health | TCO | Platform | Build↓ | Weighted | Evidence links |
|-----------|------|---------|--------|-----|----------|--------|----------|----------------|
| ... | 4 | 5 | 3 | 4 | 5 | — | 4.1 | [pricing](url), [repo](url) |
| Build custom | 5 | 5 | — | 4 | 4 | 2 | 4.3 | estimate: ... |
```
