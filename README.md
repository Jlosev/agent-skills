---
---
created: 2026-09-15
updated: 2026-09-28
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
npx skills add incubyte/ai-plugins -g -y -s product-discovery
npx skills add derrickgong87/product-idea-excavator -g -y
npx skills add mattpocock/skills -g -y -s grill-me
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

Catalog: [skills.sh/jlosev/agent-skills](https://skills.sh/jlosev/agent-skills). Listing appears after someone runs `npx skills add Jlosev/agent-skills`.

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Any text a person will read. Cut slop, keep facts, apply immediately |
| `critic` | Manual adversarial review via an isolated Opus 5.5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | JTBD-first Buy / Build / Hybrid / Defer |
| `prompt-engineer` | Lint/review agent instruction files (SKILL.md, agent, CLAUDE.md, protocol); not scaffold or chat-prompt |
| `local-llm` | Fail-closed structured complete on a local LM Studio model (Shell, not Task) |
| `pipeline` | Orchestrate brainstorm → plan → review → SDD with on-disk state and resume |

## LICENSE

MIT – see [LICENSE](LICENSE).
