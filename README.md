---
created: 2026-09-03
updated: 2026-09-03
---

# agent-skills

Personal portable agent skills + a curated community lockfile.

Private while under review. Make public only after you re-read the share checklist below.

Repo: https://github.com/Jlosev/agent-skills

## Install

No custom installer. Use [`npx skills`](https://github.com/vercel-labs/skills) or ask an agent to run the same commands.

After the repo is public:

```bash
npx skills add Jlosev/agent-skills -g -y
npx skills update
```

While it is private (GitHub access required):

```bash
git clone git@github.com:Jlosev/agent-skills.git
npx skills add ./agent-skills -g -y
```

Community skills are not vendored. Restore from `skills-lock.json` (project scope) or add the sources below with `npx skills add <owner/repo> -s <name>`.

`gstack` is not in the lock. If you want it: `git clone https://github.com/garrytan/gstack.git ~/gstack`.

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Outbound-doc voice pass (tone, density, dedup) |
| `critic` | Manual adversarial review via an isolated Opus 5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | JTBD-first Buy / Build / Hybrid / Defer |
| `prompt-engineer` | Lint SKILL.md / agent / CLAUDE.md / protocol |

## Community lock

GitHub-only entries, no company sources:

- `kepano/obsidian-skills` – defuddle, obsidian-markdown, obsidian-bases, obsidian-cli, json-canvas
- `obra/superpowers` – using-superpowers
- `eyadsibai/ltk` – agent-browser
- `vercel-labs/skills` – find-skills (the public CLI finder, not a company hub)

Placeholder `computedHash` values are rewritten the first time `npx skills add` runs.

## Share checklist (read before making the repo public)

Stripped on purpose:

- Company vault paths, internal wikis, confirm tokens, hub URLs
- Company logins (author is the GitHub handle)
- Eval fixtures and local run workspaces
- Voice profiles, calendar credentials, lockfiles from a company catalog
- `my-voice`, digest, Confluence/Jira publishers, OKR/TDR, calendar

Still in the repo (intentional, not secrets):

- Copyright name on the MIT license
- GitHub handle `Jlosev` in skill `metadata.author`
- Attribution comments for upstream (`LpcPaul/tool-scout-skill`, Dreamineering)
- Generic product words (Canvas, Obsidian, Confluence-the-product as an anti-trigger)

If a scan still finds a company or personal path, do not flip the repo to public – open an issue and strip first.
