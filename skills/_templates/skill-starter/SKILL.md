---
name: "skill-name"
description: "Use when a task matches this Spira workflow and needs concise, HTTP-aware operational guidance."
---

# Skill Display Name

Use this skill when the task clearly matches this workflow.

## Inputs

- user goal
- relevant HTTP capabilities
- required account, auth, or workspace context
- required environment variables such as base URL or auth mode

## Workflow

1. Confirm the user goal, desired output, and any constraints.
2. Identify the minimum HTTP capabilities or system context needed.
3. Prefer read-first exploration before write actions.
4. Keep the final answer grounded in confirmed evidence.
5. Move long route details or payload examples into `references/`.

## Guardrails

- Distinguish confirmed behavior from inference.
- Do not imply writes, billing, scheduling, or publishing have happened unless they actually have.
- Ask for confirmation before high-impact operations.
- Keep the skill self-contained.
- Call out required auth or environment assumptions explicitly.

## Output

- what was checked
- what is supported
- what is blocked or unknown
- recommended next step

## References

- `references/` for route lists, payload examples, and domain-specific details
