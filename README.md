
# agent-skills

Personal portable agent skills, shared with the community. Includes a curated `skills-lock.json` for third-party skills I use alongside the owned set.

## Install

Reproduce the full environment in two steps.

### a) Owned skills (global)

```bash
npx skills add Jlosev/agent-skills -g -y
```

### b) Community skills (pinned in `skills-lock.json`)

`npx skills experimental_install` restores every entry under `skills` from a local `skills-lock.json`, but only into **project** `.agents/skills/` (no `-g`). Step **a** is global, so use this **global** sequence to match the lock on a new machine:

```bash
npx skills add kepano/obsidian-skills -g -y \
  -s defuddle json-canvas obsidian-bases obsidian-cli obsidian-markdown
npx skills add obra/superpowers -g -y -s using-superpowers
npx skills add vercel-labs/skills -g -y -s find-skills
npx skills add LpcPaul/tool-scout-skill -g -y -s tool-scout --full-depth
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && cd ~/.claude/skills/gstack && ./setup
npx skills update -g
```

**Project-scoped alternative** (one lock command for `skills` only – clone first, then run inside the repo):

```bash
git clone https://github.com/Jlosev/agent-skills.git
cd agent-skills
npx skills experimental_install
```

Then run the **gstack** line from step **b** above (`toolkits` in the lock – not handled by `experimental_install`).

Optional – local clone for developing owned skills:

```bash
git clone git@github.com:Jlosev/agent-skills.git
npx skills add ./agent-skills -g -y
```

Community skills are not vendored in `skills/`. Sources and install commands live in `skills-lock.json`.

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
- `garrytan/gstack` – toolkit under `toolkits` (clone + `./setup`; full suite, not a single `npx skills add`)

Placeholder `computedHash` values are rewritten the first time `npx skills add` runs.

## LICENSE

MIT – see [LICENSE](LICENSE).
