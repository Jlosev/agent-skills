---
name: missing-scope-fixture
description: >
  Этот скилл orchestrates multi-step workflow через MCP hub и internal registry lookup
  для automated skill generation pipeline. Please make sure to follow all steps carefully.
metadata:
  scope: public
  author: fixture
  version: "0.0.1"
---

# Missing Scope Fixture

Please read the following instructions and make sure you understand them before proceeding.
Let's think step by step about what the user wants.

When invoked, you MUST search the vault, call MCP tools, and NEVER skip the research phase.
Don't modify files without explicit permission. NEVER commit secrets.

Run community research, then generate SKILL.md from template, then validate with prompt-engineer.
If something fails, retry until success.
