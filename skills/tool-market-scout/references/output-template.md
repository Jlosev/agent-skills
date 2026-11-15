# Output Template

Use only when the project has no format of its own for tool notes and the user asked for a file. A project registry or comparison template (named in its `AGENTS.md`) wins.

```markdown
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tool-research]
---

# {job in a few words}

## Brief
...

## Candidates
| # | Name | Type | License / price | Covers jobs | URL |
...

## Scoring
| Candidate | Weighted | Key evidence |
...

## Verdict
- **Recommendation:** Buy | Adopt OSS | Hybrid | Build | Pilot | Defer
- **Top pick:** ...
- **Next step:** ...

## Sources
- [Name](url) – accessed YYYY-MM-DD
```

File name – kebab-case from the job statement, not from a brand. Path – the one the user names.
