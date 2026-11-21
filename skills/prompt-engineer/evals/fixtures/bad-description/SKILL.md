---
name: bad-description-fixture
description: >
  Orchestrates end-to-end skill development workflow including community research phase
  via a fictional catalog CLI and a fallback connector with automatic retry on network
  failures, then generates SKILL.md from internal template references, runs prompt-engineer
  lint pass, delegates eval creation to skill-creator subagent with Task tool, optimizes
  description through iterative benchmark loops, validates evals.json minimum three cases,
  publishes via example-skill-publisher with a branch naming policy and a reviewer
  checklist, then sorts review comments from a test repository without sending
  messages to any external service.
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
