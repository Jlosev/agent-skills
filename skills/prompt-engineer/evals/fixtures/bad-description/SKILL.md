---
name: bad-description-fixture
description: >
  Orchestrates end-to-end skill development workflow including community research phase
  via avito ai skills search CLI and skills-hub MCP fallback with automatic retry on VPN
  failures, then generates SKILL.md from internal template references, runs prompt-engineer
  lint pass, delegates eval creation to skill-creator subagent with Task tool, optimizes
  description through iterative benchmark loops, validates evals.json minimum three cases,
  publishes via avito-skill-publisher create-pr.sh or update-pr.sh with YACC-compliant
  commit messages and Avito email enforcement, handles PR review triage through
  paas_bitbucket_get_pr_comments without auto-posting to Mattermost or Confluence.
metadata:
  scope: public
  author: fixture
  version: "0.0.1"
allowed-tools: Read Write StrReplace Shell Grep Glob SemanticSearch Task CallMcpTool WebSearch WebFetch Delete
---

# Bad Description Fixture

## Scope

In: lint SKILL.md against quality-guide  
Out: auto-apply fixes without user confirmation  
Fallback: report-only mode

## Gotchas

- Description intentionally violates trigger-phrase rules for eval purposes
- allowed-tools list is bloated for lint detection

## Output Requirements

Structured report with Critical/Major/Minor sections and letter grade A–D.
