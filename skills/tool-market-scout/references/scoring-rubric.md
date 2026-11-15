# Scoring Rubric

Weighted 1–5 per dimension. **Evidence обязателен** — URL или цитата. «Хорошие отзывы» без ссылки = не score. Оценка без источника помечается «оценка, без источника» и не выше 3.

## Dimensions

| Dimension | Weight | Score 1 | Score 3 | Score 5 |
|-----------|--------|---------|---------|---------|
| JTBD fit | 30% | <30% must jobs | core jobs, edge gaps | all must + most nice |
| License / data sovereignty | 20% | proprietary lock-in, no export | export ok, some lock-in | OSS or full data ownership |
| Project / vendor health | 15% | stale >12mo, 1 maintainer | active, known issues | active community, responsive |
| TCO 3yr | 15% | >$500/yr or hidden costs | $50–500/yr transparent | free OSS or <$50/yr |
| Platform / integration fit | 10% | wrong OS, no API | works with friction | native on target stack |
| Build effort avoided | 10% | own build <2 weeks | 1–3 months | >3 months |

**Build effort avoided** – сколько стоило бы сделать то же самому. Одно значение для всех готовых кандидатов: чем дороже своя сборка, тем выше балл у готового. У строки Build здесь «—».

**Weighted total** = Σ(score × weight) / Σ(weight применённых измерений). Неприменимое измерение – «—», его вес в делитель не входит. Max 5.0.

## OSS health (не stars)

Для каждого OSS-кандидата, тем, что доступно:

- [ ] Release или commit в окне V0 (`gh api repos/<o>/<r>` – `pushed_at`; `gh api repos/<o>/<r>/releases/latest`)
- [ ] ≥2 contributors (`gh api "repos/<o>/<r>/contributors?per_page=3"`)
- [ ] Issues получают ответ (`gh issue list -R <o>/<r> --state closed --limit 5`)
- [ ] License compatible (MIT/Apache vs AGPL implications)
- [ ] Docs: install + one real workflow described

Пункт не проверен – так и напиши; Health тогда не выше 3. Stars alone — **не evidence**.

## Paid SaaS

Evidence sources: pricing page, ToS/privacy, export/API docs, refund/trial terms. Data sovereignty без ToS или privacy-страницы – «оценка, без источника».

## Build yourself row

Всегда добавь строку **Build (custom)**:

- Estimate: что именно строим (скрипт, обвязка вокруг OSS-ядра, небольшое приложение) и сколько это займёт
- Когда Build выигрывает: strict privacy, niche workflow, все кандидаты проваливают must jobs

## Verdict thresholds

| Weighted | Data sovereignty ≥3 | Verdict |
|----------|---------------------|---------|
| ≥3.5 | yes | **Buy** (платное) или **Adopt OSS** (бесплатный OSS) |
| ≥3.5 | no | **Hybrid**, если OSS-ядро закрывает must jobs, а платный слой – остальное; иначе **Build** |
| 2.5–3.5 | any | **Pilot** top-2, then re-score |
| <2.5 | any | **Build** or **Defer** (explore more jobs) |

## Scoring table template

```markdown
| Candidate | JTBD | License | Health | TCO | Platform | Build avoided | Weighted | Evidence links |
|-----------|------|---------|--------|-----|----------|---------------|----------|----------------|
| ... | 4 | 5 | 3 | 4 | 5 | 4 | 4.2 | [pricing](url), [repo](url) |
| Build custom | 5 | 5 | — | 2 | 4 | — | 3.9 | estimate: ... |
```
