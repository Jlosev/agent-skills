---
created: 2026-09-03
updated: 2026-09-03
---

# agent-skills

Personal portable agent skills + a curated community lockfile.

Private while under review. Make public only after you re-read the share checklist below.

Repo: https://github.com/Jlosev/agent-skills

## Install

```bash
git clone git@github.com:Jlosev/agent-skills.git ~/src/agent-skills
cd ~/src/agent-skills
chmod +x install.sh
./install.sh --user
```

- Owned skills are **copied** into `~/.agents/skills` (`agent-retro` → `~/.cursor/skills`).
- Community skills come from `skills-lock.json` via `npx skills add … -g`. They are not vendored in this repo.
- `install.sh` **skips** a destination that is already a symlink (will not clobber an existing vault link).

Update later:

```bash
git pull && ./install.sh --user
```

Community-only restore from another machine (same lock):

```bash
npx skills experimental_install   # project scope, run from this repo
# or
./install.sh --user               # global add from the lock
```

`gstack` is not in the lock. If you want it: `git clone https://github.com/garrytan/gstack.git ~/gstack`.

## Owned skills

| Skill | What it does |
| --- | --- |
| `human-doc-voice` | Outbound-doc voice pass (tone, density, dedup) |
| `critic` | Manual adversarial review via an isolated Opus 5 subagent |
| `canvas-to-html` | Export a Cursor Canvas to static HTML |
| `tool-market-scout` | JTBD-first Buy / Build / Hybrid / Defer |
| `prompt-engineer` | Lint SKILL.md / agent / CLAUDE.md / protocol |
| `agent-retro` | Session-efficiency retro from gryph logs |

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
- Generic product words (Canvas, Obsidian, Gryph, Confluence-the-product as an anti-trigger)

`agent-retro` needs [gryph](https://github.com) on the machine and writes under `~/Library/Application Support/gryph/`. That is local telemetry, not something this repo uploads.

If a scan still finds a company or personal path, do not flip the repo to public – open an issue and strip first.
