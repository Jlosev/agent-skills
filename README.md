---
created: 2026-09-04
updated: 2026-09-04
---

# agent-skills

Personal portable agent skills.

## Install

**My skills**

```bash
npx skills add Jlosev/agent-skills -g -y
```

**Community I use**

```bash
npx skills add kepano/obsidian-skills -g -y
npx skills add obra/superpowers -g -y
npx skills add vercel-labs/skills -g -y -s find-skills
npx skills add LpcPaul/tool-scout-skill -g -y
npx skills add mattpocock/skills -g -y -s grill-me
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Outbound-doc voice pass (tone, density, dedup) |
| `critic` | Manual adversarial review via an isolated Opus 5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | JTBD-first Buy / Build / Hybrid / Defer |
| `prompt-engineer` | Lint/review agent instruction files (SKILL.md, agent, CLAUDE.md, protocol); not scaffold or chat-prompt |

## LICENSE

MIT – see [LICENSE](LICENSE).
