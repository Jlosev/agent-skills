---
name: missing-examples-fixture
description: >
  Используй когда нужно проверить Valkey в devenv. Триггерные фразы valkey debug, cluster info.
  Не используй для production инцидентов.
metadata:
  scope: public
  author: fixture
  version: "0.0.1"
---

# Missing Examples Fixture

Сначала вызови /skill-creator для контекста, затем выполни диагностику.
В Claude Code используй встроенный терминал.

## Алгоритм

1. Подключись к Valkey.
2. Выполни CLUSTER INFO.
3. Верни результат пользователю.

## Hard Stop Rules

- Не трогай production

## Definition of Done

- CLUSTER INFO получен

## Scope

In: devenv Valkey
Out: production
