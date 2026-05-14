---
name: "api-route-debugger"
description: "Use when you need to inspect authenticated Spira API routes, validate request and response contracts, and document gaps without taking unsafe actions."
---

# API Route Debugger

Use this skill to inspect route behavior, compare request and response contracts with expectations, and debug API issues safely.

## Workflow

1. Identify the route path, method, auth expectations, and likely caller.
2. Inspect validation, schema, and downstream dependencies before probing.
3. Prefer read-only or lowest-impact reproduction paths first.
4. Compare the intended contract with actual behavior.
5. Summarize confirmed behavior, failure modes, and safe next steps.

## Debugging Focus

- auth or session assumptions
- required params and validation shape
- route side effects
- response schema drift
- business-logic mismatches
- downstream dependency failures

## Guardrails

- Confirm before high-impact writes, deletes, billing, or publishing actions.
- Do not assume current session state or permissions.
- Prefer a safer reproduction path when a route can mutate state.
- Record whether the issue is auth, validation, contract, business logic, or external dependency related.

## References

- `references/debug-checklist.md`
