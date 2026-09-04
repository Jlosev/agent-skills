# agent-skills

Personal portable agent skills, shared with the community. Includes a curated `skills-lock.json` for third-party skills I use alongside the owned set.

## Install

```bash
npx skills add Jlosev/agent-skills -g -y
npx skills update
```

Optional – local clone for development:

```bash
git clone git@github.com:Jlosev/agent-skills.git
npx skills add ./agent-skills -g -y
```

Community skills are not vendored here. Restore them from `skills-lock.json`, or add sources manually: `npx skills add <owner/repo> -s <name>`.

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Outbound-doc voice pass (tone, density, dedup) |
| `critic` | Manual adversarial review via an isolated Opus 5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | JTBD-first Buy / Build / Hybrid / Defer |
| `prompt-engineer` | Lint/review agent instruction files (SKILL.md, agent, CLAUDE.md, protocol); not scaffold or chat-prompt |

## Community lock

Pinned in `skills-lock.json`:

- `kepano/obsidian-skills` – defuddle, obsidian-markdown, obsidian-bases, obsidian-cli, json-canvas
- `obra/superpowers` – using-superpowers
- `vercel-labs/skills` – find-skills
- `LpcPaul/tool-scout-skill` – tool-scout (community scan for tool-market-scout)

Placeholder `computedHash` values are rewritten the first time `npx skills add` runs.

## License

MIT – see [LICENSE](LICENSE).
