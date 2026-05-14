# API Debug Checklist

## Inspect First

- route path and method
- auth guard or session dependency
- input schema or parser
- downstream service calls
- write side effects
- environment assumptions such as base URL, auth mode, timeout, and cookie or bearer credentials

## Safe Validation Order

1. Read route code and caller code.
2. Check auth and validation assumptions.
3. Reproduce with the lowest-impact request possible.
4. Compare actual response shape with intended contract.
5. Document confirmed gaps and suggested fixes.

## Classification

- Auth issue
- Validation issue
- Contract mismatch
- Business logic issue
- External dependency issue
