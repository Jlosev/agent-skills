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
npx skills add incubyte/ai-plugins -g -y -s product-discovery
npx skills add derrickgong87/product-idea-excavator -g -y
npx skills add mattpocock/skills -g -y -s grill-me
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

Catalog: [skills.sh/jlosev/agent-skills](https://skills.sh/jlosev/agent-skills). Listing appears after someone runs `npx skills add Jlosev/agent-skills`.

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Any text a person will read. Cut slop, keep facts, edit the file in place and report |
| `critic` | Manual adversarial review via an isolated Opus 5.5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | Find an existing tool before building: own knowledge base first, then GitHub, npm, Homebrew, skills, MCP, SaaS; shortlist, or Buy / Build / Hybrid / Pilot / Defer when something is at stake |
| `prompt-engineer` | Lint/review agent instruction files (SKILL.md, agent, CLAUDE.md, protocol); not scaffold or chat-prompt |
| `local-llm` | Fail-closed structured complete on a local LM Studio model (Shell, not Task) |
| `herdr-update` | Herdr update review: patch notes since the last review vs your mod clones, own mods, keys and settings; merge clones, swap custom code for shipped features, recommend what fits how you work |
| `pipeline` | Orchestrate preflight → brainstorm → plan → review → SDD → verify gate → rebase/finish; on-disk state, resume, Stop hook keeps the run going |

## LICENSE

MIT – see [LICENSE](LICENSE).
